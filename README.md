# Shadowrocket Policy Module

一个面向 Shadowrocket 的规则模块项目，用四类策略把常见访问场景拆开：

- `General`：普通代理上网
- `YouTube`：YouTube、Google Video、YouTube Music 等
- `Netflix`：Netflix 播放、图片、API 与相关服务
- `DIRECT`：无需代理，直接连接

项目目标是把 Clash 常见规则拆成 Shadowrocket 更容易使用的模块格式，避免直接搬运 Clash 规则后出现策略组名、语法或顺序不匹配的问题。

当前模块采用“本地兜底规则 + 多个公开规则源自动归一化”的方式生成。默认来源偏稳健：优先使用 Shadowrocket 原生规则和明确的媒体专组规则，避免把大型 CDN、全流媒体或多个中国大源无差别叠加。

## 快速使用

1. 在 Shadowrocket 主配置里创建这些策略组：

   - `General`
   - `YouTube`
   - `Netflix`

   `DIRECT` 是 Shadowrocket 内置策略，不需要创建。

2. 将模块链接添加到 Shadowrocket：

   ```text
   https://raw.githubusercontent.com/hainingshen/shadowrocket-policy-module/main/modules/policy.module
   ```

3. 按你的节点实际情况，在 `General`、`YouTube`、`Netflix` 中分别选择节点。

## 完整配置示例

如果你还没有主配置，可以参考 [examples/example.conf](examples/example.conf)。这个示例只演示策略组结构，代理节点需要替换为你自己的订阅或节点。

## 规则顺序

模块按以下顺序生成规则：

1. `rules/youtube.list` -> `YouTube`
2. `rules/generated/youtube.list` -> `YouTube`
3. `rules/netflix.list` -> `Netflix`
4. `rules/generated/netflix.list` -> `Netflix`
5. `rules/general.list` -> `General`
6. `rules/generated/general.list` -> `General`
7. `rules/direct.list` -> `DIRECT`
8. `rules/generated/direct.list` -> `DIRECT`
9. `FINAL` -> `General`

YouTube 和 Netflix 放在最前，避免 Google/直连/GeoIP 规则抢走流媒体请求。显式 `General` 规则放在 `DIRECT` 之前，避免 GitHub、Reddit、OpenAI 等已知代理域名被国内大源误直连。最后未命中的请求默认进入 `General`。

## 本地构建

```powershell
python scripts/update_rules.py
python scripts/build.py
python tests/validate_module.py
```

`scripts/update_rules.py` 会按 [config/sources.json](config/sources.json) 拉取公开规则源并生成 `rules/generated/*.list` 和 [reports/sources.md](reports/sources.md)。`scripts/build.py` 会从手工规则和生成规则合成 [modules/policy.module](modules/policy.module)。

## 自动更新

仓库包含两个 GitHub Actions：

- `Validate`：验证已提交的生成文件和模块是否一致。
- `Update Rules`：每天定时拉取上游规则，生成模块，通过校验后自动提交变化。

如果只想人工更新规则，也可以在 GitHub Actions 页面手动运行 `Update Rules`。

## 默认来源

- YouTube：blackmatrix7 YouTube / YouTubeMusic、ACL4SSR YouTube、MetaCubeX geosite YouTube。
- Netflix：MetaCubeX geosite + geoip 为主，blackmatrix7 和 ACL4SSR 只补域名/关键词，默认不合并 blackmatrix7 的宽泛 Netflix IP 段。
- General：blackmatrix7 Proxy / Proxy domain-set、Loyalsoldier GFW、Loyalsoldier GreatFire。
- DIRECT：blackmatrix7 LAN、blackmatrix7 ChinaMaxNoMedia / ChinaMaxNoMedia domain-set。

未默认启用的大源会放在 `config/sources.json` 的 `optional_sources` 中，例如 Loyalsoldier `proxy/direct`、MetaCubeX CN 和 SukkaW Global。启用前建议先看体量、许可证和冲突风险。

## 添加规则

规则文件使用 Shadowrocket 规则语法，每行一条规则，不包含策略名：

```text
DOMAIN-SUFFIX,example.com
DOMAIN,api.example.com
DOMAIN-KEYWORD,example
IP-CIDR,192.0.2.0/24,no-resolve
```

生成模块时脚本会自动补上对应策略名。

## 注意

- 模块引用的策略组名必须和主配置完全一致。
- 本项目不会内置任何代理节点、订阅地址或账号信息。
- “全覆盖”在规则工程里无法一次性保证绝对完整；本项目通过多来源、去重、顺序优先级、关键域名断言和定时更新来逼近覆盖。
- 规则源可能有各自许可证和维护策略。新增来源前请确认允许再分发生成结果。

## License

MIT
