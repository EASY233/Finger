#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import unittest

from lib.identify import Identify
from lib.runtime import RuntimePaths


def build_sample(entry):
    data = {
        "url": "http://example.test",
        "title": "",
        "body": "",
        "status": 200,
        "Server": "",
        "size": 0,
        "header": {},
        "faviconhash": {"ehole": 0, "fofa": 0, "md5": "0"},
        "iscdn": 0,
        "ip": "",
        "address": "",
        "isp": "",
    }
    data.update(entry.get("data", {}))
    if not data["header"] and data["Server"]:
        data["header"] = {"Server": data["Server"]}
    data["size"] = len(data.get("body", ""))
    return data


class RuleRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        cls.paths = RuntimePaths.from_root(root)
        fixture_path = os.path.join(root, 'tests', 'fixtures', 'rule_regression_samples.json')
        with open(fixture_path, 'r', encoding='utf-8') as file:
            cls.samples = json.load(file)

    def test_rule_regression_samples(self):
        identify = Identify(library_dir=self.paths.library_dir)

        for sample in self.samples:
            with self.subTest(sample=sample["name"]):
                sample_data = build_sample(sample)
                result = identify.match(sample_data)
                details = identify.match_details(sample_data)
                details_by_cms = {item["cms"]: item for item in details}
                cms_values = [value.strip() for value in result["cms"].split(',') if value.strip()]

                for cms in sample.get("expect_cms_contains", []):
                    self.assertIn(cms, cms_values)

                for cms in sample.get("expect_cms_absent", []):
                    self.assertNotIn(cms, cms_values)

                for version_text in sample.get("expect_version_contains", []):
                    self.assertIn(version_text, result.get("version", ""))

                if "expect_confidence_min" in sample:
                    self.assertGreaterEqual(result["confidence"], sample["expect_confidence_min"])
                if "expect_confidence_max" in sample:
                    self.assertLessEqual(result["confidence"], sample["expect_confidence_max"])

                for cms, bounds in sample.get("expect_cms_confidence", {}).items():
                    self.assertIn(cms, details_by_cms)
                    if "min" in bounds:
                        self.assertGreaterEqual(details_by_cms[cms]["confidence"], bounds["min"])
                    if "max" in bounds:
                        self.assertLessEqual(details_by_cms[cms]["confidence"], bounds["max"])


if __name__ == '__main__':
    unittest.main()
