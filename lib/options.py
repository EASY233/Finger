#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from lib.runtime import create_runtime_config


class OptionError(ValueError):
    pass


def _read_lines(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.strip()]


def _clean_target(value):
    for token in ['"', '“', '”', '\\', "'"]:
        value = value.replace(token, "")
    return value.strip()


def normalize_urls(values):
    results = []
    for value in values:
        url = _clean_target(value)
        if not url:
            continue
        if url.startswith('http://') or url.startswith('https://'):
            results.append(url)
        else:
            results.append("http://" + url)
            results.append("https://" + url)
    return results


def expand_ip_targets(values):
    targets = []
    for value in values:
        item = value.strip()
        if not item:
            continue
        if "-" in item and "/" not in item:
            start, end = [ip_num(x) for x in item.split('-')]
            targets.extend(num_ip(num) for num in range(start, end + 1) if num & 0xff)
        else:
            targets.append(item)
    return targets


def collect_url_targets(args):
    values = []
    if args.url:
        values.append(args.url)
    if args.file:
        if not os.path.exists(args.file):
            raise OptionError("File {0} is not find".format(args.file))
        values.extend(_read_lines(args.file))
    return normalize_urls(values)


def collect_ip_targets(args):
    values = []
    if args.ip:
        values.append(args.ip)
    if args.ipfile:
        if not os.path.exists(args.ipfile):
            raise OptionError("File {0} is not find".format(args.ipfile))
        values.extend(_read_lines(args.ipfile))
    try:
        return expand_ip_targets(values)
    except Exception as exc:
        raise OptionError(
            "IP格式有误，正确格式为192.168.10.1,192.168.10.1/24 or 192.168.10.10-192.168.10.50"
        ) from exc


def resolve_api_provider(args):
    if args.fofa and args.quake:
        raise OptionError("FOFA 和 Quake 只能选择一个")
    if args.fofa:
        return "fofa"
    if args.quake:
        return "quake"
    return ""


def build_run_config(args, root_dir=None):
    output_format = args.output.lower().strip()
    if output_format not in ("json", "xlsx"):
        raise OptionError("Ouput args is error,eg(json,xlsx default:xlsx)")

    api_provider = resolve_api_provider(args)
    urls = collect_url_targets(args)
    ip_targets = collect_ip_targets(args)

    if api_provider and not args.api_query and not ip_targets:
        raise OptionError("使用 FOFA/Quake 时必须提供 --query，除非通过 -i/-if 使用 FOFA 的 IP 资产采集")
    if args.api_size is not None and args.api_size <= 0:
        raise OptionError("--size 必须为正整数")

    return create_runtime_config(
        root_dir=root_dir,
        output_format=output_format,
        proxy_url=args.proxy.strip(),
        cdn=args.cdn,
        geo=args.geo,
        audit=args.audit,
        api_provider=api_provider,
        api_query=args.api_query.strip(),
        api_size=args.api_size,
        urls=tuple(urls),
        ip_targets=tuple(ip_targets),
    )


class initoptions:
    """兼容旧接口；新代码请直接使用 build_run_config。"""

    def __init__(self, args, root_dir=None):
        self.config = build_run_config(args, root_dir=root_dir)


def ip_num(ip):
    item = [int(x) for x in ip.split('.')]
    return item[0] << 24 | item[1] << 16 | item[2] << 8 | item[3]


def num_ip(num):
    return '%s.%s.%s.%s' % ((num & 0xff000000) >> 24,
                            (num & 0x00ff0000) >> 16,
                            (num & 0x0000ff00) >> 8,
                            num & 0x000000ff)
