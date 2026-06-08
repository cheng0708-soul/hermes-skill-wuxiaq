# 三表架构·角色JSON标准格式（2026-06-08 定稿）

> 角色 JSON 是全系统的共同契约，不是三表重构的私有格式。
> SPUM CLI、场景系统、战斗系统、缘分系统都从这里读数据。

## 保留全部字段

以下字段无论三表架构如何，全部保留不动：

| 字段 | 消费方 | 理由 |
|------|--------|------|
| `art.spum` | 美术/文档 | 给美术的文字描述 |
| `art.spum_parts` | SPUM CLI | 捏脸配方，代码化产线必备 |
| `art.color` | 初始色调 | 可能被 SPUM 或 UI 使用 |
| `art.scale` | 场景/战斗 | 角色缩放 |
| `art.spum_template` | prefab 映射 | 代码复用模板 |
| `combat.stance` | 场景 | 战斗前待机姿态描述 |
| `combat.normalAttack` | 场景/特效 | 普攻演出描述 |
| `combat.ultimate` | 场景/特效 | 大招演出描述（cinematic/vfx/tempo/sfx） |
| `combat.hit` | 场景/动画 | 受击反应描述 |
| `combat.death` | 场景/动画 | 死亡动画描述 |
| `combat.intro` | 场景/入场 | 出场台词/动作描述 |
| `bonds`, `yuanfen` | 缘分系统 | 阵容缘分判定 |
| `lore` | 图鉴 | 角色背景故事 |

## 仅删除的字段

| 字段 | 原因 | 替代方案 |
|------|------|---------|
| `skills.ultimate` 内联对象 | 与 `talent_wugong` 冲突 | 由 WugongLibrary + TalentWugongTable 接管 |
| `wugong[]` 内联对象数组 | 旧格式 | 改为 `wugong_slots[]` 空引用 |

## 新增的字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `talent_wugong` | string | 角色天赋武功名，精准匹配 WugongLibrary 键名 |
| `wugong_slots` | string[3] | 3 个武功槽，填武功名引用（可空字符串） |
| `equipment_slots` | null[4] | 4 个装备槽，后续填装备 ID |
| `combat.vfx` | object | 角色级 VFX 偏好，覆盖 archetype 默认值 |

## `combat.vfx` 子字段

```json
"combat": {
  "archetype": "刚猛外功",
  "vfx": {
    "projectile": "palm",        // 飞弹形状，覆盖 archetype 默认
    "color": "#F2A900",          // 颜色，覆盖 archetype 默认
    "hitShake": "heavy",         // 震屏级别：none/light/medium/heavy
    "animPrelude": "Concentrate" // 前奏动画
  },
  ...
}
```

优先级：技能表字段 > `combat.vfx` > archetype 默认 > weapon 默认

## 迁移检查清单

迁移一个角色时逐项确认：

- [ ] `skills.ultimate` 已删除（若原版有则移到天赋表/wugong_lib）
- [ ] `wugong[]` 内联对象已删除
- [ ] `talent_wugong` 字段已添加，且与 wugong_lib.json 中 name 精准一致
- [ ] TBD: 该角色天赋武功名在 Resources/Config/talent_wugong.json 中也有记录（trigger_rate/attr）
- [ ] `wugong_slots` 已添加（至少 3 个空字符串占位）
- [ ] `equipment_slots` 已添加（4 个 null 占位）
- [ ] 其他所有字段（art/combat/bonds/yuanfen/lore）未动
- [ ] 启动后看 Console 有无 `[CharacterImporter] 武功库未找到` 警告
