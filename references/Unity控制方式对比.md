# Unity 控制方式对比（武侠Q传适用）

> 2026-06-06 整理。三种方式都能操控 Unity，但场景不同。

---

## 一、CLI Batchmode（当前在用）

```bash
/Applications/Unity/Hub/Editor/6000.4.10f1/Unity.app/Contents/MacOS/Unity \
  -batchmode -quit \
  -projectPath "/Volumes/D2T/武侠小游戏/Unity/武侠q传unity" \
  -executeMethod 命名空间.类.方法 \
  -logFile /tmp/build.log
```

| 特性 | 说明 |
|---|---|
| 编辑器状态 | **必须关闭**（`Temp/UnityLockfile` 会锁工程） |
| 能做 | 批量导入资源、跑 Editor 脚本、构建包、校验数据 |
| 不能做 | 实时操作场景、查看渲染结果 |
| 用法 | AI 写命令 → 你关 Unity → 粘贴跑 → 看日志 |
| 当前用于 | SPUM 角色 Prefab 生成、校验 |

**常见错误**：
- `error CS`：编译错误，脚本有问题
- `Two processes`：Unity Editor 没关，锁文件冲突
- License 类日志：正常，不是错误

---

## 二、Unity MCP（待接入，P2）

```
AI 客户端 (Claude Code / Cursor)
    ↓ MCP stdio 协议
relay 二进制 (~/.unity/relay/relay_linux 或 relay_mac_arm64)
    ↓ IPC (socket/pipe)
Unity Editor（MCP Bridge）
    ↓
内置工具: Unity_ManageScene / Unity_ManageGameObject / Unity_ManageAsset
         Unity_EditScript / Unity_ReadConsole / Unity_ManagePrefab
```

| 特性 | 说明 |
|---|---|
| 编辑器状态 | ✅ **必须开着** |
| 能做 | 建/删/改 GameObject、读写脚本、操作资源、读 Console |
| 不能做 | 操作 SPUM GUI 面板、调粒子参数实时看效果 |
| 用法 | 配置好 MCP 后，AI 直接发指令控制 Editor |
| 成本 | 免费（Unity 6 自带 Assistant 包） |
| 接入 | 项目已内置 `com.unity.ai.assistant`，配 relay 路径即可 |

**配置方式**（在你 Mac 上）：
1. 确认项目已开，Unity MCP Server 显示 Running（`Edit > Project Settings > AI > Unity MCP`）
2. 在 AI 客户端配置文件加：
```json
{
  "mcpServers": {
    "unity-mcp": {
      "command": "~/.unity/relay/relay_mac_arm64.app/Contents/MacOS/relay_mac_arm64",
      "args": ["--mcp"]
    }
  }
}
```
3. Unity 里 Accept 连接

---

## 三、AI Gateway（商业方案）

| 特性 | 说明 |
|---|---|
| Unity 内置 Assistant 窗口 | 切换 agent 到 Gemini/Claude Code/Codex |
| 成本 | 需 Unity Pro/Enterprise + Gateway 座位 + 各 API Key |
| 能做 | 在 Unity 里写代码、问问题，不切窗口 |
| 不做 | 不推荐。MCP 实现同样功能还免费 |

---

## 四、选型建议

```
开发阶段：
  AI 写代码/改 JSON          → 直接在当前对话做
  批量构建 Prefab             → CLI batchmode（你关 Unity 贴命令）
  实时调试/查报错             → Unity MCP（待接入）

生产阶段：
  批量导入/格式转换            → CLI batchmode
  CI/CD 自动构建               → CLI batchmode
```
