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
