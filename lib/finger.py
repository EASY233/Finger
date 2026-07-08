#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Finger 库接口 — 可被 dirsearch_bypass403 等工具直接 import 使用

用法:
    from lib.finger import Finger
    f = Finger(threads=30)
    results = f.scan(['http://target1.com', 'http://target2.com'])
    # results 是 dict 列表，可直接使用或传入 Output 导出
"""
import os
import random
import base64
import hashlib
import requests
import mmh3
import urllib3
from urllib.parse import urlsplit, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

import re
from config.data import logging
from config import settings
from lib.identify import Identify
from lib.ip_factory import IPFactory
from lib.resultio import save_results
from lib.runtime import create_runtime_config

urllib3.disable_warnings()


class Finger:
    """Finger 指纹识别器 — 库入口"""
    HTTPS_UPGRADE_MARKERS = (
        "the plain http request was sent to https port",
    )
    MAX_CLIENT_REDIRECTS = 2
    BODY_READ_LIMIT = 131072

    def __init__(self, threads=None, config=None):
        self.config = config or create_runtime_config()
        self.threads = threads or self.config.threads
        self.identify = Identify(library_dir=self.config.paths.library_dir)
        self.ip_factory = IPFactory(library_dir=self.config.paths.library_dir)
        self._headers = self._get_headers()

    # ── 公开 API ──────────────────────────

    def scan(self, urls, timeout=None):
        """扫描 URL 列表，返回识别结果列表。

        Args:
            urls: URL 字符串列表
            timeout: HTTP 请求超时（秒），None 则使用 settings.timeout

        Returns:
            list[dict]
        """
        if timeout is None:
            timeout = self.config.timeout
        results = []
        errors = []
        unique_urls = list(dict.fromkeys(urls))
        scheduled_urls = set(unique_urls)

        pool = ThreadPoolExecutor(self.threads)
        try:
            futures = {
                pool.submit(self._scan_one, url, timeout, scheduled_urls=scheduled_urls): url
                for url in unique_urls
            }
            for future in as_completed(futures):
                url = futures[future]
                try:
                    result = future.result()
                    if not result:
                        continue
                    if result.get("error_type"):
                        errors.append(result)
                    else:
                        results.append(result)
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    errors.append(self._error_result(url, "worker_error", str(e)))
        except KeyboardInterrupt:
            pool.shutdown(wait=False, cancel_futures=True)
            logging.error("用户强制中止!")
        finally:
            pool.shutdown(wait=False)

        # 有 CMS 的结果优先排在前面
        results.sort(key=lambda r: (r.get("confidence", 0), r.get("cms") != ""),
                     reverse=True)
        return results + errors

    def scan_and_save(self, urls, output_dir=None, fmt="xlsx", timeout=None):
        """扫描并保存结果到文件。

        Args:
            urls: URL 列表
            output_dir: 输出目录，默认 library 同级的 output/
            fmt: 输出格式 "xlsx" 或 "json"
            timeout: HTTP 请求超时

        Returns:
            (results, filepath): 结果列表和输出文件路径
        """
        results = self.scan(urls, timeout=timeout)

        if output_dir is None:
            output_dir = self.config.paths.output_dir
        filepath = save_results(results, output_dir, fmt, library_dir=self.config.paths.library_dir)

        logging.success(f"结果已保存: {filepath}")
        return results, filepath

    # ── 内部实现 ──────────────────────────

    def _scan_one(self, url, timeout, visited=None, client_redirect_depth=0, scheduled_urls=None):
        """扫描单个 URL，返回结果 dict"""
        visited = visited or set()
        visited.add(url)
        session = requests.Session()
        try:
            with session.get(
                url, timeout=(3, timeout),  # (连接3s, 读取timeout)
                headers=dict(self._headers),
                verify=False,
                allow_redirects=True,
                stream=True,
                proxies=self.config.proxies(),
            ) as resp:
                try:
                    return self._process_response(
                        url,
                        resp,
                        timeout,
                        session=session,
                        visited=visited,
                        client_redirect_depth=client_redirect_depth,
                        scheduled_urls=scheduled_urls,
                    )
                except Exception as e:
                    return self._error_result(
                        url,
                        "response_parse_error",
                        str(e),
                        status=getattr(resp, 'status_code', '-'),
                        server=self._safe_server_header(resp),
                    )
        except requests.exceptions.ConnectTimeout as e:
            return self._error_result(url, "connect_timeout", str(e))
        except requests.exceptions.ReadTimeout as e:
            return self._error_result(url, "read_timeout", str(e))
        except requests.exceptions.TooManyRedirects as e:
            return self._error_result(url, "too_many_redirects", str(e))
        except requests.exceptions.ProxyError as e:
            return self._error_result(url, "proxy_error", str(e))
        except requests.exceptions.SSLError as e:
            return self._error_result(url, "ssl_error", str(e))
        except (requests.exceptions.InvalidURL,
                requests.exceptions.InvalidSchema,
                requests.exceptions.MissingSchema) as e:
            return self._error_result(url, "invalid_url", str(e))
        except requests.exceptions.ConnectionError as e:
            return self._error_result(url, "connection_error", str(e))
        except requests.exceptions.Timeout as e:
            return self._error_result(url, "timeout", str(e))
        except requests.exceptions.RequestException as e:
            return self._error_result(url, "request_error", str(e))
        except Exception as e:
            return self._error_result(url, "unknown_error", str(e))
        finally:
            session.close()

    def _process_response(self, url, response, timeout, session, visited=None, client_redirect_depth=0, scheduled_urls=None):
        """解析 HTTP 响应，做指纹匹配"""
        visited = visited or {url}
        effective_url = getattr(response, 'url', url) or url
        content_length = int(response.headers.get("content-length", 0) or 0)

        raw_bytes = response.raw.read(self.BODY_READ_LIMIT, decode_content=True)
        response._content = raw_bytes
        response._content_consumed = True
        encoding = response.encoding
        if encoding == 'ISO-8859-1':
            encoding = response.apparent_encoding
        encoding = encoding or "utf-8"
        response.encoding = encoding
        html = raw_bytes.decode(encoding, "ignore")
        size = content_length or len(html)
        body_truncated = bool(content_length and content_length > len(raw_bytes))

        title = self._get_title(html)

        if self._should_retry_https(url, response, html, title):
            retry_url = self._build_https_retry_url(effective_url)
            logging.info(f"检测到 HTTPS 端口误用 HTTP，请求自动升级: {url} -> {retry_url}")
            if retry_url not in visited and not self._is_already_scheduled_upgrade_target(url, retry_url, scheduled_urls):
                return self._scan_one(
                    retry_url,
                    timeout,
                    visited=visited,
                    client_redirect_depth=client_redirect_depth,
                    scheduled_urls=scheduled_urls,
                )

        client_redirect_url = self._extract_client_redirect_url(
            base_url=effective_url,
            response=response,
            html=html,
            title=title,
            visited=visited,
            client_redirect_depth=client_redirect_depth,
        )
        if client_redirect_url:
            logging.info(f"检测到前端跳转，自动跟进: {url} -> {client_redirect_url}")
            return self._scan_one(
                client_redirect_url,
                timeout,
                visited=visited,
                client_redirect_depth=client_redirect_depth + 1,
                scheduled_urls=scheduled_urls,
            )

        server = response.headers.get("Server", "")
        server = "" if len(server) > 50 else server

        datas = {
            "url": effective_url, "title": title, "body": html,
            "status": response.status_code, "Server": server,
            "size": size, "header": response.headers,
            "faviconhash": {"ehole": 0, "fofa": 0, "md5": "0"},
            "iscdn": 0, "ip": "", "address": "", "isp": "",
        }

        favicon_url_hint = None
        if html and not body_truncated:
            parsed = urlsplit(effective_url)
            base = f"{parsed.scheme}://{parsed.netloc}"
            favicon_url_hint = self._find_favicon_href(html, base)
        faviconhash = self._get_faviconhash(
            effective_url,
            favicon_url_hint,
            session=session,
        )
        datas["faviconhash"] = faviconhash
        match_info = self.identify.match(datas)

        # CDN/IP (默认关闭，--cdn 开启)
        if self.config.cdn:
            try:
                iscdn, iplist = self.ip_factory.factory(effective_url)
                if iscdn == 0 and self.ip_factory.check_cdn_headers(response.headers):
                    iscdn = 1
                iplist_str = ','.join(set(iplist))
            except Exception:
                iscdn, iplist_str = 0, ""
        else:
            iscdn, iplist_str = 0, ""

        # 控制台实时输出（贴近 V5.1，增加置信度）
        if match_info["cms"]:
            from config.color import color
            logging.success("{0} {1} {2} {4} {3}  [{5}]".format(
                self._format_fingerprint_display(match_info),
                color.blue(server),
                str(title)[:50],
                color.yellow(str(response.status_code)),
                effective_url,
                color.cyan(str(match_info['confidence'])),
            ))

        # Server header 版本兜底提取
        version = match_info["version"] if match_info["version"] != "-" else ""
        if not version and server:
            version = self._extract_server_version(server)
        if version:
            version = version.strip()

        return {
            "url": effective_url,
            "cms": match_info["cms"],
            "confidence": match_info["confidence"],
            "fingerprints": match_info.get("fingerprints", []),
            "version": version or "-",
            "title": title,
            "status": response.status_code,
            "Server": server,
            "size": size,
            "iscdn": iscdn,
            "ip": iplist_str,
            "address": "",
            "isp": "",
            "faviconhash": faviconhash,
            "error_type": "",
            "error_detail": "",
        }

    @staticmethod
    def _format_fingerprint_display(match_info):
        from config.color import color
        fingerprints = match_info.get("fingerprints") or []
        if not fingerprints:
            return color.green(match_info.get("cms", ""))

        parts = []
        for item in fingerprints:
            text = f"{item.get('cms', '')}[{item.get('confidence', 0)}]"
            confidence = item.get("confidence", 0) or 0
            if confidence >= 80:
                parts.append(color.green(text))
            elif confidence >= 50:
                parts.append(color.yellow(text))
            else:
                parts.append(text)
        return ','.join(parts)

    def _should_retry_https(self, url, response, html, title):
        parsed = urlsplit(url)
        if parsed.scheme.lower() != 'http':
            return False
        if getattr(response, 'status_code', None) != 400:
            return False

        content = ' '.join([
            str(title or ''),
            str(html or ''),
        ]).lower()
        return any(marker in content for marker in self.HTTPS_UPGRADE_MARKERS)

    @staticmethod
    def _build_https_retry_url(url):
        parsed = urlsplit(url)
        return parsed._replace(scheme='https').geturl()

    @staticmethod
    def _normalize_url_identity(url):
        parsed = urlsplit(url)
        port = parsed.port
        default_port = 443 if parsed.scheme.lower() == 'https' else 80
        port = default_port if port is None else port
        path = parsed.path or '/'
        query = ('?' + parsed.query) if parsed.query else ''
        return (
            parsed.scheme.lower(),
            (parsed.hostname or '').lower(),
            port,
            path,
            query,
        )

    def _is_already_scheduled_upgrade_target(self, source_url, retry_url, scheduled_urls):
        if not scheduled_urls:
            return False
        retry_identity = self._normalize_url_identity(retry_url)
        source_identity = self._normalize_url_identity(source_url)
        for scheduled in scheduled_urls:
            scheduled_identity = self._normalize_url_identity(scheduled)
            if scheduled_identity == retry_identity and scheduled_identity != source_identity:
                return True
        return False

    def _extract_client_redirect_url(self, base_url, response, html, title, visited, client_redirect_depth):
        if client_redirect_depth >= self.MAX_CLIENT_REDIRECTS:
            return None
        if getattr(response, 'status_code', None) != 200:
            return None
        if not self._is_probable_client_redirect_page(html, title):
            return None

        target = self._extract_meta_refresh_target(html) or self._extract_js_redirect_target(html)
        if not target:
            return None

        target_url = urljoin(base_url, target.strip())
        if target_url in visited:
            return None
        if not self._is_same_scan_origin(base_url, target_url):
            return None
        return target_url

    @staticmethod
    def _extract_meta_refresh_target(html):
        patterns = (
            r'<meta[^>]+http-equiv=["\']?refresh["\']?[^>]+content=["\'][^"\']*?url\s*=\s*([^"\';>]+)',
            r'<meta[^>]+content=["\'][^"\']*?url\s*=\s*([^"\';>]+)[^>]*http-equiv=["\']?refresh["\']?',
            r'<meta[^>]+http-equiv=["\']?refresh["\']?[^>]+content=([^ >]+)',
        )
        for pattern in patterns:
            match = re.search(pattern, html, re.I)
            if not match:
                continue
            content = match.group(1).strip().strip("'\"")
            if pattern.endswith('content=([^ >]+)'):
                url_match = re.search(r'url\s*=\s*(.+)', content, re.I)
                if url_match:
                    content = url_match.group(1).strip().strip("'\"")
            if content:
                return content
        return None

    @staticmethod
    def _extract_js_redirect_target(html):
        patterns = (
            r'(?:window\.)?(?:top\.)?location(?:\.href)?\s*=\s*[\'"]([^\'"]+)[\'"]',
            r'location\.replace\(\s*[\'"]([^\'"]+)[\'"]',
        )
        for pattern in patterns:
            match = re.search(pattern, html, re.I)
            if match:
                target = match.group(1).strip()
                if target:
                    return target
        return None

    @staticmethod
    def _is_same_scan_origin(source_url, target_url):
        source = urlsplit(source_url)
        target = urlsplit(target_url)
        if target.scheme.lower() not in {'http', 'https'}:
            return False
        return bool(source.hostname and target.hostname and source.hostname.lower() == target.hostname.lower())

    @staticmethod
    def _is_probable_client_redirect_page(html, title):
        if not html:
            return False
        if not (
            re.search(r'<meta[^>]+http-equiv=["\']?refresh', html, re.I)
            or re.search(r'(?:window\.)?(?:top\.)?location(?:\.href)?\s*=', html, re.I)
            or re.search(r'location\.replace\(', html, re.I)
        ):
            return False

        sanitized = re.sub(r'<script\b[^>]*>.*?</script>', ' ', html, flags=re.I | re.S)
        sanitized = re.sub(r'<style\b[^>]*>.*?</style>', ' ', sanitized, flags=re.I | re.S)
        visible = re.sub(r'<[^>]+>', ' ', sanitized)
        visible = re.sub(r'\s+', ' ', visible).strip()
        if len(visible) <= 120:
            return True

        title_text = (title or '').strip().lower()
        return title_text in {'redirect', 'redirecting', 'loading', 'login'}

    def _error_result(self, url, error_type, error_detail, status='-', server=''):
        return {
            "url": url,
            "cms": "-",
            "confidence": 0,
            "version": "-",
            "title": "",
            "status": status,
            "Server": server or "-",
            "size": "-",
            "iscdn": "-",
            "ip": "-",
            "address": "-",
            "isp": "-",
            "faviconhash": {"ehole": 0, "fofa": 0, "md5": "0"},
            "error_type": error_type,
            "error_detail": error_detail,
        }

    @staticmethod
    def _safe_server_header(response):
        try:
            server = response.headers.get("Server", "")
        except Exception:
            return ""
        return "" if len(server) > 50 else server

    # ── HTTP 请求工具 ──────────────────────

    def _get_headers(self):
        ua = random.choice(settings.user_agents)
        if self.config.user_agents:
            ua = random.choice(self.config.user_agents)
        return {
            'Accept': 'text/html,application/xhtml+xml,'
                      'application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'User-Agent': ua,
        }

    # ── favicon ───────────────────────────

    def _get_faviconhash(self, url, favicon_url_hint=None, session=None, skip_fetch=False):
        favicon_url = url
        if skip_fetch:
            return {'ehole': 0, 'fofa': 0, 'md5': '0'}
        try:
            parsed = urlsplit(url)
            base = f"{parsed.scheme}://{parsed.netloc}"
            target = favicon_url_hint if favicon_url_hint else urljoin(base, "favicon.ico")
            favicon_url = target
            h = dict(self._headers)
            h['Accept'] = 'image/avif,image/webp,image/png,image/svg+xml,image/*;q=0.8,*/*;q=0.5'
            h['Sec-Fetch-Dest'] = 'image'
            h['Sec-Fetch-Mode'] = 'no-cors'
            h['Sec-Fetch-Site'] = 'same-origin'
            h.pop('Upgrade-Insecure-Requests', None)
            h.pop('Sec-Fetch-User', None)
            requester = session or requests
            resp = requester.get(target, headers=h, timeout=3, verify=False, proxies=self.config.proxies())
            raw = resp.content
            return {'ehole': mmh3.hash(base64.encodebytes(raw)),
                    'fofa': mmh3.hash(base64.b64encode(raw)),
                    'md5': hashlib.md5(raw).hexdigest()}
        except Exception as e:
            logging.warning(f"favicon 获取失败: {favicon_url} → {e}")
            return {'ehole': 0, 'fofa': 0, 'md5': '0'}

    def _find_favicon_href(self, html, base_url):
        """正则提取 favicon 路径，兼容 href/rel 任意顺序"""
        try:
            # 方案1: 提取 link[rel=icon] 中的 href
            m = re.search(
                r'<link[^>]+?rel=["\'](?:icon|shortcut icon|apple-touch-icon)["\'][^>]*?href=["\']([^"\']+)["\']',
                html, re.I)
            if m and not m.group(1).startswith('data:'):
                return urljoin(base_url, m.group(1))
            # 方案2: rel 和 href 顺序相反
            m = re.search(
                r'<link[^>]+?href=["\']([^"\']+)["\'][^>]*?rel=["\'](?:icon|shortcut icon|apple-touch-icon)["\']',
                html, re.I)
            if m and not m.group(1).startswith('data:'):
                return urljoin(base_url, m.group(1))
        except Exception:
            pass
        return None

    def _extract_server_version(self, server):
        """从 Server header 提取版本号，作为兜底"""
        # Apache-Coyote/1.1 (必须在 Apache/... 之前匹配)
        m = re.match(r'Apache-Coyote/([\d.]+)', server, re.I)
        if m: return f'Apache-Coyote {m.group(1)}'
        # Apache/2.4.47 (Win64)
        m = re.match(r'Apache/([\d.]+)', server, re.I)
        if m: return f'Apache {m.group(1)}'
        # nginx/1.18.0, nginx/1.24.0 (Ubuntu)
        m = re.match(r'nginx/([\d.]+)', server, re.I)
        if m: return f'nginx {m.group(1)}'
        # Microsoft-IIS/10.0
        m = re.match(r'Microsoft-IIS/([\d.]+)', server, re.I)
        if m: return f'IIS {m.group(1)}'
        # Virata-EmWeb/R6_2_1 (HP printers)
        m = re.match(r'Virata-EmWeb/([\w\d_.]+)', server, re.I)
        if m: return f'Virata-EmWeb {m.group(1)}'
        # OpenResty/1.21.4
        m = re.match(r'[Oo]pen[Rr]esty/([\d.]+)', server)
        if m: return f'OpenResty {m.group(1)}'
        # lighttpd/1.4.56
        m = re.match(r'lighttpd/([\d.]+)', server, re.I)
        if m: return f'lighttpd {m.group(1)}'
        # gSOAP/2.8
        m = re.match(r'gSOAP/([\d.]+)', server)
        if m: return f'gSOAP {m.group(1)}'
        # PHP/8.0.5
        m = re.search(r'PHP/([\d.]+)', server, re.I)
        if m: return f'PHP {m.group(1)}'
        # squid/frontier-squid-4.13
        m = re.match(r'squid/[^\s]*?(\d+[.\d]+)', server, re.I)
        if m: return f'squid {m.group(1)}'
        # Generic fallback: Product/V[ersion] or Product/version
        m = re.match(r'([^\s/]+)/(?:[Vv])?(\d+[.\d]*)', server)
        if m: return f'{m.group(1)} {m.group(2)}'
        # Multi-word product: "Rapid Logic/1.1", "EPSON UPnP/1.0"
        m = re.match(r'([^\s/]+(?:\s+[^\s/]+)?)/(\d+[.\d]*)', server)
        if m: return f'{m.group(1)} {m.group(2)}'
        return ''

    # ── HTML 解析 ─────────────────────────

    @staticmethod
    def _get_title(html):
        """正则提取标题"""
        if not html:
            return ''
        m = re.search(r'<title[^>]*>([^<]+)</title>', html, re.I | re.S)
        if m: return m.group(1).strip().replace('\r', '').replace('\n', '')
        for tag in ('h1', 'h2', 'h3'):
            m = re.search(rf'<{tag}[^>]*>([^<]+)</{tag}>', html, re.I)
            if m: return m.group(1).strip().replace('\r', '').replace('\n', '')
        m = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
        if m: return m.group(1).strip()
        m = re.search(r'<meta[^>]+name=["\']keywords["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
        if m: return m.group(1).strip()
        text = re.sub(r'<[^>]+>', ' ', html).strip()
        return text if len(text) <= 200 else ''
