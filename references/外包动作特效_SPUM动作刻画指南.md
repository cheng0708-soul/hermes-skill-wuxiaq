# 武侠Q传 · SPUM 动作能力 & 打斗刻画指南

> 审核结论：内容完全正确，无修正项。

## 一、SPUM 能力边界

- ✅ 外观逐人独特（SPUM像素角色生成器）
- ✅ 按流派区分动作（近战/弓/法术/斧/枪/剑）
- ✅ 动画分档，weapon自动推断或anim显式指定
- ⚠️ 不是每人一套独有招式（同流派动作共享）
- ⚠️ 自制专属动作用于个别招牌角色（后期精修）

**结论：绝技独特感靠 基础流派动作 + VFX特效 + 分镜/镜头/命中演出 实现。**

## 二、archetype→飞弹/颜色表

近战拳掌(金橙掌印)/近战刀剑(银白剑气)/斩击剑气(银白冷光)/刚猛外功(金橙重掌印)/远程暗器(铜黄毒绿箭矢)/内功奇门(太极蓝法球)

## 二-补. anim 动画触发名

Attack(近战挥砍)/AttackMagicPush(拳掌推掌)/AttackBow(弓暗器)/AttackMagic(法术挥手)/Skill(默认大招)/SkillMagic(掌法大招)/SkillBow(远程大招)

## 三、combat 分镜方法

1. archetype选流派
2. normalAttack：动作+节奏+命中感
3. ultimate.cinematic：起手→蓄力→命中→收招 四段
4. ultimate.vfx：特效意象描述
5. tempo：蓄力时长/顿帧/镜头
6. hit/death/intro各一句

## 四、落地分工

设计方→combat文字分镜+数值+art关键词
Unity侧→SPUM造形+动作选配+特效占位
后期→招牌角色精修1~2个专属骨骼动作
