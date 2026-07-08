#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest
from unittest.mock import patch
from requests.structures import CaseInsensitiveDict

import requests

from lib.identify import Identify
from lib.runtime import RuntimePaths

try:
    from lib.finger import Finger
    from lib.req import Request
    FINGER_IMPORT_ERROR = None
except ModuleNotFoundError as exc:
    Finger = None
    Request = None
    FINGER_IMPORT_ERROR = exc


def build_identify_datas(body=''):
    return {
        "url": "http://example.test",
        "title": "Example",
        "body": body,
        "status": 200,
        "Server": "nginx/1.24.0",
        "size": len(body),
        "header": {"Server": "nginx/1.24.0"},
        "faviconhash": {"ehole": 0, "fofa": 0, "md5": "0"},
        "iscdn": 0,
        "ip": "127.0.0.1",
        "address": "",
        "isp": "",
    }


class FakeRaw:
    def __init__(self, body):
        self.body = body
        self.offset = 0

    def read(self, size=-1, decode_content=False):
        if self.offset >= len(self.body):
            return b''
        if size is None or size < 0:
            chunk = self.body[self.offset:]
            self.offset = len(self.body)
            return chunk
        chunk = self.body[self.offset:self.offset + size]
        self.offset += len(chunk)
        return chunk


class ScanBehaviorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        cls.paths = RuntimePaths.from_root(root)

    @unittest.skipIf(Finger is None, f"finger runtime dependency missing: {FINGER_IMPORT_ERROR}")
    def test_stream_body_is_not_consumed_by_apparent_encoding(self):
        finger = Finger(threads=1)

        class FakeResponse:
            def __init__(self, url, status_code, body, headers=None):
                self.url = url
                self.status_code = status_code
                self._body = body.encode('utf-8')
                self.headers = CaseInsensitiveDict(headers or {})
                self.encoding = 'ISO-8859-1'
                self.raw = FakeRaw(self._body)

            @property
            def apparent_encoding(self):
                if not hasattr(self, '_content'):
                    self._content = self.raw.read(decode_content=True)
                    self._content_consumed = True
                return 'utf-8'

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        class FakeSession:
            def get(self, url, **kwargs):
                return FakeResponse(
                    url=url,
                    status_code=200,
                    body='<html><title>Swagger UI</title><body><div id="swagger-ui"></div></body></html>',
                    headers={"Server": "nginx/1.24.0", "content-length": "80"},
                )

            def close(self):
                return None

        seen = {}

        def fake_match(datas):
            seen['title'] = datas.get('title')
            seen['body'] = datas.get('body')
            return {"cms": "Swagger UI", "confidence": 85, "version": "-"}

        with patch('lib.finger.requests.Session', return_value=FakeSession()), \
                patch.object(Finger, '_get_faviconhash', return_value={"ehole": 0, "fofa": 0, "md5": "0"}), \
                patch.object(finger.identify, 'match', side_effect=fake_match):
            result = finger.scan(['http://swagger.test'])[0]

        self.assertEqual('Swagger UI', seen['title'])
        self.assertIn('swagger-ui', seen['body'])
        self.assertEqual('Swagger UI', result["cms"])

    @unittest.skipIf(Finger is None, f"finger runtime dependency missing: {FINGER_IMPORT_ERROR}")
    def test_connect_timeout_is_classified(self):
        finger = Finger(threads=1)
        fake_session = type('FakeSession', (), {
            'get': staticmethod(lambda *args, **kwargs: (_ for _ in ()).throw(requests.exceptions.ConnectTimeout('connect timed out'))),
            'close': staticmethod(lambda: None),
        })()
        with patch('lib.finger.requests.Session', return_value=fake_session):
            result = finger.scan(['http://timeout.test'])[0]

        self.assertEqual('connect_timeout', result["error_type"])
        self.assertEqual('-', result["cms"])
        self.assertIn('timed out', result["error_detail"])

    @unittest.skipIf(Finger is None, f"finger runtime dependency missing: {FINGER_IMPORT_ERROR}")
    def test_http_400_plain_http_to_https_port_retries_with_https(self):
        finger = Finger(threads=1)

        class FakeResponse:
            def __init__(self, url, status_code, body, headers=None, encoding='utf-8'):
                self.url = url
                self.status_code = status_code
                self._body = body.encode(encoding)
                self.headers = CaseInsensitiveDict(headers or {})
                self.encoding = encoding
                self.apparent_encoding = encoding
                self.content = self._body
                self.raw = FakeRaw(self._body)

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        calls = []

        class FakeSession:
            def get(self, url, **kwargs):
                return fake_get(url, **kwargs)

            def close(self):
                return None

        def fake_get(url, **kwargs):
            calls.append(url)
            if url == 'http://upgrade.test':
                return FakeResponse(
                    url=url,
                    status_code=400,
                    body='<html><title>400 Bad Request</title><body>The plain HTTP request was sent to HTTPS port</body></html>',
                    headers={"Server": "nginx/1.24.0", "content-length": "104"},
                )
            if url == 'https://upgrade.test':
                return FakeResponse(
                    url=url,
                    status_code=200,
                    body='<html><title>Secure Console</title><body>ok</body></html>',
                    headers={"Server": "nginx/1.24.0", "content-length": "58"},
                )
            raise AssertionError(f'unexpected url {url}')

        with patch('lib.finger.requests.Session', return_value=FakeSession()), \
                patch.object(Finger, '_get_faviconhash', return_value={"ehole": 0, "fofa": 0, "md5": "0"}), \
                patch.object(finger.identify, 'match', return_value={"cms": "SecureApp", "confidence": 88, "version": "-"}):
            result = finger.scan(['http://upgrade.test'])[0]

        self.assertEqual(['http://upgrade.test', 'https://upgrade.test'], calls[:2])
        self.assertEqual('https://upgrade.test', result["url"])
        self.assertEqual('SecureApp', result["cms"])
        self.assertEqual(200, result["status"])

    @unittest.skipIf(Finger is None, f"finger runtime dependency missing: {FINGER_IMPORT_ERROR}")
    def test_http_upgrade_does_not_duplicate_already_scheduled_https_target(self):
        finger = Finger(threads=1)

        class FakeResponse:
            def __init__(self, url, status_code, body, headers=None, encoding='utf-8'):
                self.url = url
                self.status_code = status_code
                self._body = body.encode(encoding)
                self.headers = CaseInsensitiveDict(headers or {})
                self.encoding = encoding
                self.apparent_encoding = encoding
                self.content = self._body
                self.raw = FakeRaw(self._body)

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        calls = []

        class FakeSession:
            def get(self, url, **kwargs):
                return fake_get(url, **kwargs)

            def close(self):
                return None

        def fake_get(url, **kwargs):
            calls.append(url)
            if url == 'http://dup-upgrade.test':
                return FakeResponse(
                    url=url,
                    status_code=400,
                    body='<html><title>400 Bad Request</title><body>The plain HTTP request was sent to HTTPS port</body></html>',
                    headers={"Server": "nginx/1.24.0", "content-length": "104"},
                )
            if url == 'https://dup-upgrade.test':
                return FakeResponse(
                    url=url,
                    status_code=200,
                    body='<html><title>Secure Console</title><body>ok</body></html>',
                    headers={"Server": "nginx/1.24.0", "content-length": "58"},
                )
            raise AssertionError(f'unexpected url {url}')

        with patch('lib.finger.requests.Session', return_value=FakeSession()), \
                patch.object(Finger, '_get_faviconhash', return_value={"ehole": 0, "fofa": 0, "md5": "0"}), \
                patch.object(finger.identify, 'match', return_value={"cms": "SecureApp", "confidence": 88, "version": "-"}):
            results = finger.scan(['http://dup-upgrade.test', 'https://dup-upgrade.test'])

        self.assertEqual(2, len(results))
        self.assertEqual(['http://dup-upgrade.test', 'https://dup-upgrade.test'], calls)

    @unittest.skipIf(Finger is None, f"finger runtime dependency missing: {FINGER_IMPORT_ERROR}")
    def test_http_400_without_https_upgrade_marker_does_not_retry(self):
        finger = Finger(threads=1)

        class FakeResponse:
            def __init__(self, url, status_code, body, headers=None, encoding='utf-8'):
                self.url = url
                self.status_code = status_code
                self._body = body.encode(encoding)
                self.headers = CaseInsensitiveDict(headers or {})
                self.encoding = encoding
                self.apparent_encoding = encoding
                self.content = self._body
                self.raw = FakeRaw(self._body)

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        calls = []

        class FakeSession:
            def get(self, url, **kwargs):
                return fake_get(url, **kwargs)

            def close(self):
                return None

        def fake_get(url, **kwargs):
            calls.append(url)
            return FakeResponse(
                url=url,
                status_code=400,
                body='<html><title>400 Bad Request</title><body>generic bad request</body></html>',
                headers={"Server": "nginx/1.24.0", "content-length": "74"},
            )

        with patch('lib.finger.requests.Session', return_value=FakeSession()), \
                patch.object(Finger, '_get_faviconhash', return_value={"ehole": 0, "fofa": 0, "md5": "0"}), \
                patch.object(finger.identify, 'match', return_value={"cms": "", "confidence": 0, "version": "-"}):
            result = finger.scan(['http://no-upgrade.test'])[0]

        self.assertEqual(['http://no-upgrade.test'], calls)
        self.assertEqual('http://no-upgrade.test', result["url"])
        self.assertEqual(400, result["status"])

    @unittest.skipIf(Finger is None, f"finger runtime dependency missing: {FINGER_IMPORT_ERROR}")
    def test_meta_refresh_redirect_is_followed_within_same_origin(self):
        finger = Finger(threads=1)

        class FakeResponse:
            def __init__(self, url, status_code, body, headers=None, encoding='utf-8'):
                self.url = url
                self.status_code = status_code
                self._body = body.encode(encoding)
                self.headers = CaseInsensitiveDict(headers or {})
                self.encoding = encoding
                self.apparent_encoding = encoding
                self.content = self._body
                self.raw = FakeRaw(self._body)

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        calls = []

        class FakeSession:
            def get(self, url, **kwargs):
                return fake_get(url, **kwargs)

            def close(self):
                return None

        def fake_get(url, **kwargs):
            calls.append(url)
            if url == 'http://redir.test/':
                return FakeResponse(
                    url=url,
                    status_code=200,
                    body='<html><head><meta http-equiv="refresh" content="0;url=/login"></head><body></body></html>',
                    headers={"Server": "nginx/1.24.0", "content-length": "92"},
                )
            if url == 'http://redir.test/login':
                return FakeResponse(
                    url=url,
                    status_code=200,
                    body='<html><title>Login</title><body>login page</body></html>',
                    headers={"Server": "nginx/1.24.0", "content-length": "58"},
                )
            raise AssertionError(f'unexpected url {url}')

        with patch('lib.finger.requests.Session', return_value=FakeSession()), \
                patch.object(Finger, '_get_faviconhash', return_value={"ehole": 0, "fofa": 0, "md5": "0"}), \
                patch.object(finger.identify, 'match', return_value={"cms": "Portal", "confidence": 77, "version": "-"}):
            result = finger.scan(['http://redir.test/'])[0]

        self.assertEqual(['http://redir.test/', 'http://redir.test/login'], calls[:2])
        self.assertEqual('http://redir.test/login', result["url"])
        self.assertEqual('Portal', result["cms"])

    @unittest.skipIf(Finger is None, f"finger runtime dependency missing: {FINGER_IMPORT_ERROR}")
    def test_js_redirect_is_followed_within_same_origin(self):
        finger = Finger(threads=1)

        class FakeResponse:
            def __init__(self, url, status_code, body, headers=None, encoding='utf-8'):
                self.url = url
                self.status_code = status_code
                self._body = body.encode(encoding)
                self.headers = CaseInsensitiveDict(headers or {})
                self.encoding = encoding
                self.apparent_encoding = encoding
                self.content = self._body
                self.raw = FakeRaw(self._body)

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        calls = []

        class FakeSession:
            def get(self, url, **kwargs):
                return fake_get(url, **kwargs)

            def close(self):
                return None

        def fake_get(url, **kwargs):
            calls.append(url)
            if url == 'http://jsredir.test/':
                return FakeResponse(
                    url=url,
                    status_code=200,
                    body="<html><body><script>window.location.href='/console';</script></body></html>",
                    headers={"Server": "nginx/1.24.0", "content-length": "77"},
                )
            if url == 'http://jsredir.test/console':
                return FakeResponse(
                    url=url,
                    status_code=200,
                    body='<html><title>Console</title><body>ok</body></html>',
                    headers={"Server": "nginx/1.24.0", "content-length": "51"},
                )
            raise AssertionError(f'unexpected url {url}')

        with patch('lib.finger.requests.Session', return_value=FakeSession()), \
                patch.object(Finger, '_get_faviconhash', return_value={"ehole": 0, "fofa": 0, "md5": "0"}), \
                patch.object(finger.identify, 'match', return_value={"cms": "ConsoleApp", "confidence": 79, "version": "-"}):
            result = finger.scan(['http://jsredir.test/'])[0]

        self.assertEqual(['http://jsredir.test/', 'http://jsredir.test/console'], calls[:2])
        self.assertEqual('http://jsredir.test/console', result["url"])
        self.assertEqual('ConsoleApp', result["cms"])

    @unittest.skipIf(Finger is None, f"finger runtime dependency missing: {FINGER_IMPORT_ERROR}")
    def test_cross_origin_client_redirect_is_not_followed(self):
        finger = Finger(threads=1)

        class FakeResponse:
            def __init__(self, url, status_code, body, headers=None, encoding='utf-8'):
                self.url = url
                self.status_code = status_code
                self._body = body.encode(encoding)
                self.headers = CaseInsensitiveDict(headers or {})
                self.encoding = encoding
                self.apparent_encoding = encoding
                self.content = self._body
                self.raw = FakeRaw(self._body)

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        calls = []

        class FakeSession:
            def get(self, url, **kwargs):
                return fake_get(url, **kwargs)

            def close(self):
                return None

        def fake_get(url, **kwargs):
            calls.append(url)
            return FakeResponse(
                url=url,
                status_code=200,
                body='<html><head><meta http-equiv="refresh" content="0;url=https://other.test/login"></head><body></body></html>',
                headers={"Server": "nginx/1.24.0", "content-length": "108"},
            )

        with patch('lib.finger.requests.Session', return_value=FakeSession()), \
                patch.object(Finger, '_get_faviconhash', return_value={"ehole": 0, "fofa": 0, "md5": "0"}), \
                patch.object(finger.identify, 'match', return_value={"cms": "", "confidence": 0, "version": "-"}):
            result = finger.scan(['http://same-origin.test/'])[0]

        self.assertEqual(['http://same-origin.test/'], calls)
        self.assertEqual('http://same-origin.test/', result["url"])
        self.assertEqual(200, result["status"])

    @unittest.skipIf(Finger is None, f"finger runtime dependency missing: {FINGER_IMPORT_ERROR}")
    def test_final_result_uses_effective_redirect_url(self):
        finger = Finger(threads=1)

        class FakeResponse:
            def __init__(self, request_url, effective_url, status_code, body, headers=None, encoding='utf-8'):
                self.request_url = request_url
                self.url = effective_url
                self.status_code = status_code
                self.headers = CaseInsensitiveDict(headers or {})
                self.encoding = encoding
                self.apparent_encoding = encoding
                self.content = body.encode(encoding)
                self.raw = FakeRaw(self.content)

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        class FakeSession:
            def __init__(self, response):
                self.response = response

            def get(self, url, **kwargs):
                return self.response

            def close(self):
                return None

        fake_response = FakeResponse(
            request_url='http://redirected.test',
            effective_url='https://redirected.test/login',
            status_code=200,
            body='<html><title>Login</title><body>ok</body></html>',
            headers={"Server": "nginx/1.24.0", "content-length": "49"},
        )

        with patch('lib.finger.requests.Session', return_value=FakeSession(fake_response)), \
                patch.object(Finger, '_get_faviconhash', return_value={"ehole": 0, "fofa": 0, "md5": "0"}), \
                patch.object(finger.identify, 'match', return_value={"cms": "RedirectedApp", "confidence": 80, "version": "-"}):
            result = finger.scan(['http://redirected.test'])[0]

        self.assertEqual('https://redirected.test/login', result["url"])

    @unittest.skipIf(Finger is None, f"finger runtime dependency missing: {FINGER_IMPORT_ERROR}")
    def test_large_body_is_truncated_not_discarded(self):
        finger = Finger(threads=1)

        class FakeResponse:
            def __init__(self, url, status_code, body, headers=None, encoding='utf-8'):
                self.url = url
                self.status_code = status_code
                self.headers = CaseInsensitiveDict(headers or {})
                self.encoding = encoding
                self.apparent_encoding = encoding
                self.content = body.encode(encoding)
                self.raw = FakeRaw(self.content)

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        class FakeSession:
            def __init__(self, response):
                self.response = response

            def get(self, url, **kwargs):
                return self.response

            def close(self):
                return None

        body = '<html><title>Huge Console</title><body>' + ('A' * 140000) + '</body></html>'
        fake_response = FakeResponse(
            url='http://large.test',
            status_code=200,
            body=body,
            headers={"Server": "nginx/1.24.0", "content-length": str(len(body.encode('utf-8')))},
        )
        seen = {}

        def fake_match(datas):
            seen['body_len'] = len(datas.get('body', ''))
            seen['title'] = datas.get('title')
            return {"cms": "LargeApp", "confidence": 70, "version": "-"}

        with patch('lib.finger.requests.Session', return_value=FakeSession(fake_response)), \
                patch.object(Finger, '_get_faviconhash', return_value={"ehole": 0, "fofa": 0, "md5": "0"}), \
                patch.object(finger.identify, 'match', side_effect=fake_match):
            result = finger.scan(['http://large.test'])[0]

        self.assertEqual('Huge Console', seen['title'])
        self.assertGreater(seen['body_len'], 1000)
        self.assertEqual('LargeApp', result["cms"])

    @unittest.skipIf(Finger is None, f"finger runtime dependency missing: {FINGER_IMPORT_ERROR}")
    def test_large_body_still_fetches_favicon(self):
        finger = Finger(threads=1)

        class FakeResponse:
            def __init__(self, url, status_code, body, headers=None, encoding='utf-8'):
                self.url = url
                self.status_code = status_code
                self.headers = CaseInsensitiveDict(headers or {})
                self.encoding = encoding
                self.apparent_encoding = encoding
                self.content = body.encode(encoding)
                self.raw = FakeRaw(self.content)

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        class FakeSession:
            def __init__(self, response):
                self.response = response

            def get(self, url, **kwargs):
                return self.response

            def close(self):
                return None

        body = '<html><title>Huge Console</title><body>' + ('A' * 140000) + '</body></html>'
        response = FakeResponse(
            url='http://large-favicon.test',
            status_code=200,
            body=body,
            headers={"Server": "nginx/1.24.0", "content-length": str(len(body.encode('utf-8')))},
        )

        with patch('lib.finger.requests.Session', return_value=FakeSession(response)), \
                patch.object(Finger, '_get_faviconhash', return_value={"ehole": 0, "fofa": 0, "md5": "0"}) as favicon_mock, \
                patch.object(
                    finger.identify,
                    'match',
                    return_value={"cms": "LargeApp", "confidence": 70, "version": "-"},
                ):
            result = finger.scan(['http://large-favicon.test'])[0]

        self.assertEqual('LargeApp', result["cms"])
        favicon_mock.assert_called_once()

    @unittest.skipIf(Finger is None, f"finger runtime dependency missing: {FINGER_IMPORT_ERROR}")
    def test_strong_match_still_fetches_favicon(self):
        finger = Finger(threads=1)

        class FakeResponse:
            def __init__(self, url, status_code, body, headers=None, encoding='utf-8'):
                self.url = url
                self.status_code = status_code
                self._body = body.encode(encoding)
                self.headers = CaseInsensitiveDict(headers or {})
                self.encoding = encoding
                self.apparent_encoding = encoding
                self.content = self._body
                self.raw = FakeRaw(self._body)

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        class FakeSession:
            def __init__(self, response):
                self.response = response

            def get(self, url, **kwargs):
                return self.response

            def close(self):
                return None

        response = FakeResponse(
            url='http://strong.test',
            status_code=200,
            body='<html><title>Strong Product</title><body>ok</body></html>',
            headers={"Server": "nginx/1.24.0", "content-length": "56"},
        )

        with patch('lib.finger.requests.Session', return_value=FakeSession(response)), \
                patch.object(Finger, '_get_faviconhash') as favicon_mock, \
                patch.object(
                    finger.identify,
                    'match',
                    return_value={"cms": "StrongProduct", "confidence": 92, "version": "StrongProduct 1.0"},
                ) as match_mock:
            result = finger.scan(['http://strong.test'])[0]

        self.assertEqual('StrongProduct', result["cms"])
        self.assertEqual(1, match_mock.call_count)
        favicon_mock.assert_called_once()

    def test_identify_run_is_pure_without_result_store(self):
        identify = Identify(library_dir=self.paths.library_dir)
        identify.obj = [{
            "cms": "PureRule",
            "method": "keyword",
            "location": "body",
            "keyword": ["pure-match"],
        }]
        identify._prepare_app()

        result = identify.run(build_identify_datas('pure-match'))

        self.assertEqual('PureRule', result["cms"])

    def test_identify_run_appends_to_explicit_result_store(self):
        identify = Identify(library_dir=self.paths.library_dir)
        identify.obj = [{
            "cms": "StoredRule",
            "method": "keyword",
            "location": "body",
            "keyword": ["store-match"],
        }]
        identify._prepare_app()

        store = []
        result = identify.run(build_identify_datas('store-match'), result_store=store, log_result=False)

        self.assertEqual('StoredRule', result["cms"])
        self.assertEqual(1, len(store))
        self.assertEqual('StoredRule', store[0]["cms"])

    @unittest.skipIf(Request is None, f"finger runtime dependency missing: {FINGER_IMPORT_ERROR}")
    def test_legacy_request_uses_finger_results_and_separates_errors(self):
        from config.data import Urlerror, Urls, Webinfo
        success = {
            "url": "http://ok.test",
            "cms": "Match",
            "confidence": 80,
            "version": "-",
            "title": "OK",
            "status": 200,
            "Server": "nginx",
            "size": 12,
            "iscdn": 0,
            "ip": "",
            "address": "",
            "isp": "",
            "faviconhash": {"ehole": 0, "fofa": 0, "md5": "0"},
            "error_type": "",
            "error_detail": "",
        }
        error = {
            "url": "http://fail.test",
            "cms": "-",
            "confidence": 0,
            "version": "-",
            "title": "",
            "status": "-",
            "Server": "-",
            "size": "-",
            "iscdn": "-",
            "ip": "-",
            "address": "-",
            "isp": "-",
            "faviconhash": {"ehole": 0, "fofa": 0, "md5": "0"},
            "error_type": "connection_error",
            "error_detail": "boom",
        }

        Urls.url = ['http://ok.test', 'http://fail.test']
        with patch('lib.req.Finger.scan', return_value=[success, error]):
            request = Request()

        self.assertEqual([success], Webinfo.result)
        self.assertEqual([error], Urlerror.result)
        self.assertEqual([success, error], request.results)


if __name__ == '__main__':
    unittest.main()
