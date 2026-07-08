#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest
from concurrent.futures import ThreadPoolExecutor

from lib.identify import Identify
from lib.runtime import RuntimePaths


def build_datas(body):
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


class IdentifyRegulaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        cls.paths = RuntimePaths.from_root(root)

    def test_regula_rule_requires_all_keywords_by_default(self):
        identify = Identify(library_dir=self.paths.library_dir)
        identify.obj = [{
            "cms": "LoginRegex",
            "method": "regula",
            "location": "body",
            "keyword": ["<input.*pass", "<input.*user"],
        }]
        identify._prepare_app()

        only_password = build_datas('<input name="pass" type="password">')
        self.assertEqual('', identify.match(only_password)["cms"])

        both_fields = build_datas('<input name="user"><input name="pass" type="password">')
        self.assertEqual('LoginRegex', identify.match(both_fields)["cms"])

    def test_regula_rule_supports_or_logic(self):
        identify = Identify(library_dir=self.paths.library_dir)
        identify.obj = [{
            "cms": "RegexOr",
            "method": "regula",
            "location": "body",
            "logic": "or",
            "keyword": ["foo", "bar"],
        }]
        identify._prepare_app()

        result = identify.match(build_datas('this page contains bar only'))
        self.assertEqual('RegexOr', result["cms"])

    def test_keyword_matching_is_case_insensitive(self):
        identify = Identify(library_dir=self.paths.library_dir)
        identify.obj = [{
            "cms": "CaseProduct",
            "method": "keyword",
            "location": "title",
            "keyword": ["swagger ui"],
        }]
        identify._prepare_app()

        result = identify.match({**build_datas(''), "title": "Swagger UI"})

        self.assertEqual('CaseProduct', result["cms"])

    def test_identify_match_is_thread_safe(self):
        identify = Identify(library_dir=self.paths.library_dir)
        identify.obj = [
            {
                "cms": "RuleA",
                "method": "keyword",
                "location": "body",
                "keyword": ["only-a"],
            },
            {
                "cms": "RuleB",
                "method": "keyword",
                "location": "body",
                "keyword": ["only-b"],
            },
        ]
        identify._prepare_app()

        def run_match(body):
            return identify.match(build_datas(body))["cms"]

        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(run_match, ["only-a", "only-b"] * 50))

        self.assertEqual({"RuleA", "RuleB"}, set(results))

    def test_path_only_url_rule_is_heavily_downgraded(self):
        identify = Identify(library_dir=self.paths.library_dir)
        identify.obj = [{
            "cms": "PathOnlyProduct",
            "method": "keyword",
            "location": "url",
            "keyword": ["/console"],
        }]
        identify._prepare_app()

        result = identify.match({
            **build_datas(''),
            "url": "http://example.test/console",
        })

        self.assertEqual('PathOnlyProduct', result["cms"])
        self.assertLessEqual(result["confidence"], 45)

    def test_duplicate_cms_aliases_are_canonicalized(self):
        identify = Identify(library_dir=self.paths.library_dir)
        identify.obj = [
            {
                "cms": "Grafana",
                "method": "keyword",
                "location": "title",
                "keyword": ["Grafana"],
            },
            {
                "cms": "grafana",
                "method": "keyword",
                "location": "body",
                "keyword": ["grafana-app"],
            },
        ]
        identify._prepare_app()

        result = identify.match({
            **build_datas('grafana-app'),
            "title": "Grafana",
        })

        self.assertEqual('Grafana', result["cms"])

    def test_explicit_alias_map_is_canonicalized(self):
        identify = Identify(library_dir=self.paths.library_dir)
        identify.obj = [
            {
                "cms": "nexus",
                "method": "keyword",
                "location": "body",
                "keyword": ["nexus repository manager"],
            },
            {
                "cms": "Sonatype-Nexus",
                "method": "keyword",
                "location": "title",
                "keyword": ["Nexus Repository Manager"],
            },
        ]
        identify._prepare_app()

        result = identify.match({
            **build_datas('nexus repository manager'),
            "title": "Nexus Repository Manager",
        })

        self.assertEqual('Nexus Repository Manager', result["cms"])

    def test_druid_alias_maps_to_alibaba_druid_not_apache_druid(self):
        identify = Identify(library_dir=self.paths.library_dir)
        identify.obj = [
            {
                "cms": "druid",
                "method": "keyword",
                "location": "body",
                "keyword": ["<title>druid monitor</title>"],
            },
            {
                "cms": "Apache-Druid",
                "method": "keyword",
                "location": "body",
                "keyword": ["<title>Apache Druid</title>"],
            },
        ]
        identify._prepare_app()

        result = identify.match({
            **build_datas('<title>druid monitor</title>'),
            "title": "druid monitor",
        })

        self.assertEqual('Alibaba-Druid', result["cms"])

    def test_multi_evidence_same_cms_is_aggregated(self):
        identify = Identify(library_dir=self.paths.library_dir)
        identify.obj = [
            {
                "cms": "AggregateApp",
                "method": "keyword",
                "location": "title",
                "keyword": ["Aggregate Console"],
            },
            {
                "cms": "AggregateApp",
                "method": "keyword",
                "location": "body",
                "keyword": ["aggregate-app"],
            },
        ]
        identify._prepare_app()

        result = identify.match({
            **build_datas('aggregate-app'),
            "title": "Aggregate Console",
        })
        details = identify.match_details({
            **build_datas('aggregate-app'),
            "title": "Aggregate Console",
        })

        self.assertEqual('AggregateApp', result["cms"])
        self.assertGreaterEqual(result["confidence"], 85)
        self.assertEqual(1, len(details))
        self.assertEqual(2, details[0]["evidence_count"])

    def test_risky_path_only_evidence_does_not_get_aggregation_bonus(self):
        identify = Identify(library_dir=self.paths.library_dir)
        identify.obj = [
            {
                "cms": "RiskyPathApp",
                "method": "keyword",
                "location": "url",
                "keyword": ["/console"],
            },
            {
                "cms": "RiskyPathApp",
                "method": "keyword",
                "location": "url",
                "keyword": ["/console/"],
            },
        ]
        identify._prepare_app()

        result = identify.match({
            **build_datas(''),
            "url": "http://example.test/console/",
        })

        self.assertEqual('RiskyPathApp', result["cms"])
        self.assertLessEqual(result["confidence"], 45)

    def test_supporting_service_with_page_evidence_is_retained_alongside_product(self):
        identify = Identify(library_dir=self.paths.library_dir)
        identify.obj = [
            {
                "cms": "Nginx",
                "method": "keyword",
                "location": "header",
                "keyword": ["Server: nginx/1.24.0"],
            },
            {
                "cms": "PortalApp",
                "method": "keyword",
                "location": "title",
                "keyword": ["Portal Console"],
            },
        ]
        identify._prepare_app()

        result = identify.match({
            **build_datas('welcome to nginx'),
            "title": "Portal Console",
            "header": {"Server": "nginx/1.24.0"},
            "Server": "nginx/1.24.0",
        })

        self.assertIn('PortalApp', result["cms"])
        self.assertIn('Nginx', result["cms"])

    def test_url_path_rules_do_not_match_hostname_substrings(self):
        identify = Identify(library_dir=self.paths.library_dir)
        identify.obj = [{
            "cms": "CasLikePath",
            "method": "keyword",
            "location": "url",
            "keyword": ["/cas"],
        }]
        identify._prepare_app()

        result = identify.match({
            **build_datas(''),
            "url": "https://casdoor.example.test/",
        })

        self.assertEqual('', result["cms"])

    def test_swagger_aliases_are_canonicalized_to_swagger_ui(self):
        identify = Identify(library_dir=self.paths.library_dir)
        identify.obj = [
            {
                "cms": "Swagger",
                "method": "keyword",
                "location": "body",
                "keyword": ["swagger-ui-bundle.js"],
            },
            {
                "cms": "Swagger UI",
                "method": "keyword",
                "location": "title",
                "keyword": ["Swagger UI"],
            },
        ]
        identify._prepare_app()

        result = identify.match({
            **build_datas('<script src="swagger-ui-bundle.js"></script>'),
            "title": "Swagger UI",
        })

        self.assertEqual('Swagger UI', result["cms"])

    def test_access_control_header_alone_does_not_identify_product(self):
        identify = Identify(library_dir=self.paths.library_dir)
        result = identify.match({
            **build_datas(''),
            "header": {
                "Server": "nginx",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            },
            "Server": "nginx",
        })

        self.assertNotIn('Access-Control', result["cms"])


if __name__ == '__main__':
    unittest.main()
