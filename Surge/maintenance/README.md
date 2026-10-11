# Surge 每日维护

目标仓库为 WhiteSoulss/wool_scripts，执行时区 Asia/Shanghai，每天 08:00。
用户后来明确暂不迁入云端；当前仍由既有本地每日任务在 107.174.244.24
服务器下载、构建和验证。Mac 只用于编辑及 SSH，不操作代理客户端或浏览器。
ad.quietvales.com 保持退役，不创建重复任务。

## 启动检查

先读取当前服务器 MANUAL_DAILY_UPDATES.md 和本仓库 Surge/AGENTS.md。
服务器需要 Python 3、Node、jq 和 git；用既有授权 GitHub 连接器发布。

在仓库根目录运行：

```bash
python3 Surge/maintenance/verify.py
python3 Surge/maintenance/check_updates.py --work-dir /tmp/wool-review-UNIQUE
```

第二个命令的工作目录必须不存在并位于仓库之外。将 UNIQUE 换成此次运行的唯一标识。
程序只归档原版和依赖，比较当前精确字节与既有基线，并输出 pending-review.json。
它不会转换、更新已批准模块或批准新哈希。下载失败返回非零状态。
已记录的 HTTP 404 在状态不变时不视为新的下载失败；恢复下载也必须复核。
所有变化和无法确认的分类都需阅读实际内容后处理。

## 可携带资料

- `Surge/Kelee-review/loon-original/`：106 项已合入去广告插件的实际 LPX 原版。
- `Surge/Kelee-review/native-ledger.json`：仅这 106 项的历史动作账本。
- `Surge/Kelee-review/ad-selection.json`：当前补充选择及去广告分类基线。
- `Surge/Kelee-review/catalog-ad-baseline.json`：全站去广告目录的变化比较基线，不代表全部已加入。
- `Surge/Kelee-review/dependency-baseline.json`：30 个原版依赖及已知缺失状态。
- `Surge/Kelee-review/fmz-baseline.json`：固定 fmz 提交的 Surge/README 文件树。
- 原版依赖的完整可用字节已保存在现有 `Surge/Script/Kelee/` 和 `Surge/Resource/Kelee/`。
  原始依赖与兼容适配稿必须分别识别，不能用适配稿冒充原版。

历史稿件含辅助工具生成的基础，不是这次从零手写。旧资料只携带既有审核记录及核验
原版/依赖字节，不产生新的语义批准。每项新的 LPX、脚本、JQ 或模板变化必须
读实际差异，再手动改写和审核原生 Surge。完全禁止 ScriptHub、通用自动转换器、
仅更新哈希接受变化，或绕过 pending-review。

`verify.py` 保留 68 个 JSON 删除/替换行为样例、联掌门户原生 JQ 与 URL 范围样例、腾讯表单兼容脚本样例、JQ 编译和
脚本语法/资源/哈希/合集冲突检查，并验证独立模块的一一对应和去广告选择门禁。
它不会改写 verification.json；可用 `--report` 指定仓库外报告路径。
通过基线检查不代表变化已被审核，也不代表客户端去广告已经验证。

## 每日工作

1. 从最新 main 开始，读取 Surge/AGENTS.md、TASK_PROMPT.md 和现有复核资料。
2. 验证当前基线，独立归档目录、LPX 和全部已选依赖，记录实际差异和下载状态。
3. 固定 fmz 最新提交，同步 Surge 目录及 README-RULE.md，保留独立 upstream 基线，
   不能覆盖总模块或删除个人补充；对并发修改重新比较，不能强推。
4. 比较 fmz 软件表、别名和实际模块能力，补充缺失的可莉去广告功能。只有规则集、
   空壳标题或部分端点覆盖不能当作完整支持；不要把配置项数等同于 App 数。
5. 逐项阅读变化并手写 Surge，保留独立模块及总模块，复核脚本重名、重叠匹配、
   覆写顺序、MITM、端口、参数和资源可用性。
6. 为实际变化编写有意义的样例并验证，更新行为记录及精确哈希。未完成的项目
   保留旧版并提交明确的 pending-review 证据，不发布待审核模块。
7. 原子提交已审核内容至 main，验证公开链接。无变化不创建空提交。

不要运行默认的 fmz mergeSurge.js 直接覆盖总模块。它仅聚合 fmz 原拆分目录，
不能保留当前的可莉、HTTPDNS 和微博补充。包装器也不能替代语义审核。

## 原生 JQ 要求

Loon 原版的 response.json.delete、replace、jq 等内联 JSON 动作手动适配为
Surge 原生 http-response-jq；请求 JSON 动作用 http-request-jq。逐项保留表达式、
请求/响应阶段、URL 范围和大小写标志，不为这些动作新增 JS 包装。
原版本来调用 JS 或处理非 JSON 内容的功能仍保留相应脚本，不能凭空改成 JQ。
verify.py 从实际归档 LPX 检查全部 JSON 动作在独立模块和总模块的原生 JQ 对应。

原生 Body Rewrite 需要 Surge iOS 5.14+ / Mac 5.9+；响应大小上限为
iOS 1 MB、Mac 10 MB，超限保持原响应。阅读并记录这些平台限制。
Pinterest 已获用户报告可访问，当前工作保留其生产配置。

## 日程与通知

沿用既有本地每日任务，不进行云端迁移、不创建重复任务、不恢复网站。
无变化或无可操作事项时保持安静；仅通知有意义的发布、失败或需要用户处理的事项。

## 配置分隔与引号修正

2026-10-11 修正百度网页 Script 的逗号量词与 fmz Crunchyroll 的正文引号字段，
见 Kelee-review/config-syntax-review-20261011.json。原版与依赖没有变化；
保留精确解码后的匹配、脚本和正文替换语义。Crunchyroll 属于个人上游修正，
同步拆分目录、重建总模块时必须保留；不改写固定 fmz upstream 原版。
新版上游变化仍需阅读，不能机械替换或仅批准新哈希。

verify.py 调用 test_config_syntax.py，对总模块和所有补充模块先做参数分隔、
引号与字段结构检查，再用 ICU 编译实际分割后的 Script/Body Rewrite 正则，
并复现两条旧错误及验证原版行为。它是文档语法模型，不是 Surge 客户端解析器。
双引号内的引号/反斜线转义按官方 iOS 5.21.0+ / Mac 6.8.0+ 文档处理；
原生 JQ 本身的历史最低版本不等于这些新引号转义的版本要求。
服务器测试需要系统 ICU（Ubuntu 的 libicu）。

## 全段语法复查

2026-10-11 按用户要求复查全部 106 个 Loon 补充及总模块；
106 个独立转换模块未发现新的语法错误，原版、依赖和生产字节全部保持。
总模块另有继承自 fmz 原版的 3 条 JSON Mock 引号和参数头漏声明问题，已手动
补齐，见 Kelee-review/module-syntax-review-20261011.json。
参数默认值来自固定 fmz 拆分模块；网易云 partQ 的 DT:true 与 partW 的 DT:false
分别绑定 fmz_netease_q_DT / fmz_netease_w_DT，避免同名参数吞掉不同默认值。
其他旧版脚本的单层花括号字符串保持原样；语法复查不等于脚本运行兼容性验证。

verify.py 加入 audit_module_syntax.py，按实际配置字段检查 Rule/嵌套逻辑、
URL/Header/Body Rewrite、Map Local 类型/状态码/头部/JSON/Base64、
Script 类型/布尔/数字/资源路径、已声明的参数，以及 General/MITM 域名与端口；
用 ICU 编译解码后的正则，用 jq 编译解码后的表达式。
检查器识别 IPv6 字面地址及带端口的方括号形式，不把 IPv6 尾段误当端口。
保留 3 个原版 Mock 引号缺陷复现、原样 JSON 样例及全部参数来源/默认值核对。

每日同步保留这 3 个 fmz 拆分模块的个人引号修正及总模块的参数补齐/命名隔离，
同时保留此前 Crunchyroll 引号修正；不改写固定 upstream 原版。
新上游有变化仍逐项阅读实际内容，不从报告自动批准。
