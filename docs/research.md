# Strategy Research Notes

这些结论来自按策略拆分的并行调研，用于指导默认规则源选择和自动化生成逻辑。

## YouTube

默认使用 [blackmatrix7 YouTube](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/YouTube/YouTube.list) 作为主源，补充 [blackmatrix7 YouTubeMusic](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/YouTubeMusic/YouTubeMusic.list)、[ACL4SSR YouTube](https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/YouTube.list) 和 [MetaCubeX geosite YouTube](https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/youtube.list)。

规则重点是 `youtube.com`、`youtu.be`、`ytimg.com`、`googlevideo.com`、`ggpht.com`、`youtubei.googleapis.com`、YouTube Music 和少量高置信 IP/UA。不要默认导入 Google 全量 IP 或全流媒体源，避免共享 CDN 误伤。

## Netflix

默认使用 [MetaCubeX geosite Netflix](https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/netflix.list) 和 [MetaCubeX geoip Netflix](https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geoip/netflix.list) 作为主源，再从 [blackmatrix7 Netflix](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/Netflix/Netflix.list) 与 [ACL4SSR Netflix](https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/Netflix.list) 补域名和关键词。

默认不合并 blackmatrix7 的完整 Netflix IP 集，因为其中有较宽的 AWS 段，可能把非 Netflix 流量打进 Netflix 策略。`us-west-2.amazonaws.com`、`cookielaw.org`、`onetrust.com` 这类通用域名也默认排除。

## ChinaIM

`ChinaIM` 是强制直连层，不新增用户可选策略组，生成时映射到 `DIRECT`。它放在 `General` 之前，目标是避免微信、QQ、企业微信、钉钉、飞书等国内即时通讯被普通代理规则命中后连到国际版本或跨境入口。

默认来源包括本地兜底清单、[blackmatrix7 WeChat](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/WeChat/WeChat.list)、[blackmatrix7 DingTalk](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/DingTalk/DingTalk.list)、[blackmatrix7 Tencent](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/Tencent/Tencent.list)、[blackmatrix7 Tencent domain-set](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/Tencent/Tencent_Domain.list)、[blackmatrix7 ByteDance](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/ByteDance/ByteDance.list) 以及 ACL4SSR 的 WeChat/Tencent/ByteDance 规则。

这会让腾讯和字节的一部分非聊天服务也更早直连。这个取舍是有意的：国内即时通讯的账号、推送、文件、图片、支付和小程序基础设施高度共用，过度收窄反而容易漏掉登录或消息通道。

## General

显式 General 规则用于保护已知需要代理的普通访问域名，避免后续 `DIRECT` 大源抢走。默认来源是 [blackmatrix7 Proxy](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/Proxy/Proxy.list)、[blackmatrix7 Proxy domain-set](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/Proxy/Proxy_Domain.list)、[Loyalsoldier GFW](https://raw.githubusercontent.com/Loyalsoldier/clash-rules/release/gfw.txt) 和 [Loyalsoldier GreatFire](https://raw.githubusercontent.com/Loyalsoldier/clash-rules/release/greatfire.txt)。

不默认启用 `tld-not-cn`、全局媒体、下载/CDN 大集合或大云厂商 IP。SukkaW Global 可作为高质量备选源，但因许可证和重叠审查要求，默认只放在 optional sources。

## DIRECT

默认使用 [blackmatrix7 LAN](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/Lan/Lan.list)、[blackmatrix7 ChinaMaxNoMedia](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/ChinaMaxNoMedia/ChinaMaxNoMedia.list) 和 [ChinaMaxNoMedia domain-set](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/ChinaMaxNoMedia/ChinaMaxNoMedia_Domain.list)。它比把 Loyalsoldier direct、ACL4SSR China、MetaCubeX CN 等大源全部合并更可控。

DIRECT 必须排在 YouTube、Netflix、General 显式规则之后。校验脚本会断言 `youtube.com`、`netflix.com`、`github.com`、`qq.com`、`taobao.com`、`router.asus.com` 等关键域名的首条命中策略。
