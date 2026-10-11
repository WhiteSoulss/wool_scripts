# Pinterest 客户端兼容性诊断

当前去广告版来自实际 Loon 原版两条 JQ，并已通过源码语义对照。用户复测仍出现
Pinterest “Something’s a little off” 页面。现有日志记录了 api.pinterest.com 的
MITM via HTTP/1.1 和旧连接复用，未包含请求完整 URL、响应状态、响应体或 JQ 执行结果。
HTTP/1.1 本身不是错误；这些证据尚不能确诊 HTTP/2、证书或 JQ 为根因。

这些测试配置独立存放在 diagnostics，不加入去广告目录、软件支持列表或总合集。
它们不包含请求/响应改写、Script、Rule、证书替换或远程资源。关闭后撤销模块覆盖。

## 第一步：只解密，保持当前协议

1. 暂时关闭 Pinterest 去广告独立模块，以及含 Pinterest 规则的 blockAds 总合集。
   若主配置或其他模块也有 Pinterest 改写，须暂时关闭那些改写，才能做单独比较。
2. 安装并只启用 [测试 A](https://raw.githubusercontent.com/WhiteSoulss/wool_scripts/main/Surge/diagnostics/Pinterest/mitm-only.sgmodule)。
   主配置原有代理策略、MITM 证书和其他设置保持一致。
3. 重新连接 Surge，并彻底退出后再打开 Pinterest，使旧 HTTP 连接不再参与此次比较。
4. 记录首页是否恢复，以及 api.pinterest.com 请求的完整 URL、HTTP 状态和响应记录。

A 恢复访问时，说明在此次仅解密条件下可以加载，接下来读取真实响应再判断 JQ 改写；
不能仅凭这一结果断言某个 JSON 字段或 Surge JQ 实现有问题。
如果同时关闭了总合集，结果也不能把总合集所有其他规则的影响完全排除。

## 第二步：A 仍失败时只切换解密协议

关闭 A 后，改为只启用 [测试 B](https://raw.githubusercontent.com/WhiteSoulss/wool_scripts/main/Surge/diagnostics/Pinterest/mitm-h2-only.sgmodule)，
再次重新连接 Surge并重开 Pinterest。B 与 A 仅相差 MITM h2=true 覆盖。
该参数是全局 MITM 设置，并非 api.pinterest.com 专属；测试结束须关闭 B。

B 恢复访问会支持 HTTP/2 解密兼容性方向；它仍没有 JQ，不能证明去广告版已修复。
A、B 都失败时，应读取实际请求/响应和连接错误，不把 JQ 作为已经确认的根因。
比较期间不得同时启用 A/B，也不要自行取消服务器证书验证来掩盖问题。

## 资料与限制

- 主机依据为实际 LPX 的 hostname=api.pinterest.com，原版 SHA256：
  905ce81e2a26cb5421219b8f9009502d7c014291b3b3a5532e13dd6ad3a01d95。
- [Surge MITM 参数](https://manual.nssurge.com/http/mitm.html)：h2 开启 HTTP/2 解密，默认 false。
- [Surge iOS 5.2.0 修复记录](https://kb.nssurge.com/surge-knowledge-base/release-notes/surge-ios)：
  修复模块不能配置 MITM h2 参数的问题。
- 未操作用户设备，没有通过 VPS 检查声称客户端访问或去广告已验证。
- 正式模块和总合集当前保持原版两条 JQ；这些诊断配置不会自动替换或启用正式模块。
