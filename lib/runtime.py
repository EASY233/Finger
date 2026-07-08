#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dataclasses import dataclass, field, replace
import os

from config import settings


def default_root_dir():
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def build_proxies(proxy_url):
    if not proxy_url:
        return None
    return {"http": proxy_url, "https": proxy_url}


@dataclass(frozen=True)
class RuntimePaths:
    root_dir: str
    output_dir: str
    config_dir: str
    library_dir: str

    @classmethod
    def from_root(cls, root_dir):
        root_dir = os.path.abspath(root_dir)
        return cls(
            root_dir=root_dir,
            output_dir=os.path.join(root_dir, 'output'),
            config_dir=os.path.join(root_dir, 'config'),
            library_dir=os.path.join(root_dir, 'library'),
        )

    @classmethod
    def default(cls):
        return cls.from_root(default_root_dir())


@dataclass(frozen=True)
class RuntimeConfig:
    paths: RuntimePaths
    threads: int
    timeout: int
    output_format: str = 'xlsx'
    proxy_url: str = ''
    cdn: bool = False
    geo: bool = False
    audit: bool = False
    user_agents: tuple[str, ...] = field(default_factory=tuple)
    fofa_email: str = ''
    fofa_key: str = ''
    fofa_size: int = 100
    quake_key: str = ''
    fingerprint_update: bool = False
    api_provider: str = ''
    api_query: str = ''
    api_size: int | None = None
    urls: tuple[str, ...] = field(default_factory=tuple)
    ip_targets: tuple[str, ...] = field(default_factory=tuple)

    def proxies(self):
        return build_proxies(self.proxy_url)

    def with_urls(self, urls):
        return replace(self, urls=tuple(urls))


def create_runtime_config(root_dir=None, **overrides):
    paths = RuntimePaths.from_root(root_dir or default_root_dir())
    defaults = {
        "paths": paths,
        "threads": settings.threads,
        "timeout": settings.timeout,
        "output_format": "xlsx",
        "proxy_url": "",
        "cdn": False,
        "geo": False,
        "audit": False,
        "user_agents": tuple(settings.user_agents),
        "fofa_email": settings.Fofa_email,
        "fofa_key": settings.Fofa_key,
        "fofa_size": settings.Fofa_Size,
        "quake_key": settings.QuakeKey,
        "fingerprint_update": settings.FingerPrint_Update,
        "api_provider": "",
        "api_query": "",
        "api_size": None,
        "urls": tuple(),
        "ip_targets": tuple(),
    }
    defaults.update(overrides)
    return RuntimeConfig(**defaults)
