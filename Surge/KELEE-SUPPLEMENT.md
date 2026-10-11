# fmz200 ＋ 可莉补充

[总模块](https://raw.githubusercontent.com/WhiteSoulss/wool_scripts/main/Surge/module/blockAds.module) · [可莉独立模块](module/Kelee/) · [复核记录](Kelee-review/manifest.json)

总模块继续使用 `Surge/module/blockAds.module`。fmz200 原始文件另存于 `Surge/upstream/fmz200/blockAds.module`；其他 fmz Surge 文件保留原结构。

本次以 fmz200 提交 `5d5f63fcf98bc69d5f8f1b1bae6f86a01ee4bb97` 和 README-RULE 的 733 行支持列表核对。新增 106 个独立配置（105 个标题，挖财原版有两份不同端点配置）。这是配置数，不等于新增软件数或客户端实测成功数。

补充配置复用此前已复核的原生 Surge 适配稿（历史基础稿含辅助工具生成配置），重新下载当前实际 Loon 原版和依赖核对精确哈希。没有使用 ScriptHub。保留原作者、非空名称和描述；所需脚本及 DREAME 资源保存至本仓库。

同应用别名、App 与小程序、普通版与轻享版按实际对象区分。36氪和哈啰的 fmz 项是空文件；腾讯视频虽列在表中，其独立 Surge 文件没有实际动作，因此补入原版规则。微博和 HTTPDNS 已有 fmz 原生模块，直接合入它们，不重复转换。签到、节点检测、订阅工具、搜索和链接跳转功能未混入去广告合集。

需要 Surge iOS 5.14+ / Mac 5.9+ 才支持原生 JQ。已做 VPS 静态和语义样例检查，未操作用户设备，不能据此宣称客户端广告已消除。安装总模块后请勿再同时启用重叠的独立去广告模块。

已知限制：哈啰原版唯一脚本 HTTP 404，独立配置保留 URL 并标注，合集将其触发器注释。茶颜悦色脚本引用的 cyys1.jpg 也为 HTTP 404。夸克扫描王已按真实请求补齐 MITM。直播吧合并时移除 fmz 抢先拒绝整个配置接口的旧规则，保留可莉逐字段净化。

## Pinterest 按原版重写（2026-10-11）

用户确认停用此前适配后恢复访问，并明确要求保留去广告功能、按原版重新转换。
已逐条阅读实际 LPX 及用户提供的两条规则，手写为 Surge 的两条原生
http-response-jq，独立模块与总合集采用相同规则，MITM 只补 api.pinterest.com。
原版表达式完整保留：只保留 is_promoted 为布尔 false 或字符串 "false" 的项目，
保留其他顶层字段与所保留项目的顺序。两种 false 之外的项目按原版删除。

上一版 JavaScript 的 true 黑名单与原版 false 白名单并不等价；已删除该适配脚本及引用。
历史记录仍保留在 Git。没有增加原版之外的 HTTP 状态/数据形状过滤或传输参数覆盖。
需要 Surge iOS 5.14+ / Mac 5.9+，并使用客户端已信任的 MITM 证书。

这次验证证明转换语义和匹配范围与原版一致，不能证明客户端访问故障已修复。
具体故障层次仍未确证，等待用户设备复测；未自动操作用户代理客户端。
见 [当前复核记录](Kelee-review/pinterest-reconversion-20261011.json)、
[客户端待确认记录](Kelee-review/pinterest-pending-review.json) 与
[实际原版对照样例](maintenance/test_pinterest.js)。

## 原生 JQ 复核（2026-10-11）

已核对全部 106 项可莉补充模块的实际归档原版。原有 133 条内联 JSON 动作已用
原生 JQ；联掌门户剩余一条 response.json.delete("value.config") 现手写为
http-response-jq 的 del(.value.config)，同时更新独立模块和总模块，删除旧 JS 适配。
全部 134 条内联 JSON 动作都有原生 JQ 对应。原版调用 JS 的功能继续保留脚本。

联掌门户保留全部十条 Map Local、6025/9220 端口、5090 HTTP 引擎和 MITM。
原生 Body Rewrite 有平台响应大小上限：iOS 1 MB、Mac 10 MB，超限保持原响应。
每日维护已加入此语法要求和检查。Pinterest 用户最后报告「可以了」，
本次保留其生产配置；服务器验证仍不等于客户端去广告验证。
详见 [复核记录](Kelee-review/native-jq-audit-20261011.json)。

## 补充配置

| 名称 | 独立模块 | 原作者 |
| --- | --- | --- |
| 5EPlay去广告 | [5EPlay_remove_ads.sgmodule](module/Kelee/5EPlay_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 36氪去广告 | [36Kr_remove_ads.sgmodule](module/Kelee/36Kr_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 123云盘去广告 | [123NetWorkDisk_remove_ads.sgmodule](module/Kelee/123NetWorkDisk_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 360摄像机去广告 | [360SmartCamera_remove_ads.sgmodule](module/Kelee/360SmartCamera_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 360智慧生活去广告 | [SafetyHome_remove_ads.sgmodule](module/Kelee/SafetyHome_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| B612咔叽去广告 | [SnowCamera_remove_ads.sgmodule](module/Kelee/SnowCamera_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| CC直播去广告 | [CCLive_remove_ads.sgmodule](module/Kelee/CCLive_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| DJ多多去广告 | [DjDuoDuo_remove_ads.sgmodule](module/Kelee/DjDuoDuo_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| DREAME去广告 | [DREAME_remove_ads.sgmodule](module/Kelee/DREAME_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| ECOVACS HOME去广告 | [EcovacsHome_remove_ads.sgmodule](module/Kelee/EcovacsHome_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| Foodie去广告 | [Foodie_remove_ads.sgmodule](module/Kelee/Foodie_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| Hong Kong Toolbar去广告 | [HongKongToolbar_remove_ads.sgmodule](module/Kelee/HongKongToolbar_remove_ads.sgmodule) | C.Hiang |
| Jump去广告 | [Jump_remove_ads.sgmodule](module/Kelee/Jump_remove_ads.sgmodule) | MoonYuki[https://github.com/MoonYuki] |
| KOOK去广告 | [KOOK_remove_ads.sgmodule](module/Kelee/KOOK_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| OKOK去广告 | [OKOK_remove_ads.sgmodule](module/Kelee/OKOK_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| PICOOC去广告 | [PICOOC_remove_ads.sgmodule](module/Kelee/PICOOC_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| Pinterest去广告 | [Pinterest_remove_ads.sgmodule](module/Kelee/Pinterest_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| ReelShort去广告 | [ReelShort_remove_ads.sgmodule](module/Kelee/ReelShort_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| Roborock去广告 | [Roborock_remove_ads.sgmodule](module/Kelee/Roborock_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| RQrun去广告 | [RQrun_remove_ads.sgmodule](module/Kelee/RQrun_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| Sofascore去广告 | [Sofascore_remove_ads.sgmodule](module/Kelee/Sofascore_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| TeraBox去广告 | [TeraBox_remove_ads.sgmodule](module/Kelee/TeraBox_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| Uki去广告 | [Uki_remove_ads.sgmodule](module/Kelee/Uki_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| WakeUp课程表去广告 | [WakeupSchedule_remove_ads.sgmodule](module/Kelee/WakeupSchedule_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| YY语音去广告 | [YYVoiceTool_remove_ads.sgmodule](module/Kelee/YYVoiceTool_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 百度网页去广告 | [BaiduSearchWebpage_remove_ads.sgmodule](module/Kelee/BaiduSearchWebpage_remove_ads.sgmodule) | Keywos[https://github.com/Keywos] |
| 比心去广告 | [Bixin_remove_ads.sgmodule](module/Kelee/Bixin_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 测测去广告 | [Cece_remove_ads.sgmodule](module/Kelee/Cece_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 成分喵去广告 | [ChengFenMiao_remove_ads.sgmodule](module/Kelee/ChengFenMiao_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 创维智慧云去广告 | [SkyworthDigitalPicamera_remove_ads.sgmodule](module/Kelee/SkyworthDigitalPicamera_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 触站去广告 | [Chuzhan_remove_ads.sgmodule](module/Kelee/Chuzhan_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 磁力宅播放器去广告 | [XFuse_remove_ads.sgmodule](module/Kelee/XFuse_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 大姨妈月经期助手去广告 | [Dayima_remove_ads.sgmodule](module/Kelee/Dayima_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 得间小说去广告 | [iReaderDejian_remove_ads.sgmodule](module/Kelee/iReaderDejian_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 豆瓣阅读去广告 | [DoubanRead_remove_ads.sgmodule](module/Kelee/DoubanRead_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 堆糖去广告 | [DuiTang_remove_ads.sgmodule](module/Kelee/DuiTang_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 多屏互动去广告 | [TCLnScreen_remove_ads.sgmodule](module/Kelee/TCLnScreen_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 风鸟去广告 | [RiskBird_remove_ads.sgmodule](module/Kelee/RiskBird_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 纷玩岛去广告 | [LiveLab_remove_ads.sgmodule](module/Kelee/LiveLab_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 海雀去广告 | [AlcidaeVideo_remove_ads.sgmodule](module/Kelee/AlcidaeVideo_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 哈罗去广告 | [EasyBike_remove_ads.sgmodule](module/Kelee/EasyBike_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 慧生活798去广告 | [SmartLife_remove_ads.sgmodule](module/Kelee/SmartLife_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 健康160去广告 | [91160_remove_ads.sgmodule](module/Kelee/91160_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 剑网三无界去广告 | [SeasunJX3_remove_ads.sgmodule](module/Kelee/SeasunJX3_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 京东外卖去广告 | [JDWaimai_remove_ads.sgmodule](module/Kelee/JDWaimai_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 金山文档去广告 | [WPS_Documents_remove_ads.sgmodule](module/Kelee/WPS_Documents_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 看家王去广告 | [ChatCam_remove_ads.sgmodule](module/Kelee/ChatCam_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 口袋壁纸去广告 | [ShoujiDesk_remove_ads.sgmodule](module/Kelee/ShoujiDesk_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 快对去广告 | [KuaiDuiZuoYe_remove_ads.sgmodule](module/Kelee/KuaiDuiZuoYe_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 快影去广告 | [KwaiVideoeditor_remove_ads.sgmodule](module/Kelee/KwaiVideoeditor_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 夸克扫描王去广告 | [QuarkScanking_remove_ads.sgmodule](module/Kelee/QuarkScanking_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 酷狗概念版去广告 | [KuGouYouth_remove_ads.sgmodule](module/Kelee/KuGouYouth_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 酷狗铃声去广告 | [KGRing_remove_ads.sgmodule](module/Kelee/KGRing_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 库街区去广告 | [KuroBBS_remove_ads.sgmodule](module/Kelee/KuroBBS_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 联掌门户去广告 | [LZMH_remove_ads.sgmodule](module/Kelee/LZMH_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 萝卜快跑去广告 | [RoboTaxi_remove_ads.sgmodule](module/Kelee/RoboTaxi_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 马克水印相机去广告 | [marki_remove_ads.sgmodule](module/Kelee/marki_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 漫客栈去广告 | [MKZ_remove_ads.sgmodule](module/Kelee/MKZ_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 每日赛车去广告 | [MeiRiSaiChe_remove_ads.sgmodule](module/Kelee/MeiRiSaiChe_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 美食杰去广告 | [MeiShiJie_remove_ads.sgmodule](module/Kelee/MeiShiJie_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 萌娘百科去广告 | [MoeGirlWiki_remove_ads.sgmodule](module/Kelee/MoeGirlWiki_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 摩天轮去广告 | [FerrisWheel_remove_ads.sgmodule](module/Kelee/FerrisWheel_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 摩托范去广告 | [MotorFans_remove_ads.sgmodule](module/Kelee/MotorFans_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 南网在线去广告 | [CSG_remove_ads.sgmodule](module/Kelee/CSG_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 排班日历去广告 | [AxWorkSchedule_remove_ads.sgmodule](module/Kelee/AxWorkSchedule_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 胖乖生活去广告 | [PangguaiLife_remove_ads.sgmodule](module/Kelee/PangguaiLife_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 配音秀去广告 | [DubbingShow_remove_ads.sgmodule](module/Kelee/DubbingShow_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 启信宝去广告 | [QiXinBao_remove_ads.sgmodule](module/Kelee/QiXinBao_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 省钱快报去广告 | [YueDanBa_remove_ads.sgmodule](module/Kelee/YueDanBa_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 收银通商户端去广告 | [ShouYinTongMerchant_remove_ads.sgmodule](module/Kelee/ShouYinTongMerchant_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 数字心动去广告 | [DigitalHeartbeat_remove_ads.sgmodule](module/Kelee/DigitalHeartbeat_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 随手记去广告 | [KingdeeMyMoney_remove_ads.sgmodule](module/Kelee/KingdeeMyMoney_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 他趣去广告 | [Taqu_remove_ads.sgmodule](module/Kelee/Taqu_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 腾讯文档去广告 | [TXDocs_remove_ads.sgmodule](module/Kelee/TXDocs_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 天猫校园去广告 | [TmallCampus_remove_ads.sgmodule](module/Kelee/TmallCampus_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 天气通去广告 | [TianQiTong_remove_ads.sgmodule](module/Kelee/TianQiTong_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 天气预报去广告 | [iReaderCityWeather_remove_ads.sgmodule](module/Kelee/iReaderCityWeather_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 天天跳绳去广告 | [CrazyRope_remove_ads.sgmodule](module/Kelee/CrazyRope_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 图怪兽去广告 | [TuGuaiShou_remove_ads.sgmodule](module/Kelee/TuGuaiShou_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 挖财记账去广告 | [WaCaiJiZhang_remove_ads.sgmodule](module/Kelee/WaCaiJiZhang_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 挖财记账去广告 | [Wacai_remove_ads.sgmodule](module/Kelee/Wacai_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 微博轻享版去广告 | [Weibo_intl_remove_ads.sgmodule](module/Kelee/Weibo_intl_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 微脉圈去广告 | [Weimai_remove_ads.sgmodule](module/Kelee/Weimai_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 微信小程序去广告 | [WexinMiniPrograms_Remove_ads.sgmodule](module/Kelee/WexinMiniPrograms_Remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 沃尔玛去广告 | [Walmart_remove_ads.sgmodule](module/Kelee/Walmart_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 香港抖音去广告 | [HKDouYin_remove_ads.sgmodule](module/Kelee/HKDouYin_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 小白智慧打印去广告 | [XiaobaiPrint_remove_ads.sgmodule](module/Kelee/XiaobaiPrint_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 小店掌柜去广告 | [ShopKeeperAdmin_remove_ads.sgmodule](module/Kelee/ShopKeeperAdmin_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 小黑盒去广告 | [XiaoHeiHe_remove_ads.sgmodule](module/Kelee/XiaoHeiHe_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 小桔充电去广告 | [XiaojukejiCharge_remove_ads.sgmodule](module/Kelee/XiaojukejiCharge_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 小喵看书去广告 | [MiaoRead_remove_ads.sgmodule](module/Kelee/MiaoRead_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 行者户外去广告 | [OnTheWay_remove_ads.sgmodule](module/Kelee/OnTheWay_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 新浪财经去广告 | [SinaStock_remove_ads.sgmodule](module/Kelee/SinaStock_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 一甜相机去广告 | [Yitian_remove_ads.sgmodule](module/Kelee/Yitian_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 有道翻译官去广告 | [YoudaoTrans_remove_ads.sgmodule](module/Kelee/YoudaoTrans_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 有道云笔记去广告 | [YoudaoNote_remove_ads.sgmodule](module/Kelee/YoudaoNote_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 阅友去广告 | [Yueyou_remove_ads.sgmodule](module/Kelee/Yueyou_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 云鲸智能去广告 | [NarwelRobots_remove_ads.sgmodule](module/Kelee/NarwelRobots_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 掌上无畏契约去广告 | [ValorantBible_remove_ads.sgmodule](module/Kelee/ValorantBible_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 直播吧去广告 | [Zhibo8_remove_ads.sgmodule](module/Kelee/Zhibo8_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 智慧苏州去广告 | [SuZhouCitizenCard_remove_ads.sgmodule](module/Kelee/SuZhouCitizenCard_remove_ads.sgmodule) | xream[https://github.com/xream] |
| 智联招聘去广告 | [ZhiLianZhaoPin_remove_ads.sgmodule](module/Kelee/ZhiLianZhaoPin_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 中国天气去广告 | [WeatherChina_remove_ads.sgmodule](module/Kelee/WeatherChina_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 纵横小说去广告 | [ZongHeng_remove_ads.sgmodule](module/Kelee/ZongHeng_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 最美壁纸去广告 | [iWallBiZhi_remove_ads.sgmodule](module/Kelee/iWallBiZhi_remove_ads.sgmodule) | 可莉🅥[https://github.com/luestr/ProxyResource/blob/main/README.md] |
| 腾讯视频去广告 | [Tencent_Video_remove_ads.sgmodule](module/Kelee/Tencent_Video_remove_ads.sgmodule) | RuCu6[https://github.com/RuCu6] |

历史适配稿含辅助工具生成的基础，不是全部从零手写；新变化必须读实际原版及依赖，再手动改写和复核。云端每日维护见 [maintenance/README.md](maintenance/README.md)。


## Tinder 额外补充

按用户指定站点 [loon-plugins.vercel.app](https://loon-plugins.vercel.app/plugins/tinder)，
单独加入 devchristian1337 的 Tinder 去广告；可莉补充仍为 106 项。
已阅读全文 LPX 与实际 JS，手写为原生 Surge JQ并加入同一总模块；保留
[独立 Tinder 模块](module/Extra/Tinder_remove_ads.sgmodule)。
原版广告/会员推广开关、对象类型判断和 URL 分派保持，奖励视频与付费功能状态保持。
原版和 JS 已归档，且都纳入现有每日差异检查，见
[复核记录](Extra-review/tinder-review-20261011.json)。
需要对 api.gotinder.com 开启 MITM，原生 JQ 的版本和响应大小限制同上；
服务器语义样例通过不代表客户端去广告已验证。
