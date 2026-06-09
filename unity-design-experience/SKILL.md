---
name: unity-design-experience
category: software-development
description: "Unity 设计经验积累库——项目架构、管线方案、踩坑记录、2D角色生产、动画/特效集成等实战知识。适合回合制/卡牌/2D像素类游戏。中文别名: Unity设计经验"
---

# Unity 设计经验（武侠Q传实战积累）

> 本 skill 记录本项目（武侠Q传 Unity 版）开发过程中的实战经验、架构决策和踩坑记录。  
> 用于快速参考同类问题，避免重复犯错。

---

## 一、项目信息

| 项目 | 值 |
|------|-----|
| Unity 版本 | Unity 6000.4.10f1 |
| 渲染管线 | URP |
| 游戏类型 | 2D 横版回合制卡牌 |
| 角色方案 | SPUM 1.8.6（像素角色生成 + 代码化产线） |
| 数据驱动 | 全部 JSON（角色 / 武功 / 天赋 / 关卡 / 战斗参数） |
| 开发平台 | Mac (Apple Silicon) |

---

## 二、数据驱动架构（铁律）

```
改角色 → 写JSON      ← C#代码不动
改敌人 → 写JSON      ← C#代码不动
改关卡 → 写JSON      ← C#代码不动
改平衡 → 改config    ← C#代码不动
改战斗逻辑 → 改C#    ← 频率最低
```

**不要用 ScriptableObject**——全部 JSON 驱动。理由：
- JSON 可用任何编辑器修改，不依赖 Unity
- 方便外包/LLM 批量产出
- 版本对比/差分容易

**CharacterDef / SkillDef 等数据类**标记 `[System.Serializable]`，用 `JsonUtility.FromJson<T>()` 反序列化。

---

## 三、2D 角色生产工具对比

| 工具 | 类型 | 价格 | 适合 | 动画灵活性 | 批量能力 |
|------|------|------|------|-----------|---------|
| **SPUM** | 像素角色生成器 | $39 | Q版像素批量产出 | ❌ 预制动作组 | ✅ 填JSON→CLI出prefab |
| **AnyPortrait** | Unity 内绑骨动画 | $55 | 有散图想自己做专属动作 | ✅ 自由K帧 | ❌ 逐个手动 |
| **Spine** | 外部骨骼动画软件 | $79~299 | 专业动画师/买成品角色 | ✅ 自由K帧 | ❌ 逐个 |
| **Character Creator 2D** | 纸娃娃拼装 | $30~45 | 开箱即用量产 | ⚠️ 预制动作库 | ✅ 拼装快 |
| **Unity 2D Animation** | Unity 原生绑骨 | **免费** | 零成本方案 | ✅ 自由K帧 | ❌ 逐个 |
| **DragonBones** | 免费版 Spine | **免费** | 不想买 Spine Editor | ✅ 自由K帧 | ❌ 逐个 |

**共存规则**：多种工具可在同一项目共存（命名空间/渲染管线/资源目录互不冲突），各自管理各自角色的 prefab。战斗脚本通过一个 `if` 分支判断角色类型，调用对应接口。

---

## 四、SPUM 管线经验

### 4.1 代码化产线（已落地）

```
角色 JSON (spum_parts / spum_template)
  → CLI 脚本（SPUMCharacterBuilder）
  → 自动生成 prefab（含 AnimatorController）
```

`spum_template` 优先级：
1. 有 `spum_template` → 用模板 prefab，忽略 spum_parts
2. 无模板但有 `spum_parts` → 走 CLI 产线
3. 都无 → 强盗木桩兜底

### 4.2 ⚠️ AnimatorController 不可置空（重要踩坑）

**症状**：用代码动画系统控制 SPUM 角色时，置空 `runtimeAnimatorController` 导致角色卡死、部件不显示。

**根因**：SPUM 的 AnimatorController 不只是动画播放器——它还管理武器挂点激活、身体部件遮罩、材质参数同步、渲染组件激活时序。置空 = 丢了以上全部管线。

**修复**：不动 `runtimeAnimatorController`，通过 `TryFindStateAndIndex + PlayAnimation(state, index)` 走 SPUM 原生状态机驱动。

### 4.3 SPUM 成品角色文件结构

```
wj_XX_角色名/
├── wj_XX_Body.png      # 身体躯干
├── wj_XX_Hair.png      # 头发
├── wj_XX_Eye.png       # 眼睛
├── wj_XX_FaceHair.png  # 胡须（可选）
├── wj_XX_Cloth.png     # 上衣
├── wj_XX_Pant.png      # 下装
├── wj_XX_Back.png      # 披风/背饰（可选）
├── wj_XX_Weapon.png    # 武器（可选）
├── wj_XX.json          # 装配配方
└── wj_XX.prefab        # 最终产物
```

---

## 五、Spine 相关经验

### 5.1 Spine 成品角色核心文件（3个）

| 文件 | 说明 |
|------|------|
| `*.json` 或 `*.skel` | 骨骼 + 动画数据（.skel 是二进制版，更小） |
| `*.atlas.txt` | 贴图图集描述 |
| `*.png` | 贴图大图（所有部件合在一张上） |

### 5.2 旧版格式兼容问题

`.spine` 源文件是 2.x 版的话，最新的 Spine Unity Runtime 4.x 无法直接解析。

**3 条路**：
1. **装旧版 Runtime**：装 `spine-unity@3.8` 就能直接读 2.x 格式，不花钱
2. **用 Spine CLI 转换**：`spine-cli -i xxx.spine -o xxx.skel -f skeleton`
3. **找人帮忙导出**：有 Spine Editor 的人打开→重新导出为 4.x 格式

### 5.3 成品角色购买平台

| 平台 | 价格 | 说明 |
|------|------|------|
| Unity Asset Store | $5~$50 | 搜"Spine"或"2D Character" |
| Itch.io | $5~$30 | 独立作者多 |
| Cartoon Cupboard | $20~$60 | 专门做 Spine 角色 |

---

## 六、AnyPortrait 相关

### 6.1 角色要素

一个 AnyPortrait 角色 = 散图 + `.apsp` 工程 + prefab：

```
蔡文姬/
├── 各部位散图 PNG（头/身/臂/手/裙等）
├── ca_chara.apsp     # 工程文件（骨骼 + 所有关键帧）
└── ca_chara.prefab   # 最终产物
```

### 6.2 AnyPortrait 管 5 层中的哪几层

| 层 | AnyPortrait 负责？ |
|----|-------------------|
| ① 外观 | ✅ 绑骨 + 拼装 + 物理飘动 |
| ② 数值 | ❌ 代码/JSON 负责 |
| ③ 技能动画 | ✅ 自由 K 帧，不限动作 |
| ④ 演出（镜头/特效） | ❌ Unity 里另外做 |
| ⑤ 养成 | ❌ 代码/JSON 负责 |

---

## 七、常见 Unity C# 踩坑（项目实战汇总）

### 7.1 WaitUntil 布尔表达式缺运算符

**症状**：`yield return new WaitUntil(() => cond1 cond2 cond3)` 编译通过但逻辑错——C# 把多个并列条件解析为一个表达式，实际永远是死循环。

**修复**：条件之间加 `||`：
```csharp
yield return new WaitUntil(() => cond1 || cond2 || cond3);
```

### 7.2 [Serializable] 遗漏

**症状**：`JsonUtility.FromJson<T>` 要求 T 标记 `[System.Serializable]`。遗漏时 Unity 不报错误，但字段保持默认值——静默失败。

**修复**：
```csharp
[System.Serializable]
public class CombatConfig { ... }
```

### 7.3 CS1061 missing-field 模式

**症状**：设计文档新增了字段（如 `skill.targetMode`），但 C# 类定义没同步 → 编译错误。

**教训**：文档先于代码时，先在 SkillDef/CharacterDef 补字段定义，再调编译器。`文档改了 → 类没改 = 编译不过`。

### 7.4 Coroutine 定义了但从未启动

**症状**：`DrainUltimatesRoutine` 写了完整逻辑，但 `BattleLoop` 中从未 `yield return StartCoroutine(...)`。

**修复**：在正确的阶段加 `StartCoroutine` 调用。

### 7.5 自动站位写回遗漏

**症状**：`enemies[i].position` 改了但没写回数组，后续查到的仍是旧值。

**修复**：
```csharp
enemies[i] = new EnemyEntry(e.characterId, e.level, newPosition);
```

### 7.6 damageMultiplier 单位确认

JSON 中存的是整数百分比（六脉=63）还是小数（0.63）？如果是整数，需补 `/= 100f`，否则算出来的伤害是天文数字。

### 7.7 AnimatorController 自动生成：默认状态 + Loop Time（经验记录）

**场景**：通过 `AutoRigCharacter.cs` 解析 JSON 骨骼关键帧，反编译成 `.anim` 文件并自动组装 AnimatorController 时。

**两个坑：**

**① 默认状态不是 idle**
- 自动生成的 AnimatorController 把第一个拿到的动画（往往是 `behit`）设为默认状态 → 角色一进场就播放受击动画，而非待机。
- **修复**：生成时扫描所有动画名，找到含 `idle`（忽略大小写）的那个，用 `rootStateMachine.defaultState = defaultState` 设为默认状态。

**② 待机/移动动画不循环**
- idle/run/walk/move 这类动画没勾 Loop Time → 播一次就停住，角色石化。
- **修复**：对动画名做不区分大小写的全字匹配（`idle`/`run`/`walk`/`move`），匹配到的 `.anim` 强制设置 `loopTime = true`。

### 7.8 解析 Spine JSON 骨骼动画：正则不够用，需深度解析

**场景**：从 Spine 导出 JSON 中提取骨骼关键帧，反编译为 Unity `.anim` 动画文件。

**坑**：复杂角色的 Spine JSON 数据结构比预想深得多：

| 问题 | 说明 |
|------|------|
| `drawOrder` 嵌套 | 角色骨骼层级深，`drawOrder` 节点内有嵌套大括号 |
| `"curve": "stepped"` 字段 | Spine 用这个定义阶梯插值，简单正则直接匹配到一半断掉 |
| 正则表达式脆弱 | 普通正则按 `{...}` 提取动作块，遇到嵌套就匹配到错误的位置，结果整个动画块匹配失败 → 生成的 `.anim` 是空的（无 `m_EulerCurves`/`m_PositionCurves` 数据）→ 角色永远停在 Setup Pose，一动不动 |

**修复**：基于大括号层级的深度解析算法（Depth-Based Brace Parser）

```csharp
// 思路：逐字符扫描，维护一个 depth 计数器
// 遇到 {  → depth++
// 遇到 }  → depth--
// depth==0 时提取出一个完整块
```

这个算法：
- 对 `drawOrder` 嵌套天然免疫（depth 正确计数）
- 对 `"curve": "stepped"` 等额外字段不敏感（它在提取块内部，不影响块的边界）
- 100% 无遗漏提取所有骨骼关键帧

**验证**：修复后 `character_caocao_idle.anim` 中 `m_EulerCurves` 和 `m_PositionCurves` 被多条骨骼运动增量曲线及上百个关键帧填充，角色正常待机呼吸。

**教训**：正则表达式适合提取**扁平的、非嵌套的结构**。遇到嵌套 JSON/配置格式，先问自己——当前的数据结构深度是否可预测？如果是嵌套的、深度不固定的，直接用 **depth-based parser** 而不是正则。

**场景**：通过 `AutoRigCharacter.cs` 解析 JSON 骨骼关键帧，反编译成 `.anim` 文件并自动组装 AnimatorController 时。

**两个坑：**

**① 默认状态不是 idle**
- 自动生成的 AnimatorController 把第一个拿到的动画（往往是 `behit`）设为默认状态 → 角色一进场就播放受击动画，而非待机。
- **修复**：生成时扫描所有动画名，找到含 `idle`（忽略大小写）的那个，用 `rootStateMachine.defaultState = defaultState` 设为默认状态。

**② 待机/移动动画不循环**
- idle/run/walk/move 这类动画没勾 Loop Time → 播一次就停住，角色石化。
- **修复**：对动画名做不区分大小写的全字匹配（`idle`/`run`/`walk`/`move`），匹配到的 `.anim` 强制设置 `loopTime = true`。

JSON 中存的是整数百分比（六脉=63）还是小数（0.63）？如果是整数，需补 `/= 100f`，否则算出来的伤害是天文数字。

---

## 八、角色完成度五层模型

一个能上架的角色要过 5 关：

| 层 | 内容 | 优先级 |
|----|------|--------|
| ① 外观 | 像素小人能动（Idle/Attack/Hit/Die）+ 卡面图标 | P0 |
| ② 数值 | stats/growth + 伤害公式 + 触发率 | P0 |
| ③ 技能 | 天赋大招有视觉记忆点 + 武功槽可用 | P0 |
| ④ 演出 | 出场台词 + 放招分镜 + 阵亡演出 + 缘分互动 | P1 |
| ⑤ 养成 | 升级 + 装备 + 突破 + 升星 | P2 |

**①②③齐了就能上场打，④⑤让角色有灵魂。**

---

## 九、渲染/管线混用经验

### 9.1 多种 2D 工具共存

- 命名空间隔离（SPUM → `SPUM`，AnyPortrait → `apStudio`，互不冲突）
- 各管各的 prefab
- 战斗脚本判断角色类型：`if (isSpum) { ... } else if (isAnyPortrait) { ... }`
- 都兼容 URP

### 9.2 动画系统混用

- SPUM → Unity Animator（预制状态机）
- AnyPortrait → 自己的播放器
- Spine → Spine-SkeletonAnimation 组件
- 三者各自的 GameObject 上挂各自的组件，各自播放

---

## 十、生产管线对照

```
SPUM 管线（批量）：        AnyPortrait 管线（精做）：
JSON spum_parts            散图 PNG
  ↓ CLI 生成 prefab            ↓ 在 Unity 绑骨 K 帧
  ↓ 拖入场景                    ↓ 导出 .apsp + prefab
  ↓ 马上能动                    ↓ 拖入场景 + 代码调 Play()
  15分钟/角色                  数小时/角色
```

**项目混用策略**：
- 64 武将批量 → SPUM
- 关键角色/主角/BOSS → AnyPortrait 或 Spine 成品
- 杂兵 → SPUM
