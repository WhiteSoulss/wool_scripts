每天北京时间 08:00（Asia/Shanghai）维护 WhiteSoulss/wool_scripts/main。
用户已授权每日更新及发布，后来明确暂不迁入云端；所有下载、构建和验证在
107.174.244.24 服务器完成，用户电脑只用于编辑与既有 SSH 连接。
ad.quietvales.com 保持退役；不操作用户 Surge、Loon、Stash 或浏览器，
不恢复网站，不改动共享 nginx router 配置。

先读取服务器 MANUAL_DAILY_UPDATES.md、仓库 Surge/AGENTS.md、
Surge/maintenance/README.md、Surge/Kelee-review/manifest.json、
native-ledger.json、dependency-baseline.json、fmz-baseline.json 和现有
pending-review。固定最新 main，保留并发用户修改。

运行 python3 Surge/maintenance/verify.py 检查现有审核基线。运行
python3 Surge/maintenance/check_updates.py --work-dir /tmp/wool-review-此次唯一标识，
归档 hub.kelee.one/list.json、当前实际 LPX、所有原版依赖，读取报告及实际差异。
检查器只归档和报告，不能转换或批准。固定 fmz200/wool_scripts 最新提交，
同步其 Surge 目录和 README-RULE.md，保留独立 upstream 基线及个人补充，不能
用原版 blockAds.module 或默认 mergeSurge.js 覆盖增强总模块。

可莉补充严格限去广告插件及必需脚本/JQ/模板依赖。核对实时目录“去广告”标签
和插件实际用途，并结合 fmz 软件表、别名及实际原生 Surge 动作判断缺失能力。
排除只有规则集、空壳模块以及签到、节点检测、订阅/配置管理、跳转、搜索和
资源转换插件。此限制不删除 fmz 原有其他目录文件。

新增或变化必须读取实际 Loon 原版、脚本/JQ/模板差异与旧 Surge 配置，逐项手动
编写并复核原生 Surge 语义。完全禁止 ScriptHub、通用自动转换器、自动批准或
仅改哈希接受变化。旧稿含辅助工具生成的基础，不得称为全部从零手写；只有
原版及所有依赖精确字节一致时才可复用未变的已审核配置。
保留作者、非空 name/desc、参数默认值、请求/响应体要求、头部、端口、MITM。
原版内联 JSON/JQ 动作手动使用 Surge 原生 http-response-jq / http-request-jq，
保留原表达式、阶段、URL 范围及标志；不要新增 JS 包装来实现 JSON 删除、替换或 JQ。
原版本来调用脚本或处理非 JSON 内容的功能仍按实际行为保留相应脚本。
遵守原生 JQ 的最低版本和响应大小限制；verify.py 必须从实际 LPX 验证对应关系。
Pinterest 用户已报告可访问，保留当前生产规则，不重新发布历史 JS 适配。

保留哈啰缺失脚本警告及合集禁用触发器、腾讯视频旧客户端限制与已审核兼容稿、
Quark Scanking MITM、联掌门户自定义端口/HTTP 引擎、直播吧配置净化冲突修正，
除非读过并验证的新证据支持修改。更新 Surge/module/Kelee/ 独立模块及必要
镜像资源，把已审核补充合入同一个 Surge/module/blockAds.module。保持署名，
精确行去重、Script 键唯一、MITM 合并，审查重叠模式和请求/响应脚本执行顺序。

通过相关语义样例、JQ 编译、JS 语法（不运行不可信上游脚本）、元数据/参数/端口/
资源哈希和链接检查后，写清实际行为、来源和精确哈希，更新审核账本和 baseline。
基线校验通过不是新的语义批准；不能宣称服务器检查证明客户端去广告生效。
下载失败、未知动作或验证失败时保留受影响项目上次已审核版本，将 pending-review
证据持久化到仓库，不发布未审核稿；不要只依赖 VPS 工作目录保存。

用既有授权 GitHub 连接器或 git 权限发布，取得最新 main 头并以非强制快进/
expected_sha 提交，不能覆盖并发修改。发布后验证总模块、独立模块和资源公开
raw 链接及字节。无变化不生成空提交。无变化或无可操作事项保持安静，只在
有意义更新、失败或需要用户处理时通知。

保留 Kelee-review/config-syntax-review-20261011.json 的百度参数引号与 Crunchyroll 原生正文引号修正，后者为个人 fmz 上游覆盖。同步拆分模块及重建合集时先阅读新上游再保留修正；不改写固定 upstream 原版。verify.py 包含实际配置字段分割后的 ICU 正则检查，不只编译账本里的完整正则。双引号转义需遵守已记录的 Surge 版本要求。

保留 module-syntax-review-20261011.json 记录的三个 fmz JSON Mock 引号修正与总模块的原版参数默认值；网易云 Q/W 的 DT 默认值分别命名，不能合并成一个开关。verify.py 调用全段语法检查器，覆盖本地响应、嵌套规则、参数声明和主机端口；通过报告不能替代原版变化的人工语义复核。


## Tinder 独立补充（2026-10-11）

用户指定从 https://loon-plugins.vercel.app 加入 Tinder 去广告。
这是 devchristian1337 的单独来源，不是可莉目录项，不得放入可莉选择基线冒充可莉插件。
读取 Surge/Extra-review/manifest.json、tinder-review-20261011.json、实际归档 LPX 和
原版 JS；保留 Surge/module/Extra/Tinder_remove_ads.sgmodule 与同一总合集中的三条
原生 JQ、唯一 MITM api.gotinder.com。原版根据 URL 是否包含 /v2/meta 决定处理方式，
特殊 profile 查询也必须保留相同行为。SDK 和服务端会员权限字段不修改。

check_updates.py 每日同时归档 Tinder 最新 LPX 和 JS，对照其精确哈希；这段 JS 是语义
依赖，即使客户端使用原生 JQ，也不能漏查。checker 只报差异、不转换、不批准。
变化时先逐行阅读原版再手动复核，不能只更新 hash。fmz 同步、重建合集须保留这个来源、
作者、独立模块和行为，不能覆盖增强总模块。其他来源的插件未经用户授权不批量加入。
verify.py 调用 test_tinder.py，核对实际配置、URL 分派、类型边界、广告开关与原版的
JSON 语义、奖励视频/权限字段保留及合集端点重叠；完整语法门禁也包含独立 Tinder。
语义参照 JS 已全文审阅，无 I/O，仅在隔离 Node vm 里使用模拟数据比较，不暴露网络、
文件、进程或定时器。服务器验证仍不代表客户端实测。


## 用户最新要求：fmz 独立微博单独安装（2026-10-12）

Surge/module/weibo.module 继续按 fmz 原版独立同步和保留；不得再把它作为附加组件
合入 Surge/module/blockAds.module。用户选择另行导入。读取 manifest.json 的
independent_bundle_exclusions 和 weibo-standalone-review-20261012.json。
已移出全部独立来源动作及其不共用的 MITM 项；不得恢复 fmzweibo_ 脚本块、
独立 weibo.module 的脚本/规则、*.weibo.cn、*.weibo.com 或 weibo.com 三项来源。
现有可莉微博轻享版及其具体域名照常保留；fmz 原总模块自身范围照常同步。
未来若原版或其他组件新增共享动作，必须阅读真实来源并复核优先级，不能通过
移除这条排除门禁或只更新哈希强行接受。verify.py 会检查独立微博未重新合入。
这项用户要求取代历史文档/包装器中“额外合入 fmz 独立微博”的安排。


## 用户响应体内存限制（2026-10-12）

用户要求降低 Surge iOS 响应体处理的内存压力。可莉 12 个独立模块的 29 条响应脚本，
及总合集中的对应 28 条有效脚本与 1 条已注释哈啰引用，将 max-size=-1 手动改为
max-size=1048576（1 MiB）。脚本内容、URL 匹配、阶段、requires-body、作者、参数、
MITM、原生 JQ 和其他动作保持原样。超限响应原样放行，该次脚本去广告不执行；
该参数限制解压后响应缓冲，不是引擎总内存上限，也不是响应体截断。

读取 Kelee-review/response-body-limit-review-20261012.json 与 manifest 的
response_body_policy。每日同步和重建保留这项个人限制，不能从历史模板恢复 -1，
也不能自动扩大上限。新上游动作或依赖变化仍需阅读并逐项复核；若大响应确实需要
特殊预算，先记录待复核事项。test_response_limits.py 已接入 verify.py，
检查有效响应脚本的 iOS 默认或显式上限不超过 1 MiB，并核对独立/合集相同字段。
原生 JQ 沿用 Surge 自身的响应限制，不添加 max-size 到 Body Rewrite。
fmz 原版脚本、独立微博、B 站和单独的 AllInOne 已使用 iOS 默认上限，本次未改。
