# AI × 武侠Q传 · 协作开发手册

> 明确分工、固定工具链，杜绝 token 浪费。

---

## 一、分工原则

| 层级 | 谁来做 | 工具 | 典型任务 |
|---|---|---|---|
| SPUM 捏脸 | **人工** | Unity SPUM 编辑器 GUI | 选部件、调外观 |
| 素材验货 | **AI出清单 → 人工确认** | asset-verify CLI | 买包后先验再导入 |
| 文件编辑 | **AI** | bash / Read / Edit | 改JSON、改.cs、看日志 |
| 批处理构建 | AI写命令→**人工粘贴跑** | Unity batchmode CLI | 重建prefab、导入数据 |
| Play验收 | **人工** | Unity Play + 截图 | 按规范截图发给AI |
| 脚本开发 | **AI** | 直接编辑.cs | 新功能、bug修复 |

---

## 二、禁止事项

- ❌ 不用 Computer Use 鼠标点 Unity（截图→点击→报错循环烧 token）
- ❌ 不在 Unity 开着时跑 batchmode（争锁报错）
- ❌ 不用 Computer Use 打开 Unity（人工双击 Hub 即可）
- ❌ **导入第三方包时全选**（会把Samples/Demo塞进项目，污染结构，还可能带过时API炸编译）

---

## 三、数据管道

```
JSON (计划蓝图) → CharacterImporter → CharacterDef → GameDatabase → BattleUnit
```

无 ScriptableObject 中间层，JSON 即唯一数据源。

---

## 四、Asset Store 素材导入流程（重要！）

```
网页 Asset Store → 点 "Add to My Assets"
    ↓ 这只是关联到你的 Unity 账号，没下到本地
Unity Editor → Window → Asset Store（或 Package Manager → My Assets）
    ↓ 找到资产 → 点 Download（下载到本地缓存）
    ↓ 弹出 Import 窗口（树形勾选框）
    ↓ AI 告诉你勾哪些、去掉哪些
    ↓ 只勾必要目录（Core/Runtime/Editor），取消 Samples/Demo/Documentation
    ↓ 点 Import
```

**关键规则**：你装了某个包后，必须**明确告诉我**——"我装了 XXX"。AI 不会自动知道你项目里多了什么包。告诉我之后，我会去读它的 API 和用法，然后写代码时才会用。

### 导入前必问 AI

```bash
# 流程
你要导入 XXX.unitypackage
  → 先问我："这个包要注意什么？"
  → 我告诉你勾哪些文件夹、跳过哪些
  → 你照着勾 → Import
```

---

## 五、标准 CLI 命令

> **前提：关闭 Unity 编辑器**

### 重建角色 Prefab（改完 JSON 后必跑）
```bash
/Applications/Unity/Hub/Editor/6000.4.10f1/Unity.app/Contents/MacOS/Unity \
  -batchmode -quit \
  -projectPath "/Volumes/D2T/武侠小游戏/Unity/武侠q传unity" \
  -executeMethod WuxiaQ.EditorTools.SPUMCharacterBuilder.Run \
  -logFile /tmp/spum_build.log && echo "✅ 完成" || (echo "❌ 失败" && cat /tmp/spum_build.log | tail -30)
```

### 校验角色 Prefab
```bash
/Applications/Unity/Hub/Editor/6000.4.10f1/Unity.app/Contents/MacOS/Unity \
  -batchmode -quit \
  -projectPath "/Volumes/D2T/武侠小游戏/Unity/武侠q传unity" \
  -executeMethod WuxiaQ.EditorTools.SPUMCharacterBuilder.Validate \
  -logFile /tmp/spum_validate.log && echo "✅ 完成" || cat /tmp/spum_validate.log | tail -20
```

### 素材包验货（导入前必跑）
```bash
asset-verify /Volumes/D2T/武侠小游戏/Unity/功能组件/xxx.unitypackage
```

---

## 六、截图验收规范

| 场景 | 方式 | 注意 |
|---|---|---|
| 角色外观 | Scene视图，正面全身，关Grid/Gizmos | 不要用Game视图 |
| 战斗流程 | Play模式截全场（含血条/飘字） | 截一个完整回合 |
| 大招特效 | Play模式，按大招时刻截图 | 可多张连续截 |
| 报错 | **复制Console文本** | 文字比截图省token |

---

## 七、标准协作流程

### 改角色外观
```
AI改JSON(spum_parts) → 你关Unity → 粘贴CLI命令 → 重开Unity
→ Play → 截图给AI → AI判断 → 满意或继续调
```

### 新功能开发
```
AI读.cs → AI编辑.cs → Unity自动编译
→ 你Play验证 → 截图/报错发给AI
```

### 报错处理
```
你复制Console报错文字 → AI定位文件行号修复
```

---

## 八、Unity MCP（待接入，P2）

项目已内置 `com.unity.ai.assistant`（含 MCP Server），接入后 AI 可直接调用 Unity Editor API，无需关闭编辑器跑 batchmode。

关键区别：
- **Unity MCP** = 免费（Unity 6 自带），外部 AI 客户端连入操控 Editor
- **AI Gateway** = 要钱（需 Pro/Enterprise 订阅 + 座位），Unity 内置 Assistant 连第三方 AI

---

## 九、技术限制说明

### 视觉识别（看图）
本机配置了 dashscope(qwen3.5-omni-plus) 视觉模型，但**甲骨文 VPS(美国)连不上阿里云 API**，所以看图功能不可用。如需看图，需：
1. 换用从国内 VPS（阿里云 39.107.53.75）可访问的视觉 provider
2. 或换 OpenAI/Claude 等从美国能直达的 API

不管哪种，都需要你配置 API Key 并告诉我一声。

---

*最后更新：2026-06-06*
