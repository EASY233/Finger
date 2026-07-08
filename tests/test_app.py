#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

try:
    from lib.app import FingerApplication
    APP_IMPORT_ERROR = None
except ModuleNotFoundError as exc:
    FingerApplication = None
    APP_IMPORT_ERROR = exc


def build_args(**overrides):
    defaults = {
        "url": "http://example.test",
        "file": None,
        "ip": None,
        "ipfile": None,
        "fofa": False,
        "quake": False,
        "api_query": "",
        "api_size": None,
        "cdn": False,
        "geo": False,
        "audit": False,
        "proxy": "",
        "output": "json",
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


class AppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    @unittest.skipIf(FingerApplication is None, f"app runtime dependency missing: {APP_IMPORT_ERROR}")
    def test_application_collects_urls_and_runs_scan(self):
        app = FingerApplication(root_dir=self.root)
        args = build_args()
        fake_result = [{
            "url": "http://example.test",
            "cms": "0example",
            "confidence": 80,
            "version": "-",
            "title": "Example",
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
        }]

        with patch('lib.app.Finger.scan', return_value=fake_result):
            results, output = app.run(args)

        self.assertEqual(fake_result, results)
        self.assertTrue(output.path.endswith('.json'))

    @unittest.skipIf(FingerApplication is None, f"app runtime dependency missing: {APP_IMPORT_ERROR}")
    def test_application_fofa_ip_targets_are_deduplicated(self):
        app = FingerApplication(root_dir=self.root)
        args = build_args(url=None, ip="127.0.0.1", fofa=False, output="json")
        run_config = app.build_run_config(args)

        with patch('lib.app.FofaClient.search_ip_web_assets', return_value=[
            "http://dup.test", "http://dup.test", "https://dup.test"
        ]):
            urls = app.collect_urls(run_config)

        self.assertEqual(["http://dup.test", "https://dup.test"], urls)

    @unittest.skipIf(FingerApplication is None, f"app runtime dependency missing: {APP_IMPORT_ERROR}")
    def test_checkenv_does_not_auto_update_on_init(self):
        with patch('lib.checkenv.CheckEnv.update') as update_mock:
            FingerApplication(root_dir=self.root)
        update_mock.assert_not_called()


if __name__ == '__main__':
    unittest.main()
