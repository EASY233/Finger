<h1 align="center">
  <br>
  <img src="http://picbed.easy233.top//imgQQ%E6%88%AA%E5%9B%BE20210603085018.png" width="400px" alt="Finger">
</h1>

<h4 align="center">一款红队在大量的资产中存活探测与重点攻击系统指纹探测工具</h4>

<p align="center">
  <a href="#开始">开始</a> •
  <a href="#更新日志">更新日志</a> •
  <a href="#支持选项">支持选项</a> •
  <a href="#指纹识别规则">指纹识别规则</a> •
  <a href="#v61-核心功能">V6.1 核心功能</a> •
  <a href="#感谢列表">感谢列表</a>
</p>
<p align="center">
    <img src="https://img.shields.io/badge/Author-EASY233-da282a">
    <img src="https://img.shields.io/badge/Language-Python%203.7+-da282a"></a>
    <img src="https://img.shields.io/badge/Version-V6.1-da282a">
</p>

---

## 开始

Finger定位于一款红队在大量的资产中存活探测与重点攻击系统指纹探测工具。在面临大量资产时候Finger可以快速从中查找出重点攻击系统协助我们快速展开渗透。早有前辈贡献出优秀的作品[EHole(棱洞)3.0 重构版-红队重点攻击系统指纹探测工具](https://github.com/EdgeSecurityTeam/EHole)，但是该项目代码不开源我想做出一些修改也没有办法，所以决定使用其指纹库自行开发一个趁手的工具。


---

## 更新日志

### V6.1 更新

- **架构统一**：新增 `lib/app.py`、`lib/runtime.py`、`lib/resultio.py`，统一扫描、配置、导出入口。`req.py` 改为复用 `Finger` 主引擎
- **库模式纯净化**：`Identify.match()` / `match_details()` 只返回结果，`run()` 支持显式 `result_store`，避免隐式全局状态
- **证据聚合**：同产品多证据保留 `evidence_count`、`locations`、`methods`，跨位置证据自动提高置信度
- **置信度内联显示**：CLI 输出 `产品[置信度]`，xlsx 新增 `FingerprintDetails` 列
- **强制 favicon**：默认始终拉取 favicon，不因高置信跳过 hash 证据
- **HTTPS 自动重试**：`400 plain HTTP request was sent to HTTPS port` 自动升级为 HTTPS
- **前端跳转跟进**：支持同源 JS/meta refresh 跳转跟进，限制深度并阻止跨源跳转
- **编码修复**：`stream=True` 下先读取响应体再设置编码，避免标题/正文为空
- **大小写不敏感**：keyword 匹配改为大小写不敏感，`Swagger UI` / `swagger ui` 统一识别
- **大响应体优化**：读取前 128KB，保留标题和首屏特征
- **输出文件名优化**：加入毫秒时间戳，重名自动追加后缀
- **别名归一化**：增加展示名优选和 CMS 名别名归一化，消除碎片
- **规则质量修复**：收紧宽规则
- **版本提取修正**：支持多捕获组选择第一个有效组，修正版本正则
- **规则审计增强**：`RuleAudit` 增加静态规则审计、版本规则审计、路径型规则提示
- **回归测试**：新增 41 条测试 + `tests/fixtures/pages/` 真实页面夹具，覆盖 Swagger、Grafana、Harbor、Portainer、Nexus、Druid、Gitea、Prometheus 等

### V6.0 版本大更新

- **规则库扩充**：合并 17 个指纹库来源，254K 原始规则去重清洗 → **16,938 条规则，覆盖 11,993 产品**
- **智能置信度**：重写为算法自动计算，根据匹配位置/命中率/关键词质量自动分级，xlsx 输出红/黄色着色
- **URL 路径匹配**：新增 `location: url`（130条规则），匹配页面 URL 而非 body 中的链接，与 dirsearch 联动
- **Server 版本提取**：自动提取 nginx/Apache/IIS/PHP/Virata-EmWeb 等版本号
- **硬件型号提取**：支持 HP 打印机/海康摄像头/Dell 服务器/Canon 等设备型号自动提取
- **默认口令标注**：xlsx 新增 `DefaultCreds` 列，覆盖 1,756 产品，带 `[产品] 口令` 来源标注
- **规则质量审计**：`--audit` 四维自动检测（Server 多样性/404 命中率/命中率异常/关键词质量）
- **架构统一**：CLI + 库模式共用 `Finger` 类
- **质量修复**：删除 32 个通用误报关键词（`body`/`/login`/`download`/`self.location` 等），favicon SSL 修复
- **性能优化**：默认超时 10→5s，扫描速度提升 ~40%
- **增强 60+ 产品类别**：OA/ERP/打印机/安全设备/AI 平台/物联网/视频监控 等
- **默认口令**：1,756 产品默认口令（来源：手工整理 + CMS 名提取 + DefaultCreds-cheat-sheet + ObserverWard FingerprintHub）
- **MD5 faviconhash 支持**：新增 MD5 十六进制 favicon 哈希匹配，兼容 ObserverWard 指纹格式
- **来源标注**：DefaultCreds 列带 `[产品]` 标注，精确匹配 + 模糊回退双重保障

### V5.1 更新

- 优化输出
- 修复通过fofa api查询web信息不全的bug

### V5.0 版本大更新

- 取消html输出格式，默认使用xlsx格式保存数据，目前只支持xlsx和json保存数据
- 增加自动获取IP，识别CDN，获取ip归属地功能。
- 增加调用fofa，360quake的api来搜集资产，并自动进行存活探测以及指纹识别(⚠️**注意Finger调用api的时候仅获取web资产**)。
- 修复若干bug

### 2022-3-18 更新

- Finger会把所有请求失败的资产同样保存下来，并记录下请求失败原因方便手动检查
- 对输入目标进行了简单的去除特殊字符处理
- 修复部分小bug

---

## 支持选项

### 下载使用

Finger使用python3.7+开发全平台支持,可以使用下面命令下载使用:

```bash
git clone https://github.com/EASY233/Finger.git
cd Finger
pip3 install -r requirements.txt
python3 Finger.py -h
```

### 参数说明

Finger追求极简命令参数只有以下几个:

| 参数 | 说明 |
|------|------|
| `-u URL` | 对单个URL进行指纹识别 |
| `-f FILE` | 对指定文件中的url进行批量指纹识别 |
| `-i IP` | 对ip进行fofa数据查询采集其web资产 |
| `-if FILE` | 对指定文件中的ip批量调用fofa进行数据查询采集其web资产 |
| `-fofa` | 调用fofa api进行资产收集 |
| `-quake` | 调用360 quake进行资产收集 |
| `-o FORMAT` | 指定输出方式，支持 json/xlsx（默认xlsx） |
| `--proxy URL` | 代理地址 (http://127.0.0.1:8080 或 socks5://...) |
| `--cdn` | 启用CDN检测（默认关闭） |
| `--geo` | 启用IP归属地查询（默认关闭） |
| `--audit` | 🆕 启用规则质量审计 |

Finger支持的URL格式有:`www.baidu.com`、`127.0.0.1`、`http://www.baidu.com`，但是前两种不推荐使用。Finger会在URL处理阶段自动为其添加`http://`和`https://`

Finger支持的IP格式有单个IP格式（192.168.10.1）、IP段（192.168.10.1/24）、某一小段IP（192.168.10.10-192.168.10.50），满足日常使用的所有需求。Finger会首先通过Fofa采集IP的web资产，然后对其进行存活探测以及系统指纹探测。

### 配置说明

编辑 `config/settings.py` 进行配置:

```python
# 设置线程数，默认30
threads = 30

# HTTP请求超时（秒），默认5
timeout = 5

# 设置Fofa key信息
Fofa_email = ""
Fofa_key = ""
# 普通会员API查询数据是前100，高级会员是前10000条根据自已的实际情况进行调整。
Fofa_Size = 100

# 设置360quake key信息，每月能免费查询3000条记录
QuakeKey = ""

# 是否选择在线更新指纹库，默认关闭
FingerPrint_Update = False
```

---

## 指纹识别规则

Finger的指纹规则学习之[EHole(棱洞)3.0 重构版-红队重点攻击系统指纹探测工具](https://github.com/EdgeSecurityTeam/EHole)，并进行了优化。规则格式如下:

### 规则字段

| 字段 | 必填 | 说明 |
|------|:---:|------|
| `cms` | ✅ | 系统/产品名称 |
| `method` | ✅ | 识别方式: `keyword` / `faviconhash` / `regula` |
| `location` | ✅ | 匹配位置: `title` / `header` / `body` / `url` |
| `keyword` | ✅ | 关键词列表（favicon hash / 正则 / 文本） |
| `logic` | — | 匹配逻辑: `and`（默认，全部命中）/ `or`（任一命中） |
| `version_regex` | — | 版本号提取正则，如 `Nginx/([\\d.]+)` |
| `model_regex` | — | 设备型号提取正则，如 `DS-2\\w{2}\\d{4}\\w*[\\-\\w/]*` |
| `expected_server` | — | 预期 Server 头列表，不匹配时自动降权 |

### 示例

```json
{
    "cms": "Shiro",
    "method": "keyword",
    "location": "header",
    "keyword": ["rememberMe=", "=deleteMe", "shiroCookie"],
    "logic": "or"
}
```

```json
{
    "cms": "HP-LaserJet-Printer",
    "method": "keyword",
    "location": "title",
    "keyword": ["HP LaserJet", "HP Color LaserJet"],
    "logic": "or",
    "model_regex": "HP\\s+(LaserJet|Color LaserJet)\\s+(?:MFP\\s+|Pro\\s+)?[\\w\\d]+",
    "expected_server": ["Virata-EmWeb"]
}
```

### 识别方式

| method | 说明 | 精度 | 示例 |
|--------|------|------|------|
| `keyword` | 关键词匹配，支持 AND/OR 逻辑 | title/header 精准，body 取决于关键词质量 | `"keyword": ["Swagger UI"]` |
| `faviconhash` | favicon 图标 hash 匹配（EHole + FOFA 双 hash 兼容） | **极高**（密码学哈希，几乎零误报） | `"keyword": ["81586312"]` |
| `regula` | 正则表达式匹配 | 取决于正则质量 | `"keyword": ["Apache/([\\d.]+)"]` |

### 匹配位置

| location | 说明 |
|----------|------|
| `title` | 页面 `<title>` 标签内容（最可靠的位置） |
| `header` | HTTP 响应头（多格式兼容：`Server: nginx` / `(Server: nginx`） |
| `url` | 🆕 URL 路径匹配（与 dirsearch 联动，精确度等同 title） |
| `body` | 页面 HTML 全文（最不可靠，需谨慎使用关键词） |

---

## V6.1 核心功能

### 智能置信度算法

置信度不再由规则预设 `confidence` 字段，而是从匹配过程自动推导：

| 维度 | 规则 |
|------|------|
| faviconhash 命中 | → 直接 **95 分**（密码学哈希） |
| title 多关键词 AND | → **80-95 分** |
| URL 路径匹配 | → **80-85 分** |
| body OR 多关键词命中 | → **55-70 分** |
| body OR 单短通用词 | → **30-50 分**（大概率 FP） |
| Server 头不匹配预期 | → **-20 分** |

> xlsx 输出：≥80 **红色**（高置信度），50-79 **黄色**（中置信度），<50 无色（低置信度）

### 输出列说明

| 列 | 内容 |
|------|------|
| Url | 目标 URL |
| Title | 页面标题 |
| CMS | 识别到的产品指纹（置信度着色） |
| MaxConfidence | 所有指纹中最高的置信度分数 (0-100) |
| FingerprintDetails | 每个指纹的独立置信度和版本，如 `Grafana(88) Grafana 13.1.0` |
| Version | 产品版本号 / Server 版本 |
| Server | 原始 Server 响应头 |
| Status | HTTP 状态码 |
| Size | 响应体大小 |
| IP | IP 地址 |
| Address | IP 归属地（需 --geo） |
| ISP | 运营商（需 --geo） |
| DefaultCreds | 🆕 默认口令，带来源标注（如 `[Nacos] nacos/nacos`, `[Tomcat] tomcat/tomcat`） |

JSON 输出会保留兼容字段 `cms` / `confidence`，同时新增 `fingerprints` 数组，逐项记录 `cms`、`confidence`、`version`、`evidence_count`、`locations`、`methods`。

### 规则质量审计

```bash
python Finger.py -f targets.txt --audit
```

扫描完成后自动检测可疑规则（Server 多样性过高、404 命中率过高、命中率异常占比、高危短通用词），输出 `*_audit.csv`。

### 库模式

```python
from lib.finger import Finger

f = Finger(threads=30)
results = f.scan(['http://target1.com', 'http://target2.com'])
for r in results:
    print(f"{r['url']} → {r['cms']} [{r['confidence']}]")
```

### 架构

```
Finger.py              CLI入口 → FingerApplication
lib/app.py             应用编排：参数、资产收集、扫描、审计、输出
lib/finger.py          扫描引擎（CLI + 库模式共用）
lib/identify.py        指纹匹配、证据聚合、版本/型号提取
lib/resultio.py        json/xlsx/csv 安全导出
lib/output.py          输出兼容层
lib/audit.py           规则质量审计
lib/rule_heuristics.py 规则启发式、别名归一化、风险标记
lib/match_filters.py   陪衬服务过滤
lib/runtime.py         路径和运行时配置
lib/options.py         URL/IP 目标预处理
config/settings.py     配置文件
library/               指纹库 + 默认口令库 + CDN/IP 数据
```

### 发包行为

- 常规目标默认 2 次请求：主页 + favicon
- 遇到 HTTP 发到 HTTPS 端口的 400 页面，会自动升级 HTTPS 重试
- 遇到同源 JS/meta refresh 跳转页，会跟进最终页面，限制最大跳转深度
- 请求头包含 `Sec-Fetch-*` 系列，与 Chrome 浏览器一致
- UA 池为 Chrome 131 / Firefox 135
- `verify=False` 跳过 SSL 证书验证（主页和 favicon）
- 不发送 Cookie

---

## 感谢列表
在开发过程中参考学习了非常多前辈们的优秀开源项目，特此感谢!

[Glass(镜) V2.0-剑客到刺客的蜕变](https://github.com/s7ckTeam/Glass)

[EHole(棱洞)3.0 重构版-红队重点攻击系统指纹探测工具](https://github.com/EdgeSecurityTeam/EHole)

[WebAliveScan](https://github.com/broken5/WebAliveScan)

[AUTO-EARN](https://github.com/Echocipher/AUTO-EARN)

[Ip2region](https://github.com/lionsoul2014/ip2region)

[OneForAll](https://github.com/shmilylty/OneForAll)

[ObserverWard](https://github.com/0x727/ObserverWard)

[FingerprintHub](https://github.com/0x727/FingerprintHub)

[DefaultCreds-cheat-sheet](https://github.com/ihebski/DefaultCreds-cheat-sheet)

感谢**Ti0s** 提供的建议

![Stargazers over time](https://starchart.cc/EASY233/Finger.svg)
