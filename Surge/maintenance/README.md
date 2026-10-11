# Codex Cloud 每日维护

用户已授权将 Surge GitHub 每日更新迁入 Codex Cloud。目标仓库为
WhiteSoulss/wool_scripts，执行时区 Asia/Shanghai，每天 08:00。
迁移后的工作不依赖用户 Mac、SSH 私钥、VPS 原版归档或已退役的网站。

## 启动检查

选择已发布、具有当前仓库访问权限的云端环境。先按照适用的 cloud runtime
技能核实真实网络/凭据 readiness，不以 draft 设置代替观测。
需要 Python 3、Node 和 jq，以及 git。已测试的 cloud onboarding 环境具备这些工具。
公共来源需要 github.com、api.github.com、raw.githubusercontent.com、
codeload.github.com、hub.kelee.one、kelee.one；新增实际依赖的来源另行检查。
现有 Git 读取权限不等于发布权限，发布前核实既有认证可写，不复制 root 私钥。

在仓库根目录运行：

```bash
python3 Surge/maintenance/verify.py
python3 Surge/maintenance/check_updates.py --work-dir /tmp/wool-review-UNIQUE
```

第二个命令的工作目录必须不存在并位于仓库之外。将 UNIQUE 换成此次运行的唯一标识。
程序只归档原版和依赖，比较当前精确字节与既有基线，并输出 pending-review.json。
它不会转换、更新已批准模块或批准新哈希。下载失败返回非零状态。
已记录的三个 HTTP 404 在状态不变时不视为新的下载失败；恢复下载也必须复核。
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

历史稿件含辅助工具生成的基础，不是这次从零手写。迁移只携带旧审核记录及核验
原版/依赖字节，不产生新的语义批准。每项新的 LPX、脚本、JQ 或模板变化必须
读实际差异，再手动改写和审核原生 Surge。完全禁止 ScriptHub、通用自动转换器、
仅更新哈希接受变化，或绕过 pending-review。

`verify.py` 保留既有 67 个 JSON 行为样例、两项兼容脚本行为样例、JQ 编译和
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

## 日程与通知

使用真正的 Codex/ChatGPT hosted 云端定时任务，绑定此已发布环境和 GitHub 权限，
时区为 Asia/Shanghai，每天 08:00，指令使用 TASK_PROMPT.md 的全文。
环境安装、草稿保存或 VM cron 都不能冒充日程已生效。
须确认实际 task ID、启用状态、环境、时区、下次运行时间并完成首次维护验证。
新云任务跑通后才停用原本的本地任务，避免无人维护或重复发布。
无变化或无可操作事项时保持安静；仅通知有意义的发布、失败或需要用户处理的事项。
