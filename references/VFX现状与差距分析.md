# VFX 现状与差距分析

> 2026-06-08
> 来源：Explore 扫描所有素材包和特效资产（33 tool uses）

---

## 核心发现

### 1. SPUM 15个动画只用了2个

| 已用 | 空闲可用 |
|------|---------|
| Attack, Skill | Slash, Punch, Cast, Shoot, Dash, Idle2, Damage, Down, Die, StandUp, Run, Jump, Walk |

最大浪费：策划 JSON 里写的 `combat.stance` / `combat.normalAttack` / `combat.ultimate.cinematic` 目前全是文字备注，没有接运行时播放。

### 2. combat.archetype 在 JSON 里但代码没接

外包文档定义了4个流派原型：

| archetype | 视觉语言 | 适用角色 |
|-----------|---------|---------|
| 远程暗器 | 飞弹/弹道+命中粒子 | 东方不败、李寻欢、楚留香 |
| 内功奇门 | 法阵/光环+元素粒子 | 段誉、虚竹、天山童姥 |
| 刚猛外功 | 近身冲击波+震动 | 萧峰、郭靖、洪七公 |
| 剑气 | 斩击光刃+剑气波 | 令狐冲、西门吹雪、叶孤城 |

JSON里字段：`role_json → combat → archetype`
但 `BattleUnit.BuildVisual()` 和 `PerformAction` 都从没读过这个字段。

### 3. 飞弹/弹道系统已设计但未实现

外包文档描述：

| 弹体类型 | 适用 | 效果 |
|---------|------|------|
| Arrow | 暗器 | 直线高速飞行+命中炸开粒子 |
| Sphere | 内功 | 弧形轨迹+拖尾+命中膨胀爆散 |
| Palm | 拳掌 | 掌印前冲+命中冲击环 |
| Slash | 剑气 | 横向斩击光刃+命中斩裂痕 |

当前代码只有 `actor.DashToRoutine()` 和 `actor.LungeRoutine()` 近身逻辑——远程角色也近身砍。

### 4. HitFx 只有暴击/非暴击两档

```csharp
HitFx.Spawn(..., crit);  // 框架两档
```

没有区分：刀砍火花 vs 拳掌气爆 vs 法术光爆 vs 暗器血花。

---

## 分层方案

```
VFXID（如 "slash_sword" / "blast_fire" / "projectile_arrow"）
  ↓ 存武功表或武功总表里
VFXResolver 查注册表
  ↓ 接口不变
    现版：ParticleSystem 程序实现（零资产）
    后期：换成 Sprite 序列帧 / VFX Graph（接口不变）
```

核心思想：每个武功配置一个 VFXID，引擎通过 VFXID 查找对应的粒子/动画/弹道配置，不依赖于角色 JSON 的手动精调。

## 待做

- [ ] 接入 SPUM 剩余的 13 个动画状态
- [ ] 接入 combat.archetype 字段驱动 VFX 流派
- [ ] 实现飞弹/弹道系统
- [ ] HitFx 改为按技能类型分档
- [ ] VFX 配置存 JSON（一行搞定）
