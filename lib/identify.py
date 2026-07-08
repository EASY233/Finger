#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY233
import os
import re
import json
from config.color import color
from urllib.parse import urlsplit
from config.data import logging
from lib.match_filters import filter_matches
from lib.rule_heuristics import classify_rule, normalize_cms_key, prefer_display_name


class Identify:
    VERSION_FALLBACK_PATTERNS = {
        "Grafana": (
            r'Grafana[^0-9]*([\d]+(?:\.[\d]+)+)',
            r'"version"\s*:\s*"([\d]+(?:\.[\d]+)+)"',
        ),
        "Jenkins": (
            r'Jenkins[^0-9]*([\d]+(?:\.[\d]+)+)',
            r'X-Jenkins[:"]\s*"?([\d]+(?:\.[\d]+)+)',
        ),
        "RabbitMQ": (
            r'RabbitMQ[^0-9]*([\d]+(?:\.[\d]+)+)',
        ),
        "Zabbix": (
            r'Zabbix[^0-9]*([\d]+(?:\.[\d]+)+)',
        ),
    }

    def __init__(self, library_dir):
        self.library_dir = library_dir
        filepath = os.path.join(library_dir, 'finger.json')
        with open(filepath, 'r', encoding='utf-8') as file:
            finger = json.load(file)
        self.obj = finger.get('fingerprint', [])
        # 初始化指纹库
        self._prepare_app()

    def run(self, datas, result_store=None, log_result=True):
        summary = self.match(datas)
        result = {
            "url": datas.get("url", ""),
            "cms": summary["cms"],
            "confidence": summary["confidence"],
            "fingerprints": summary.get("fingerprints", []),
            "version": summary["version"],
            "title": datas.get("title", ""),
            "status": datas.get("status", ""),
            "Server": datas.get("Server", ""),
            "size": datas.get("size", ""),
            "iscdn": datas.get("iscdn", 0),
            "ip": datas.get("ip", ""),
            "address": datas.get("address", ""),
            "isp": datas.get("isp", ""),
            "faviconhash": datas.get("faviconhash", {"ehole": 0, "fofa": 0, "md5": "0"}),
            "error_type": datas.get("error_type", ""),
            "error_detail": datas.get("error_detail", ""),
        }

        if result_store is None:
            return result

        exists = any(
            value.get("url") == result["url"] and value.get("title") == result["title"]
            for value in result_store
        )
        if not exists:
            if summary["cms"]:
                result_store.insert(0, result)
            else:
                result_store.append(result)
            if log_result:
                msg = "{0} {1} {2:5} {4} {3}".format(
                    color.green(result['cms'] or '-'),
                    color.blue(result['Server']),
                    result['title'],
                    color.yellow(result['status']),
                    result["url"],
                )
                logging.success(msg)
        return result

    def match(self, datas):
        """库模式：只做匹配，返回结果 dict，不写全局状态。"""
        matches = self._match_app(datas)
        return self._summarize_matches(matches, datas=datas)

    def match_details(self, datas):
        """返回按 CMS 去重后的详细命中信息，便于回归测试和外部审计。"""
        matches = self._match_app(datas)
        return filter_matches(self._aggregate_matches(matches), datas)

    def _summarize_matches(self, matches, datas=None):
        top = filter_matches(self._aggregate_matches(matches), datas or {})
        cms_list = [m["cms"] for m in top]
        versions = []
        for match in top:
            version = match.get("version")
            if version and version not in versions:
                versions.append(version)
        fingerprints = []
        for match in top:
            fingerprints.append({
                "cms": match["cms"],
                "confidence": match["confidence"],
                "version": match.get("version") or "",
                "evidence_count": match.get("evidence_count", 1),
                "locations": list(match.get("locations", ())),
                "methods": list(match.get("methods", ())),
            })
        return {
            "cms": ','.join(cms_list),
            "confidence": max((m["confidence"] for m in top), default=0),
            "version": ','.join(versions) or "-",
            "fingerprints": fingerprints,
        }

    def _aggregate_matches(self, matches):
        grouped = {}
        for match in sorted(matches, key=lambda x: x["confidence"], reverse=True):
            key = normalize_cms_key(match["cms"])
            grouped.setdefault(key, []).append(match)

        collapsed = []
        for key, items in grouped.items():
            best = dict(items[0])
            versions = []
            methods = set()
            locations = set()
            flags = set()
            for item in items:
                version = item.get("version")
                if version and version not in versions:
                    versions.append(version)
                method = item.get("method")
                location = item.get("location")
                if method:
                    methods.add(method)
                if location:
                    locations.add(location)
                flags.update(item.get("flags", ()))

            confidence = best["confidence"]
            risky_only = bool(flags) and flags <= {"path_only_url", "risky_single_header"}
            if len(locations) >= 2 and not risky_only:
                confidence += 5
            if len(items) >= 2 and 'faviconhash' in methods and len(methods) >= 2:
                confidence += 5
            if len(items) >= 3 and len(locations) >= 2 and not risky_only:
                confidence += 5
            if versions and len(locations) >= 2 and not risky_only:
                confidence += 3

            best["confidence"] = max(10, min(100, confidence))
            best["version"] = ','.join(versions) if versions else None
            best["evidence_count"] = len(items)
            best["locations"] = tuple(sorted(locations))
            best["methods"] = tuple(sorted(methods))
            collapsed.append(best)

        return sorted(collapsed, key=lambda x: x["confidence"], reverse=True)

    def _prepare_app(self):
        aliases = {}
        for line in self.obj:
            if "regula" == line["method"]:
                line["_compiled_keyword_res"] = [
                    self._prepare_pattern(pattern) for pattern in line.get("keyword", [])
                ]
            line["_effective_model_location"] = self._resolve_model_location(line)
            line["_heuristic_flags"] = classify_rule(line)
            # 预编译版本号正则
            vr = line.get("version_regex", "")
            if vr:
                line["_version_re"] = re.compile(vr, re.I)
            # 预编译设备型号正则
            mr = line.get("model_regex", "")
            if mr:
                line["_model_re"] = re.compile(mr, re.I)
            aliases.setdefault(normalize_cms_key(line.get("cms", "")), set()).add(line.get("cms", ""))
        self._cms_aliases = {key: prefer_display_name(values) for key, values in aliases.items()}

    def _prepare_pattern(self, pattern):
        regex, _, rest = pattern.partition('\\;')
        try:
            return re.compile(regex, re.I)
        except re.error:
            return re.compile(r'(?!x)x')

    def _resolve_model_location(self, rule):
        location = rule.get("model_location", rule.get("location", "body"))
        cms = rule.get("cms", "")
        if cms in {"Hikvision-Cameras-and-Surveillance", "Hikvision-Webs", "HP-LaserJet-Printer"} and location == "title":
            return "body"
        return location

    def _get_match_string(self, datas, location, cache=None):
        """将 datas 中的值转为匹配用字符串，对 header 做多格式兼容。

        不同指纹库来源的关键词格式不同：
        - Finger 原生: 关键字匹配 dict 的 str() 结果
        - EHole 系列: 关键字用 HTTP 头格式 "Server: nginx"
        - 部分魔改版: 关键字前带 '(' 前缀 "(Server: nginx"
        - url 匹配: 同时生成完整 URL / 路径+查询 / 纯路径三行，覆盖各种路径关键词
        """
        if cache is not None and location in cache:
            return cache[location]

        data = datas.get(location, "")
        if location == "url":
            url = str(data)
            parsed = urlsplit(url)
            path_qs = parsed.path + ('?' + parsed.query if parsed.query else '')
            # 兼容带/不带尾部斜杠: /actuator 和 /actuator/ 互相匹配
            path = parsed.path.rstrip('/')
            value = '\n'.join([path_qs, parsed.path, path, path + '/'])
            if cache is not None:
                cache[location] = value
            return value
        if location == "header" and hasattr(data, 'items'):
            # 兼容 CaseInsensitiveDict (requests) 和普通 dict
            header_dict = dict(data)
            lines = [str(header_dict)]
            for k, v in header_dict.items():
                lines.append(f"{k}: {v}")
                lines.append(f"{k.lower()}: {v}")
                lines.append(f"({k}: {v}")
            value = '\n'.join(lines)
            if cache is not None:
                cache[location] = value
            return value
        value = str(data)
        if cache is not None:
            cache[location] = value
        return value

    def _match_app(self, datas):
        matches = []
        match_cache = {}
        for line in self.obj:
            method = line['method']
            matched = False
            matched_keywords = []

            # ── faviconhash: 密码学哈希 → 直接 95 分，不走算法 ──
            if method == "faviconhash":
                fav = datas.get("faviconhash", {})
                targets = [str(value) for value in line.get("keyword", [])]
                if isinstance(fav, dict):
                    matched = any(
                        target in {
                            str(fav.get('ehole', '')),
                            str(fav.get('fofa', '')),
                            str(fav.get('md5', '')),
                        }
                        for target in targets
                    )
                else:
                    matched = str(fav) in targets

                if matched:
                    ver_num = self._extract_version(datas, line)
                    canonical_cms = self._canonical_cms(line["cms"])
                    version = f"{canonical_cms} {ver_num}" if ver_num else None
                    model = self._extract_model(datas, line)
                    if model:
                        version = (version + ' ' if version else '') + f"[{model}]"
                    matches.append({
                        "cms": canonical_cms,
                        "confidence": 95,
                        "version": version,
                    })
                    continue

            # ── keyword: 统计命中关键词 → 算法计算置信度 ──
            elif method == "keyword":
                logic = line.get('logic', 'and')
                loc = line.get("location", "body")
                data_str = self._get_match_string(datas, loc, match_cache)
                data_lower = data_str.lower()

                if logic == 'or':
                    # 统计所有命中的关键词（不再用 any() 提前退出）
                    matched_keywords = [k for k in line["keyword"] if str(k).lower() in data_lower]
                    matched = bool(matched_keywords)
                else:  # and
                    matched = all(str(k).lower() in data_lower for k in line["keyword"])
                    if matched:
                        matched_keywords = list(line["keyword"])

            # ── regula: 正则匹配 → 算法计算置信度 ──
            elif method == "regula":
                logic = line.get('logic', 'and')
                loc = line.get("location", "body")
                data_str = self._get_match_string(datas, loc, match_cache)
                patterns = line.get("_compiled_keyword_res", [])
                if patterns:
                    if logic == 'or':
                        matched_keywords = [pattern.pattern for pattern in patterns if pattern.search(data_str)]
                        matched = bool(matched_keywords)
                    else:
                        matched = all(pattern.search(data_str) for pattern in patterns)
                        if matched:
                            matched_keywords = [pattern.pattern for pattern in patterns]

            # ── 统一计算置信度 ──
            if matched:
                confidence = self._compute_confidence(datas, line, matched_keywords)
                ver_num = self._extract_version(datas, line, match_cache)
                canonical_cms = self._canonical_cms(line["cms"])
                version = f"{canonical_cms} {ver_num}" if ver_num else None
                model = self._extract_model(datas, line, match_cache)
                if model:
                    version = (version + ' ' if version else '') + f"[{model}]"
                matches.append({
                    "cms": canonical_cms,
                    "confidence": confidence,
                    "version": version,
                    "method": method,
                    "location": line.get("location", "body"),
                    "flags": tuple(sorted(line.get("_heuristic_flags", ()))),
                })

        return matches

    def _compute_confidence(self, datas, rule, matched_keywords):
        """完全自动化的置信度计算——不依赖规则中预设的 confidence 字段。

        原则: 置信度从匹配过程本身推导，不从事先标注。
         - faviconhash 已在 _match_app 中直接返回 95，不进入此方法
         - keyword 匹配根据 位置/逻辑/命中率/关键词质量 计算
         - regula 匹配取保守值
        """
        method = rule.get('method', 'keyword')
        loc = rule.get('location', 'body')
        logic = rule.get('logic', 'and')
        total_kw = len(rule.get('keyword', []))
        hit_count = len(matched_keywords)

        # ── Step 1: 方法基础分 ──
        if method == 'regula':
            base = 50   # 正则: 特异性取决于正则质量，取保守值
        else:
            base = 55   # keyword: 基线

        # ── Step 2: 位置调整 (title/url 最可靠, header 次之, body 最弱) ──
        if loc == 'title':
            base += 25
        elif loc == 'url':
            base += 25   # URL 路径匹配与 title 同等可靠
        elif loc == 'header':
            base += 10

        # ── Step 3: 逻辑 + 命中率 (AND全命中 > OR高命中率 > OR低命中率) ──
        if logic == 'and':
            if total_kw >= 2:
                base += 15   # 多关键词 AND: 全部命中 → 误报概率极低
            else:
                base += 5    # 单关键词 AND: 等同单点匹配
        else:  # OR
            if total_kw >= 2:
                ratio = hit_count / total_kw
                base += int(ratio * 15)  # 命中1/10≈+1, 5/10≈+7, 10/10=+15
            # 单关键词 OR: 最不可靠, +0

        # ── Step 4: 关键词风险惩罚 ──
        for kw in matched_keywords:
            # ≤3 字符纯英文 → 如 "php" "asp" "body" → 几乎每页都有
            if len(kw) <= 3 and kw.isascii() and kw.isalpha():
                base -= 20
            # 短 HTML 标签 → "<span>" "<div>" 等
            elif kw.startswith('<') and len(kw) < 15:
                base -= 15
            # 短 URL 路径在 body 中 → 是链接而非页面本身 (url location 不惩罚)
            elif kw.startswith('/') and loc == 'body' and len(kw) < 30:
                base -= 10

        # ── Step 5: Server header 交叉校验（仅对配置了 expected_server 的规则生效） ──
        expected = rule.get('expected_server', [])
        if expected:
            server = str(datas.get('Server', '')).lower()
            if not any(e.lower() in server for e in expected):
                base -= 20  # Server 不匹配 → 大概率 FP

        flags = rule.get("_heuristic_flags", frozenset())
        if 'path_only_url' in flags:
            base -= 40
        if 'risky_single_header' in flags:
            base -= 20
        if 'short_title' in flags:
            base -= 10
        if 'supporting_service' in flags:
            base -= 25

        return max(10, min(100, base))

    def _extract_version(self, datas, rule, match_cache=None):
        """从响应中提取版本号"""
        version_re = rule.get("_version_re")
        if version_re:
            loc = rule.get("version_location", rule.get("location", "body"))
            data_str = self._get_match_string(datas, loc, match_cache)
            m = version_re.search(data_str)
            if m:
                for group in m.groups():
                    if group:
                        return group
                return m.group(0)
        return self._fallback_version(datas, rule.get("cms", ""), match_cache)

    def _extract_model(self, datas, rule, match_cache=None):
        """从响应中提取设备型号（硬件指纹）"""
        model_re = rule.get("_model_re")
        if not model_re:
            return None
        loc = rule.get("_effective_model_location", rule.get("model_location", rule.get("location", "body")))
        data_str = self._get_match_string(datas, loc, match_cache)
        m = model_re.search(data_str)
        if not m:
            return None
        model = m.group(0)
        if rule.get("cms") == "HP-LaserJet-Printer":
            extended = re.search(
                r'HP\s+(?:LaserJet|Color LaserJet|OfficeJet|PageWide|DesignJet)\s+(?:MFP\s+|Pro\s+)?[\w\d]+(?:\s+[\w\d-]+)*',
                data_str,
                re.I,
            )
            if extended:
                model = extended.group(0)
        return model

    def _fallback_version(self, datas, cms, match_cache=None):
        patterns = self.VERSION_FALLBACK_PATTERNS.get(cms, ())
        if not patterns:
            return None

        candidates = [
            self._get_match_string(datas, "title", match_cache),
            self._get_match_string(datas, "header", match_cache),
            self._get_match_string(datas, "body", match_cache),
        ]
        for candidate in candidates:
            for pattern in patterns:
                match = re.search(pattern, candidate, re.I)
                if match:
                    return match.group(1)
        return None

    def _canonical_cms(self, cms):
        return self._cms_aliases.get(normalize_cms_key(cms), cms)
