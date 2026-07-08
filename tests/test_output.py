#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import tempfile
import unittest
import zipfile

from lib.output import Output
from lib.resultio import collect_default_creds, load_default_creds, save_results
from lib.runtime import RuntimePaths


class OutputSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        cls.paths = RuntimePaths.from_root(root)

    def test_xlsx_export_does_not_emit_formulas_for_remote_content(self):
        results = [{
            "url": "http://example.test",
            "title": "=cmd|'/C calc'!A0",
            "cms": "@danger",
            "confidence": 95,
            "version": "-",
            "Server": "nginx",
            "status": 200,
            "size": 10,
            "ip": "127.0.0.1",
            "address": "",
            "isp": "",
        }]

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = save_results(results, tmpdir, "xlsx", timestamp="20240101010101", library_dir=self.paths.library_dir)
            with zipfile.ZipFile(filepath) as workbook:
                sheet_xml = workbook.read('xl/worksheets/sheet1.xml').decode('utf-8')

            self.assertNotIn('<f>', sheet_xml)

    def test_output_accepts_explicit_results_without_global_state(self):
        results = [{
            "url": "http://local.test",
            "title": "Local",
            "cms": "-",
            "confidence": 0,
            "version": "-",
            "Server": "",
            "status": 200,
            "size": 0,
            "ip": "",
            "address": "",
            "isp": "",
        }]

        with tempfile.TemporaryDirectory() as tmpdir:
            output = Output(results=results, fmt="json", output_dir=tmpdir, library_dir=self.paths.library_dir)
            self.assertTrue(os.path.exists(output.path))

    def test_default_creds_are_merged_across_cms_aliases(self):
        default_creds, creds_orig_keys = load_default_creds(self.paths.library_dir)
        creds = collect_default_creds("GitLab,Nexus Repository Manager,ArgoCD", default_creds, creds_orig_keys)

        joined = " | ".join(creds)
        self.assertIn("root/5iveL!fe", joined)
        self.assertIn("admin/nexus", joined)
        self.assertIn("admin/admin123", joined)


if __name__ == '__main__':
    unittest.main()
