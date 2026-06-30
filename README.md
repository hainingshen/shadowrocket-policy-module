# Shadowrocket Policy Module

一个面向 Shadowrocket 的规则模块项目，用四类策略把常见访问场景拆开：

- `General`：普通代理上网
- `YouTube`：YouTube、Google Video、YouTube Music 等
- `Netflix`：Netflix 播放、图片、API 与相关服务
- `DIRECT`：无需代理，直接连接

项目目标是把 Clash 常见规则拆成 Shadowrocket 更容易使用的模块格式，避免直接搬运 Clash 规则后出现策略组名、语法或顺序不匹配的问题。

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
2. `rules/netflix.list` -> `Netflix`
3. `rules/direct.list` -> `DIRECT`
4. `FINAL` -> `General`

流媒体规则放在直连规则之前，避免部分 CDN 或共享域名被过早直连。最后未命中的请求默认进入 `General`。

## 本地构建

```powershell
python scripts/build.py
python tests/validate_module.py
```

构建脚本会从 `rules/*.list` 生成 [modules/policy.module](modules/policy.module)。

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
- 规则列表偏保守，优先保证可读和可维护；可以按自己的使用场景继续补充。

## License

MIT
