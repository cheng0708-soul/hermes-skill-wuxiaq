# 经验记录 · Unity 武侠Q传：2D / 3D 选型与踩坑

> Unity 6000.4.10f1，URP。3D→2D 路线决策与素材踩坑记录。

---

## 一、路线决策：2D vs 3D（结论：**2D**）

| 维度 | 3D（All Star） | 2D（SPUM） |
|---|---|---|
| 还原原作 | ✗ 原作是 2D Q版 | ✓ 像素/卡通贴近 Q版 |
| 角色多样性 | ✗ 整包仅 1 个能用 | ✓ 工具批量生成 |
| 题材契合 | ✗ 西式写实/科幻 | ✓ 可生成武侠风 |
| 上手成本 | 高 | 低 |
| 已写代码 | 复用 | 复用 |

## 二、3D 路线放弃原因（All Star）

1. **可用成品角色极少**：仅 1 个 FutureForces/F01.prefab 带网格+Humanoid，还是科幻士兵
2. **基础身体无网格**：RootAnimsMale/BaseMale.fbx 的 renderers=0，隐形人
3. **动画分两套**：Legacy/ 旧动画不可重定向；Modern 动画可
4. **ProceduralMaterial 过时 API**：CS0619 致全工程编译失败
5. **URP 材质洋红**：Standard 着色器在 URP 下渲染异常

**教训**：3D 包先验四关——成品角色数/动画类型/材质管线/题材

## 三、2D 路线（SPUM）成功原因

- 现成 prefab + 全套战斗动画开箱即用
- 自带角色生成编辑器

**坑**：
1. 需要 `com.unity.2d.sprite` 包
2. 动画必须 `PopulateAnimationLists()` 先于 `OverrideControllerInit()`
3. `PlayAnimation(PlayerState, int)` 枚举区分普攻/技能
4. 默认朝左，需 `localScale.x = -1`
5. 死亡"诈尸"：`isDeath` 被其他动画置 false 会站起来

本项目用 `SPUM_Adapter` 反射驱动，不硬依赖 SPUM 类型。
