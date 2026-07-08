#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import unittest

from lib.identify import Identify
from lib.runtime import RuntimePaths


def load_json(pathname):
    with open(pathname, 'r', encoding='utf-8') as file:
        return json.load(file)


class PageRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        cls.paths = RuntimePaths.from_root(root)
        cls.identify = Identify(library_dir=cls.paths.library_dir)
        cls.case_file = os.path.join(cls.paths.root_dir, 'tests', 'fixtures', 'page_regression_cases.json')
        cls.page_dir = os.path.join(cls.paths.root_dir, 'tests', 'fixtures', 'pages')
        cls.cases = load_json(cls.case_file)

    def test_real_page_regression_cases(self):
        for case in self.cases:
            with self.subTest(case=case["name"]):
                page = load_json(os.path.join(self.page_dir, case["page"]))
                page.setdefault("size", len(page.get("body", "")))
                page.setdefault("iscdn", 0)
                page.setdefault("ip", "")
                page.setdefault("address", "")
                page.setdefault("isp", "")
                page.setdefault("header", {})
                page.setdefault("faviconhash", {"ehole": 0, "fofa": 0, "md5": "0"})

                summary = self.identify.match(page)
                details = self.identify.match_details(page)
                cms_values = [item.strip() for item in summary["cms"].split(',') if item.strip()]
                details_by_cms = {item["cms"]: item for item in details}

                for cms in case.get("expect_cms_contains", []):
                    self.assertIn(cms, cms_values)

                for cms in case.get("expect_cms_absent", []):
                    self.assertNotIn(cms, cms_values)

                for version_text in case.get("expect_version_contains", []):
                    self.assertIn(version_text, summary.get("version", ""))

                for cms_prefix in case.get("expect_version_prefix", []):
                    self.assertTrue(
                        any(version.startswith(cms_prefix) for version in summary.get("version", "").split(',')),
                        msg=f"{case['name']} missing version prefix {cms_prefix}: {summary.get('version', '')}",
                    )

                for cms, bounds in case.get("expect_cms_confidence", {}).items():
                    self.assertIn(cms, details_by_cms)
                    if "min" in bounds:
                        self.assertGreaterEqual(details_by_cms[cms]["confidence"], bounds["min"])
                    if "max" in bounds:
                        self.assertLessEqual(details_by_cms[cms]["confidence"], bounds["max"])


if __name__ == '__main__':
    unittest.main()
