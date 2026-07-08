# 修复路线图与代码级改造清单

## Phase 1: 先修高风险缺陷

- [x] 统一结果导出实现，消除 `lib/finger.py` 与 `lib/output.py` 的双份导出逻辑
- [x] 修复 xlsx 公式注入风险，强制按字符串写入远端返回内容
- [x] 修复审计 CSV 注入与转义问题，改为标准库 `csv.writer`
- [x] 修复 `regula` 多关键词只生效首条正则的问题

## Phase 2: 收敛主链路状态管理

- [x] CLI 主链路改为显式传递 `results`，不再依赖 `Webinfo.result` 作为唯一数据源
- [x] `IpAttributable` 支持对显式传入结果集做归属地填充
- [x] `Output` 支持显式传入结果集和格式，保留旧接口兼容

## Phase 3: 提高可维护性与可验证性

- [x] 规则库读取改为显式读取 `fingerprint` 键
- [x] 收敛关键吞错点，保留必要告警
- [x] 增加最小回归测试，覆盖规则语义与导出安全
- [x] 建立规则库样本回归集，覆盖 body/header/url/faviconhash/expected_server 场景
- [x] 为扫描失败增加结构化错误分类输出
- [x] 继续清理 `lib/req.py` 与 `Identify.run()` 的全局状态路径

## Phase 4: 架构收敛与真实页面回归

- [x] 将 FOFA / Quake 的交互式输入改为参数和运行时配置驱动
- [x] 扫描器增加结构化错误分类与失败结果输出
- [x] 增加 400 plain HTTP request was sent to HTTPS port 自动协议重试
- [x] 增加同源 JS/meta refresh 跳转跟进
- [x] 默认始终拉取 favicon，避免高置信页面漏掉 hash 证据
- [x] 将规则样本回归扩展到真实页面夹具
- [x] 覆盖高价值产品和高误报页面：Swagger、Grafana、Harbor、Portainer、Nexus、Druid、Gitea、Prometheus、Sonatype 营销页、Example Domain
- [x] 规则库别名碎片归一化，审计别名碎片降为 0
- [x] 收窄 Swagger 等路径型噪声规则
- [x] 版本提取覆盖补强，修复 Grafana 伪版本提取
- [x] 默认口令库补强并按别名合并输出

## V6.1 剩余非阻断项

- [ ] 继续逐步减少“URL 路径型规则偏多”的中风险审计项
- [ ] 持续用真实页面样本压低规则库长尾误报
- [ ] 对更多高价值产品补充真实版本提取样本
