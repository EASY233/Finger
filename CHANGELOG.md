# Changelog

## V6.1

V6.1 是一次架构收敛、扫描链路修复和规则质量治理版本。

### 架构与状态管理

| 问题 | 修改 |
|------|------|
| CLI、库模式、旧 `lib/req.py` 各自维护状态和输出逻辑 | 新增 `lib/app.py`、`lib/runtime.py`、`lib/resultio.py`，统一应用编排、运行时配置和导出 |
| `Identify.run()` 会写全局结果，库模式不够可控 | `Identify.match()` / `match_details()` 保持纯函数式返回，`run()` 支持显式 `result_store` |
| 导出逻辑分散且 xlsx/csv 存在公式注入风险 | 统一导出实现，xlsx 强制字符串写入，CSV 使用标准库转义 |
| 同秒多次输出可能覆盖文件 | 输出文件名加入毫秒，重名时自动追加后缀 |

### 扫描链路

| 问题 | 修改 |
|------|------|
| HTTP 请求发到 HTTPS 端口时直接失败 | 检测 `plain HTTP request was sent to HTTPS port` 并自动升级 HTTPS 重试 |
| 同时扫描 HTTP/HTTPS 时升级请求可能重复 | 记录调度集合，避免重复请求已调度的 HTTPS 目标 |
| JS/meta refresh 跳转页识别不到最终产品 | 支持同源前端跳转跟进，限制最大深度并拒绝跨源跳转 |
| `stream=True` 下 `apparent_encoding` 可能提前消费响应体 | 先读取响应体并写回 `_content`，再判断编码，避免标题/正文为空 |
| 大响应体直接丢弃导致漏标题和首屏特征 | 改为读取前 128KB，仍保留 favicon 拉取 |
| 高置信页面跳过 favicon 会漏掉 hash 证据 | 默认始终拉取 favicon |
| 请求错误只表现为空结果 | 输出 `error_type` / `error_detail`，区分超时、代理、SSL、连接、解析等错误 |

### 指纹识别与置信度

| 问题 | 修改 |
|------|------|
| 正则规则多关键词只处理首条 | `regula` 规则支持完整 `and/or` 多正则匹配 |
| keyword 大小写敏感导致漏报 | keyword 匹配改为大小写不敏感 |
| 同产品多条证据只取最高一条 | 同产品证据聚合，跨位置证据提高置信度 |
| 多产品共用一个总置信度，不利于人工判断误报 | JSON 增加 `fingerprints` 明细，CLI 显示 `产品[置信度]`，xlsx 增加 `FingerprintDetails` |
| 支撑服务和真实产品混在一起容易误判 | Nginx/Apache/Cloudflare/Intercom/cdnjs 等作为陪衬服务降权显示，不再压掉真实产品 |
| Grafana 版本正则过宽，可能提取伪版本 | 修复多捕获组取值逻辑并收窄 Grafana 版本正则 |

### 规则库治理

| 问题 | 修改 |
|------|------|
| 同产品多展示名造成别名碎片 | 增加别名归一化和展示名优选 |
| Swagger 纯路径规则制造低置信噪声 | 删除/收窄重复和纯路径 Swagger 规则，保留页面证据 |
| `Access-Control-Allow-Methods`、`jsessionid`、`.action/.do` 等泛化规则误报 | 删除相关过宽规则 |
| `0example`、`HttpOnly` 属于占位/属性规则，不是产品指纹 | 删除对应规则 |
| 裸 `GitLab`、`theme`、`platform`、`datalayer`、`x-ua-compatible`、`FrontEnd`、`Isite` 等词级规则误报 | 收窄为专用证据或删除 |
| Sonatype 营销页被误报为 Nexus/GitLab/Sangfor/VMware | 增加真实页面回归并收紧相关规则 |
| 默认口令按展示名碎片重复或漏合并 | 默认口令按归一化 CMS 名合并输出 |

### 测试与审计

| 问题 | 修改 |
|------|------|
| 只有合成样本，不足以覆盖真实页面误报 | 增加真实页面夹具，覆盖 Swagger、Grafana、Harbor、Portainer、Nexus、Druid、Gitea、Prometheus、Sonatype 等 |
| 规则质量只能靠人工看扫描结果 | `RuleAudit` 增加静态规则审计、版本正则审计、路径型规则提示 |
| 回归缺少扫描行为覆盖 | 新增协议升级、前端跳转、favicon、错误分类、大响应体、输出安全等测试 |

### 验证

```bash
python -m unittest discover -s tests -v
```

当前测试集：41 条，通过。
