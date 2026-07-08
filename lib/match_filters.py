#!/usr/bin/env python
# -*- coding: utf-8 -*-


GENERIC_WEB_SERVER_EVIDENCE = {
    "Nginx": ("welcome to nginx", "<title>nginx", "nginx"),
    "Apache": ("apache installation", "apache is functioning normally", "test page for apache"),
    "OpenResty": ("openresty", "thank you for flying openresty"),
    "lighttpd": ("lighttpd", "powered by lighttpd"),
    "IIS": ("welcome.png", "<title>iis", "internet information services"),
    "PHP": ("phpinfo()", "php version", "php credits"),
}


def apply_generic_service_filters(matches, page_data):
    content = ' '.join([
        str(page_data.get("title", "")),
        str(page_data.get("body", "")),
    ]).lower()
    non_service_cms = {
        item["cms"] for item in matches
        if item["cms"] not in GENERIC_WEB_SERVER_EVIDENCE
    }

    filtered = []
    for item in matches:
        if item["cms"] == "登录页面" and non_service_cms - {"登录页面"}:
            continue
        evidence = GENERIC_WEB_SERVER_EVIDENCE.get(item["cms"])
        if evidence and not any(token in content for token in evidence):
            continue
        filtered.append(item)
    return filtered


def filter_matches(matches, page_data):
    filtered = apply_generic_service_filters(matches, page_data)
    return filtered
