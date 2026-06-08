# 武侠Q传 · 项目结构速览（AI 上下文地图）

> 新对话开头贴这个文件，AI 秒懂项目布局，无需重新摸索。  
> Unity 版本：6000.4.10f1 | 渲染管线：URP | 平台：Mac，外置盘 D2T

---

## 核心目录

```
武侠q传unity/
├── Assets/Game/
│   ├── Resources/
│   │   ├── Characters/         ← 武将 JSON 蓝图（wj_03.json 等），策划产出
│   │   └── Units/              ← 角色 Prefab（由 CLI 批量生成，不手编）
│   ├── Scripts/
│   │   ├── Battle/             ← 战斗核心
│   │   │   ├── BattleBootstrap.cs    场景入口，拉起战斗
│   │   │   ├── BattleManager.cs      回合/行动队列
│   │   │   ├── BattleUnit.cs         单个战斗单位（血/怒/技能）
│   │   │   ├── DamageCalculator.cs   伤害公式
│   │   │   ├── SPUM_Adapter.cs       反射驱动 SPUM 动画（不硬依赖 SPUM 类型）
│   │   │   └── FloatingText.cs       飘字
│   │   ├── Data/
│   │   │   ├── CharacterImporter.cs  JSON → CharacterDef（运行时解析）
│   │   │   ├── CharacterDef.cs       运行时数据模型
│   │   │   └── GameDatabase.cs       全局数据仓库（Dictionary）
│   │   ├── Core/
│   │   │   └── GameSession.cs        关卡状态、解锁逻辑
│   │   └── UI/
│   │       ├── BattleHUD.cs          战斗 UI（血条、怒气、大招按钮）
│   │       ├── StageSelectBootstrap.cs  关卡选择界面入口
│   │       ├── UIFactory.cs          UI 元件工厂
│   │       └── UnitHealthBar.cs      血条组件
│   ├── Editor/
│   │   ├── SPUMCharacterBuilder.cs   ← CLI 入口：批量构建角色 Prefab
│   │   │   菜单：武侠Q/生成武将 SPUM 角色
│   │   │   方法：WuxiaQ.EditorTools.SPUMCharacterBuilder.Run
│   │   └── SPUMSetup.cs              SPUM 初始化工具
│   └── Scenes/
│       ├── Battle.unity              战斗场景（代码驱动，场景本身近乎空）
│       └── StageSelect.unity         关卡选择场景
├── Assets/SPUM/                      ← SPUM 插件（第三方，勿改核心脚本）
│   └── Resources/Addons/             部件库 Index.json（Builder 读取）
├── docs/                             ← 设计文档
│   ├── AI协作开发手册.md             ← 协作流程（本项目 AI 开发规范）
│   ├── 项目总览.md                   规划/进度/决策（事实源）
│   ├── 角色生产流水线.md             加/改角色外观的完整步骤
│   ├── 战斗系统设计.md               P1 战斗升级方案（已拍板未实施）
│   └── 角色设计对接规范.md           数值底本、设计契约
└── PROJECT_MAP.md                    ← 本文件
```

---

## 数据流向

```
wj_XX.json          → CharacterImporter → CharacterDef → GameDatabase
                                                              ↓
SPUM Prefab         → BattleBootstrap.SpawnTeam()    → BattleUnit（战斗实体）
(Units/wj_XX.prefab)                                          ↓
                                                       BattleManager（调度）
```

---

## 关键约定

- **Prefab 不手编**：全部由 `SPUMCharacterBuilder.Run` 从 JSON 生成（幂等）
- **SPUM_Adapter**：用反射驱动 SPUM 动画，不直接依赖 SPUM 类型，避免包更新崩编译
- **Bootstrap 模式**：Battle.unity 场景近乎空，所有对象由代码在 Awake 生成
- **数值单一来源**：JSON → CharacterDef，无 ScriptableObject 中间层

---

## 当前待办（截至 2026-06-06）

| 优先级 | 任务 | 状态 |
|--------|------|------|
| P0 | 默认队 3 人外观校对（萧峰/西门吹雪/段誉） | 🔄 进行中 |
| P1 | 战斗升级：6人阵型 + 手动选目标 + 命中反馈 | ⏳ 待开始 |
| P1 | 数值平衡（玩家小数值 vs 敌人大数值） | ⏳ 待开始 |
| P2 | 招式 VFX（可外包） | ⏳ 待开始 |
| P2 | Unity MCP 接入 | ⏳ 待开始 |

---

## 素材库

> 位于 `/Volumes/D2T/武侠小游戏/Unity/功能组件/`，导入前先验货。

| 素材 | 状态 | 优先级 | 用途 |
|------|------|--------|------|
| SPUM 1.8.6 | ✅ 已导入 | — | 像素角色生成，核心产线 |
| Unity Heat - Modern UI v1.1.7 | ⬜ 未导入 | P1 | 升级战斗 HUD / 关卡选择 UI |
| Unity Cutscene Engine v1.5 | ⬜ 未导入 | P2 | 大招过场动画 |
| Animation Designer v1.2.5 | ⬜ 未导入 | P2 | SPUM 自定义动作补充 |
| Advanced Melee Targeting v1.6 | ⬜ 未导入 | 参考 | 手动选目标逻辑参考 |
| FS - Melee Combat System v2.0.6 | ⬜ 未导入 | 参考 | 近战战斗架构参考 |
| All Star Character Collection 5.2 | ⬜ 未导入 | 备用 | SPUM 部件不够时的备选 |
| Character Creator 2D v1.95 | ⬜ 未导入 | 备用 | SPUM 替代方案 |
| Flare Engine - 2D Tools v1.8.4 | ⬜ 未导入 | 备用 | 通用 2D 工具 |
| Body Poser v1.2 | ⬜ 未导入 | P2 | 过场静态姿势 |

