#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re


CMS_KEY_ALIASES = {
    'apacheairflow': 'apache-airflow',
    'apahce-airflow': 'apache-airflow',
    'apachedruid': 'apache-druid',
    'alibabadruid': 'alibaba-druid',
    'alibaba-druid连接池': 'alibaba-druid',
    'alibaba-nacos': 'nacos',
    'druid': 'alibaba-druid',
    'alertmanager': 'alertmanager',
    'argocd': 'argocd',
    'casdoor': 'casdoor',
    'consulbyhashicorp': 'consul-hashicorp',
    'gitlab': 'gitlab',
    'gitlabci': 'gitlabci',
    'gitlabci': 'gitlabci',
    'apache-nifi': 'apache-nifi',
    'cockpit': 'cockpit',
    'jupyter': 'jupyter notebook',
    'jupyter-notebook': 'jupyter notebook',
    'prometheus server': 'prometheus',
    'prometheus time series collection and processing server': 'prometheus',
    'apache tomcat': 'apache-tomcat',
    'calibre': 'calibre',
    'cpanel': 'cpanel',
    'dedecms': 'dedecms',
    'emby': 'emby',
    'gitlab': 'gitlab',
    'gitlabci': 'gitlabci',
    'grafana': 'grafana',
    'huawei-ssl-vpn': 'huawei-ssl-vpn',
    'jboss': 'jboss',
    'jeecgboot': 'jeecgboot',
    'jetty': 'jetty',
    'jfrog-artifactory': 'jfrog-artifactory',
    'jpress': 'jpress',
    'jumpserver堡垒机': 'jumpserver堡垒机',
    'memcached': 'memcached',
    'metabase': 'metabase',
    'netdata': 'netdata',
    'o2oa': 'o2oa',
    'roundcube': 'roundcube',
    'ruoyi-system': 'ruoyi-system',
    'sangfor-data-center': 'sangfor-data-center',
    'seafile': 'seafile',
    'sonicwall-ssl-vpn': 'sonicwall-ssl-vpn',
    'thinkphp': 'thinkphp',
    'vmware-vsphere': 'vmware-vsphere',
    'yonyou-grp-u8': 'yonyou-grp-u8',
    'zentao-system': 'zentao-system',
    'zabbix': 'zabbix',
    'swagger ui': 'swagger-ui',
    'swagger': 'swagger-ui',
    'alibaba-fastjson': 'alibaba-fastjson',
    'nexus': 'nexus repository manager',
    'sonatype nexus repository manager': 'nexus repository manager',
    'sonatype-nexus': 'nexus repository manager',
}

CMS_DISPLAY_NAME_OVERRIDES = {
    'alertmanager': 'Alertmanager',
    'apache-airflow': 'Apache-Airflow',
    'apache-druid': 'Apache-Druid',
    'apache-nifi': 'Apache-NiFi',
    'alibaba-fastjson': 'Alibaba-Fastjson',
    'alibaba-druid': 'Alibaba-Druid',
    'argocd': 'ArgoCD',
    'calibre': 'Calibre',
    'casdoor': 'Casdoor',
    'consul-hashicorp': 'Consul-HashiCorp',
    'cockpit': 'Cockpit',
    'cpanel': 'cPanel',
    'dedecms': 'DedeCMS',
    'emby': 'Emby',
    'grafana': 'Grafana',
    'huawei-ssl-vpn': 'HuaWei-SSL-VPN',
    'jboss': 'JBoss',
    'jeecgboot': 'JeecgBoot',
    'jetty': 'Jetty',
    'jfrog-artifactory': 'JFrog-Artifactory',
    'jpress': 'JPress',
    'jumpserver堡垒机': 'JumpServer堡垒机',
    'memcached': 'Memcached',
    'metabase': 'Metabase',
    'nacos': 'Nacos',
    'netdata': 'NetData',
    'o2oa': 'O2OA',
    'gitlab': 'GitLab',
    'gitlabci': 'GitLabCI',
    'jupyter notebook': 'Jupyter Notebook',
    'nexus repository manager': 'Nexus Repository Manager',
    'apache-tomcat': 'Apache-Tomcat',
    'prometheus': 'Prometheus',
    'roundcube': 'RoundCube',
    'ruoyi-system': 'ruoyi-System',
    'sangfor-data-center': 'Sangfor-Data-Center',
    'seafile': 'Seafile',
    'sonicwall-ssl-vpn': 'SonicWALL-SSL-VPN',
    'swagger-ui': 'Swagger UI',
    'thinkphp': 'ThinkPHP',
    'uptime-kuma': 'Uptime-Kuma',
    'vmware-vsphere': 'VMware-vSphere',
    'yonyou-grp-u8': 'Yonyou-GRP-U8',
    'zentao-system': 'Zentao-System',
    'zabbix': 'Zabbix',
    'calibre-web': 'Calibre-Web',
}


SUPPORTING_SERVICE_CMS = {
    'apache',
    'apache-web-server',
    'nginx',
    'openresty',
    'lighttpd',
    'iis',
    'microsoft iis',
    'php',
    'php-fpm',
    'asp',
    'asp.net',
    'jetty',
    'cowboy',
    'hudson',
    'apache-coyote',
    'apache tomcat',
    'tengine',
    'http-proxy',
    'alt-svc',
    'cdnjs',
    'google-webmaster-platform',
    'hotjar',
    'intercom',
    'linkedin',
    'typekit',
    'aws cloudfront',
    'fastly cdn',
    'akamai',
    'akamaighost',
    'aliyuncdn',
    'ali-cdn',
    'google cloud cdn',
}

RISKY_HEADER_PREFIXES = (
    'server:',
    'set-cookie',
    'x-',
    'proxy-agent:',
    'www-authenticate:',
    'realm=',
)

COOKIE_TOKENS = (
    'session',
    'jsessionid',
    'phpsessid',
    'sid=',
    'token',
    'visitor',
)


def normalize_cms_key(name):
    key = re.sub(r'\s+', ' ', str(name or '').strip()).lower()
    return CMS_KEY_ALIASES.get(key, key)


def prefer_display_name(names):
    names = [str(name).strip() for name in names if str(name).strip()]
    if not names:
        return ''
    normalized = normalize_cms_key(names[0])
    if normalized in CMS_DISPLAY_NAME_OVERRIDES:
        return CMS_DISPLAY_NAME_OVERRIDES[normalized]
    return sorted(
        names,
        key=lambda value: (
            -sum(1 for char in value if char.isupper()),
            value.islower(),
            -len(value),
            value,
        ),
    )[0]


def is_supporting_service_cms(name):
    return normalize_cms_key(name) in SUPPORTING_SERVICE_CMS


def is_serverish_header_keyword(keyword):
    keyword = str(keyword or '').strip().lower()
    return keyword.startswith(RISKY_HEADER_PREFIXES)


def is_cookie_like_keyword(keyword):
    keyword = str(keyword or '').strip().lower()
    return any(token in keyword for token in COOKIE_TOKENS)


def is_path_only_url_rule(rule):
    if rule.get('method') != 'keyword' or rule.get('location') != 'url':
        return False
    keywords = rule.get('keyword', [])
    return bool(keywords) and all(str(keyword).startswith('/') for keyword in keywords)


def is_short_title_rule(rule):
    if rule.get('method') != 'keyword' or rule.get('location') != 'title':
        return False
    keywords = rule.get('keyword', [])
    return len(keywords) == 1 and len(str(keywords[0]).strip()) <= 12


def is_risky_single_header_rule(rule):
    if rule.get('method') != 'keyword' or rule.get('location') != 'header':
        return False
    keywords = rule.get('keyword', [])
    if len(keywords) != 1:
        return False
    keyword = str(keywords[0])
    return is_serverish_header_keyword(keyword) or is_cookie_like_keyword(keyword)


def classify_rule(rule):
    flags = set()
    if is_path_only_url_rule(rule):
        flags.add('path_only_url')
    if is_risky_single_header_rule(rule):
        flags.add('risky_single_header')
    if is_short_title_rule(rule):
        flags.add('short_title')
    if is_supporting_service_cms(rule.get('cms', '')):
        flags.add('supporting_service')
    return frozenset(flags)
