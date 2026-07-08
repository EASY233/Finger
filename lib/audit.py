#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""指纹规则质量审计 — 扫描后自动检测可疑规则"""

import os
import json
import re
from collections import Counter, defaultdict

from lib.resultio import write_csv_rows
from lib.rule_heuristics import classify_rule, normalize_cms_key, prefer_display_name


class RuleAudit:
    """分析扫描结果，标记可能存在误报的规则"""

    VERSION_REGEX_WARNING_CMS = {
        "prometheus",
        "apache-airflow",
        "apache-nifi",
        "minio",
        "rancher",
        "keycloak",
        "gitlab",
        "gitlabci",
        "nexus repository manager",
        "harbor",
        "portainer",
        "casdoor",
        "argocd",
        "gitea",
        "opensearch",
        "opensearch dashboards",
        "nginx proxy manager",
        "uptime-kuma",
        "alertmanager",
        "consul-hashicorp",
        "alibaba-druid",
    }

    def __init__(self, library_dir, xlsx_path=None):
        self.library_dir = library_dir
        self.finger_path = os.path.join(library_dir, 'finger.json')
        self.xlsx_path = xlsx_path
        with open(self.finger_path, 'r', encoding='utf-8') as f:
            self.rules = json.load(f).get('fingerprint', [])

    def run(self, scan_results):
        """scan_results: list[dict], 每个dict含 url/cms/Server/status/title"""
        findings = []

        findings.extend(self._static_rule_findings())
        findings.extend(self._version_rule_findings())

        if not scan_results:
            findings.sort(key=lambda x: (
                0 if x['severity'] == 'HIGH' else 1,
                -x['hits']
            ))
            return findings

        # ── 维度1: 每种指纹的命中统计 ──
        fp_stats = defaultdict(lambda: {
            'total': 0, 'servers': Counter(), 'status_codes': Counter(),
            'titles': Counter(), 'urls': []
        })

        total_fingerprinted = 0
        for row in scan_results:
            cms_str = str(row.get('cms', ''))
            if not cms_str or cms_str in ('None', '-', ''):
                continue
            total_fingerprinted += 1
            server = str(row.get('Server', '')).strip()
            status = str(row.get('status', '')).strip()
            title = str(row.get('title', '')).strip()
            url = str(row.get('url', ''))

            for fp in cms_str.split(','):
                fp = fp.strip()
                if fp:
                    fp_stats[fp]['total'] += 1
                    if server and server != 'None':
                        fp_stats[fp]['servers'][server[:60]] += 1
                    fp_stats[fp]['status_codes'][status] += 1
                    if len(fp_stats[fp]['urls']) < 3:
                        fp_stats[fp]['urls'].append(url)

        # ── 维度2: Server 多样性 ──
        for fp, stats in fp_stats.items():
            unique_servers = len(stats['servers'])
            if unique_servers >= 5:
                top_servers = stats['servers'].most_common(5)
                findings.append({
                    'fingerprint': fp,
                    'hits': stats['total'],
                    'issue': 'Server多样性过高',
                    'detail': f'{unique_servers}种不同Server: {", ".join(s[:40] for s, _ in top_servers)}',
                    'severity': 'HIGH' if unique_servers >= 8 else 'MEDIUM',
                    'suggestion': '该指纹可能匹配了过于通用的特征，建议检查规则关键词',
                    'examples': stats['urls'][:3],
                })

        # ── 维度3: 404 命中率 ──
        for fp, stats in fp_stats.items():
            if stats['total'] >= 5:
                status_404 = stats['status_codes'].get('404', 0)
                ratio_404 = status_404 / stats['total']
                if ratio_404 >= 0.35:
                    findings.append({
                        'fingerprint': fp,
                        'hits': stats['total'],
                        'issue': f'404命中率过高 ({ratio_404:.0%})',
                        'detail': f'{status_404}/{stats["total"]} 次匹配在404页面上',
                        'severity': 'HIGH' if ratio_404 >= 0.5 else 'MEDIUM',
                        'suggestion': '404页面不应匹配产品指纹，建议检查关键词是否过于泛化',
                        'examples': stats['urls'][:3],
                    })

        # ── 维度4: 命中率异常 (单个指纹占比过高) ──
        if total_fingerprinted > 0:
            for fp, stats in fp_stats.items():
                ratio = stats['total'] / total_fingerprinted
                if ratio >= 0.25 and stats['total'] >= 10:
                    findings.append({
                        'fingerprint': fp,
                        'hits': stats['total'],
                        'issue': f'命中率异常 ({ratio:.0%}的已识别URL)',
                        'detail': f'占总识别URL的 {ratio:.1%}，可能存在大面积误报',
                        'severity': 'HIGH' if ratio >= 0.5 else 'MEDIUM',
                        'suggestion': '参考VMware-ESX案例，检查规则是否包含通用HTML标签或泛化关键词',
                        'examples': stats['urls'][:3],
                    })

        # ── 维度5: 规则关键词质量 ──
        # 仅标记真正的通用英文短词，不标记产品专有缩写（如 OKI=打印机, QTS=威联通OS）
        COMMON_WORDS = {
            'the', 'and', 'for', 'not', 'but', 'all', 'can', 'had', 'her',
            'was', 'one', 'our', 'out', 'has', 'are', 'use', 'any', 'see',
            'new', 'get', 'who', 'how', 'its', 'may', 'etc', 'you', 'did',
            'his', 'him', 'she', 'two', 'too', 'run', 'set', 'put', 'add',
            'end', 'let', 'try', 'ask', 'big', 'few', 'lot', 'off', 'old',
            'own', 'pay', 'win', 'yes', 'yet', 'way', 'day', 'man', 'men',
            'now', 'top', 'hot', 'bad', 'boy', 'buy', 'car', 'cat', 'cut',
            'dog', 'dry', 'eat', 'far', 'fit', 'fix', 'fly', 'fun', 'god',
            'hit', 'job', 'key', 'kid', 'law', 'lie', 'low', 'map', 'mix',
            'net', 'oil', 'pop', 'red', 'row', 'sad', 'sit', 'six', 'son',
            'sum', 'sun', 'tax', 'ten', 'tip', 'toy', 'war', 'wet', 'win',
        }
        for r in self.rules:
            for kw in r.get('keyword', []):
                kw_lower = kw.lower()
                # ≤3字符纯英文 且 是常见通用单词（非产品缩写）
                if (len(kw) <= 3 and kw.isascii() and kw.isalpha()
                        and kw_lower in COMMON_WORDS):
                    findings.append({
                        'fingerprint': r['cms'],
                        'hits': fp_stats.get(r['cms'], {}).get('total', 0),
                        'issue': f'高危通用短词: "{kw}"',
                        'detail': f'location={r.get("location")}, logic={r.get("logic","and")}, 该词是常见英文单词，几乎每页都有',
                        'severity': 'HIGH',
                        'suggestion': f'建议删除 "{kw}" 或改为更具体的复合关键词',
                        'examples': [],
                    })
                    break  # 每条规则只报告一次

        # 按严重程度排序
        findings.sort(key=lambda x: (
            0 if x['severity'] == 'HIGH' else 1,
            -x['hits']
        ))

        return findings

    def _static_rule_findings(self):
        findings = []
        cms_name_groups = defaultdict(set)
        cms_rule_stats = defaultdict(lambda: {
            "path_only_url": 0,
            "risky_single_header": 0,
            "total": 0,
        })

        for rule in self.rules:
            cms = str(rule.get('cms', '')).strip()
            if not cms:
                continue
            key = normalize_cms_key(cms)
            cms_name_groups[key].add(cms)
            flags = classify_rule(rule)
            cms_rule_stats[key]["total"] += 1
            if 'path_only_url' in flags:
                cms_rule_stats[key]["path_only_url"] += 1
            if 'risky_single_header' in flags:
                cms_rule_stats[key]["risky_single_header"] += 1

        for key, names in cms_name_groups.items():
            if len(names) < 2:
                continue
            canonical_names = {prefer_display_name([name]) for name in names}
            if len(canonical_names) == 1:
                continue
            findings.append({
                'fingerprint': sorted(names)[0],
                'hits': len(names),
                'issue': '同产品名称碎片化',
                'detail': ' / '.join(sorted(names)),
                'severity': 'MEDIUM',
                'suggestion': '建议统一 CMS 展示名，避免同一产品在结果中重复出现',
                'examples': [],
            })

        for key, stats in cms_rule_stats.items():
            if stats["path_only_url"] >= 2:
                findings.append({
                    'fingerprint': key,
                    'hits': stats["path_only_url"],
                    'issue': 'URL 路径型规则偏多',
                    'detail': f'{stats["path_only_url"]}/{stats["total"]} 条规则仅靠路径识别',
                    'severity': 'HIGH' if stats["path_only_url"] >= 3 else 'MEDIUM',
                    'suggestion': '建议补充 title/body/header 佐证，避免仅靠路径命中',
                    'examples': [],
                })
            if stats["risky_single_header"] >= 2:
                findings.append({
                    'fingerprint': key,
                    'hits': stats["risky_single_header"],
                    'issue': '高风险单头部规则偏多',
                    'detail': f'{stats["risky_single_header"]}/{stats["total"]} 条规则仅靠通用响应头或 Cookie 识别',
                    'severity': 'HIGH' if stats["risky_single_header"] >= 3 else 'MEDIUM',
                    'suggestion': '建议补充页面正文、标题或 favicon 佐证',
                    'examples': [],
                })

        return findings

    def _version_rule_findings(self):
        findings = []
        for rule in self.rules:
            version_regex = str(rule.get("version_regex", "")).strip()
            if not version_regex:
                continue
            cms = str(rule.get("cms", "")).strip()
            if not cms:
                continue

            location = str(rule.get("version_location", rule.get("location", "body"))).strip() or "body"
            if location not in {"body", "title", "header", "url"}:
                location = "body"

            keyword_count = len(rule.get("keyword", []))
            logic = rule.get("logic", "and")
            key = normalize_cms_key(cms)
            risk = 0
            detail_bits = []

            if key in self.VERSION_REGEX_WARNING_CMS:
                risk += 1
                detail_bits.append("高价值产品版本规则")

            if location == "title" and keyword_count <= 1:
                risk += 1
                detail_bits.append("版本来源依赖单标题")
            if location == "body" and keyword_count <= 1 and logic == "and":
                risk += 1
                detail_bits.append("版本来源依赖单正文证据")
            if re.search(r'\\d\+|\\d\*\+|\\d\{\d', version_regex):
                detail_bits.append("regex含明显数字模式")

            if risk >= 2:
                findings.append({
                    'fingerprint': cms,
                    'hits': 1,
                    'issue': 'version_regex 可靠性需复核',
                    'detail': f'location={location}, logic={logic}, regex={version_regex}',
                    'severity': 'MEDIUM',
                    'suggestion': '建议用真实页面夹具验证该版本规则；若无稳定版本文本，删除 version_regex',
                    'examples': detail_bits[:3],
                })

        return findings

    def save_csv(self, findings, output_path):
        """保存审计结果为 CSV"""
        rows = [['Severity', 'Fingerprint', 'Hits', 'Issue', 'Detail', 'Suggestion', 'Examples']]
        for item in findings:
            rows.append([
                item["severity"],
                item["fingerprint"],
                item["hits"],
                item["issue"],
                item["detail"],
                item["suggestion"],
                ' | '.join(item.get('examples', [])),
            ])
        write_csv_rows(rows, output_path)

    def print_summary(self, findings):
        """打印审计摘要"""
        high = [f for f in findings if f['severity'] == 'HIGH']
        medium = [f for f in findings if f['severity'] == 'MEDIUM']

        print(f"\n{'='*60}")
        print(f"  规则质量审计报告")
        print(f"{'='*60}")
        print(f"  HIGH: {len(high)} 条  MEDIUM: {len(medium)} 条")
        print()

        if high:
            print("  🔴 HIGH 严重问题:")
            for item in high[:10]:
                print(f"    [{item['fingerprint']}] {item['issue']}")
                print(f"      {item['detail']}")
                print(f"      → {item['suggestion']}")
                if item.get('examples'):
                    print(f"      例: {item['examples'][0]}")
                print()

        if medium:
            print("  🟡 MEDIUM 中等问题:")
            for item in medium[:5]:
                print(f"    [{item['fingerprint']}] {item['issue']}")
                print(f"      {item['detail']}")
                print()
