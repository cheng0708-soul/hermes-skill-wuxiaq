#!/usr/bin/env python3
"""
武侠Q传 前10关对手数值验证脚本 v2026-06-07
基于原版攻防公式（定稿§4 + §5）
普攻: atk²/(atk + def×3)
技能: base²/(base + def×3) - 化解值

使用方法:
  python3 scripts/enemies_stage_1_10.py

会输出每关的完整数值校验，包括：
- 玩家与敌方的属性对比
- 普攻/技能伤害计算
- 化解判定
- 综合难度评价

扩展：如需增加新关卡，在 stages 数组中添加即可。
敌人模板在 enemy_templates 字典中，可通过 scale_enemy() 缩放到任意等级。
"""

import sys

FREE_VALS = {"atk": 3, "mp": 3, "spd": 2, "def": 5, "hp": 10}

def final_stat(base, growth, lv, free_points=0, stat_type="atk"):
    val = base + growth * (lv - 1) + free_points * FREE_VALS[stat_type]
    return round(val, 1)

def normal_dmg(atk, ddef, C=3):
    return round(atk * atk / (atk + ddef * C), 1)

def skill_dmg(base, ddef, C=3):
    return round(base * base / (base + ddef * C), 1)

def dispel_chance(dmp, amp):
    if dmp + amp <= 0:
        return 0
    return min(dmp / (dmp + amp) * 0.8, 0.8)

def dispel_val(dmp, amp, base=0):
    return round(base + max(dmp - amp, 0) * 0.2, 1)

# 玩家角色模板
player_chars = {
    "萧峰": {
        "base":  {"hp": 399, "atk": 200, "mp": 213, "spd": 122, "def": 133},
        "growth": {"hp": 9.0, "atk": 6.1, "mp": 5.4, "spd": 2.6, "def": 1.3},
        "skill": {"name": "降龙十八掌", "wa": 0.6, "wm": 0.4, "ws": 0.0}
    },
    "段誉": {
        "base":  {"hp": 207, "atk": 77, "mp": 266, "spd": 124, "def": 69},
        "growth": {"hp": 5.2, "atk": 5.2, "mp": 8.2, "spd": 3.5, "def": 2.3},
        "skill": {"name": "六脉神剑", "wa": 0.4, "wm": 0.6, "ws": 0.0}
    },
    "令狐冲": {
        "base":  {"hp": 317, "atk": 182, "mp": 237, "spd": 211, "def": 88},
        "growth": {"hp": 7.5, "atk": 5.1, "mp": 5.6, "spd": 1.4, "def": 2.2},
        "skill": {"name": "独孤九剑", "wa": 0.7, "wm": 0.3, "ws": 0.0}
    },
}

# 敌方模板（基准等级，关卡缩放用 +5%/级）
enemy_templates = {
    "山贼喽啰": {
        "lv": 1, "hp": 180, "atk": 80, "mp": 30, "spd": 55, "def": 35,
        "skill": None, "feature": "山间小贼，不堪一击"
    },
    "山贼头目": {
        "lv": 3, "hp": 350, "atk": 140, "mp": 50, "spd": 65, "def": 55,
        "skill": {"name": "刀法", "wa": 0.8, "wm": 0.2, "ws": 0.0},
        "feature": "略通武艺的山贼统领"
    },
    "流寇": {
        "lv": 2, "hp": 160, "atk": 110, "mp": 20, "spd": 130, "def": 25,
        "skill": None, "feature": "来去如风的劫匪"
    },
    "黑衣人": {
        "lv": 3, "hp": 260, "atk": 130, "mp": 60, "spd": 85, "def": 50,
        "skill": {"name": "暗杀术", "wa": 0.6, "wm": 0.4, "ws": 0.0},
        "feature": "神秘刺客，出手狠辣"
    },
    "少林武僧": {
        "lv": 4, "hp": 380, "atk": 110, "mp": 80, "spd": 40, "def": 110,
        "skill": {"name": "罗汉拳", "wa": 0.7, "wm": 0.3, "ws": 0.0},
        "feature": "皮糙肉厚的佛门武僧"
    },
    "采花贼": {
        "lv": 3, "hp": 190, "atk": 120, "mp": 30, "spd": 155, "def": 30,
        "skill": {"name": "毒针", "wa": 0.3, "wm": 0.0, "ws": 0.7},
        "feature": "身法鬼魅的恶徒"
    },
    "镖师": {
        "lv": 5, "hp": 450, "atk": 100, "mp": 40, "spd": 50, "def": 80,
        "skill": None, "feature": "身经百战的护院"
    },
    "江湖散人": {
        "lv": 5, "hp": 300, "atk": 150, "mp": 90, "spd": 90, "def": 65,
        "skill": {"name": "游龙剑法", "wa": 0.6, "wm": 0.4, "ws": 0.0},
        "feature": "武功杂而不精的江湖客"
    },
    "魔教教徒": {
        "lv": 4, "hp": 240, "atk": 70, "mp": 180, "spd": 65, "def": 45,
        "skill": {"name": "化血魔功", "wa": 0.2, "wm": 0.8, "ws": 0.0},
        "feature": "修炼邪功的魔教弟子"
    },
    "关底BOSS": {
        "lv": 8, "hp": 800, "atk": 220, "mp": 160, "spd": 95, "def": 95,
        "skill": {"name": "霸王刀", "wa": 0.5, "wm": 0.5, "ws": 0.0},
        "feature": "前10关压轴强敌"
    },
}

def scale_enemy(template, target_lv):
    ratio = 1.0 + (target_lv - template["lv"]) * 0.05
    e = {"lv": target_lv}
    for stat in ["hp", "atk", "mp", "spd", "def"]:
        e[stat] = int(template[stat] * ratio)
    e["skill"] = template["skill"]
    e["feature"] = template["feature"]
    return e

# 前10关设计
stages = [
    {
        "stage": 1, "name": "初出茅庐",
        "player_lv": 1, "player_chars": [("萧峰", {}, 0)],
        "enemies": [("山贼喽啰", 1)],
        "description": "首战告捷，教学关卡。1v1熟悉操作节奏。",
    },
    {
        "stage": 2, "name": "小试牛刀",
        "player_lv": 2, "player_chars": [("萧峰", {}, 2), ("令狐冲", {}, 0)],
        "enemies": [("山贼喽啰", 1), ("山贼喽啰", 1)],
        "description": "1v2，解锁第二个角色。",
    },
    {
        "stage": 3, "name": "山贼头目",
        "player_lv": 3, "player_chars": [("萧峰", {"atk":2,"hp":2}, 4), ("令狐冲", {"atk":2,"hp":2}, 2)],
        "enemies": [("山贼喽啰", 2), ("山贼头目", 3)],
        "description": "首次出现头目级敌人。头目会用技能。",
    },
    {
        "stage": 4, "name": "流寇出没",
        "player_lv": 4, "player_chars": [("萧峰", {"atk":2,"hp":4}, 6), ("令狐冲", {"atk":2,"hp":4}, 4)],
        "enemies": [("流寇", 3), ("流寇", 3), ("山贼喽啰", 2)],
        "description": "首次3人队，出现高速敌人。流寇先手攻击。",
    },
    {
        "stage": 5, "name": "月黑风高",
        "player_lv": 5, "player_chars": [("萧峰", {"atk":4,"hp":6}, 8), ("令狐冲", {"atk":4,"hp":4}, 6), ("段誉", {}, 2)],
        "enemies": [("黑衣人", 4), ("流寇", 4), ("流寇", 3)],
        "description": "解锁第三个角色。黑衣人平衡型+流寇摸后排。",
    },
    {
        "stage": 6, "name": "少林武僧",
        "player_lv": 6, "player_chars": [("萧峰", {"atk":4,"hp":8}, 10), ("令狐冲", {"atk":6,"hp":6}, 8), ("段誉", {"mp":4,"hp":4}, 4)],
        "enemies": [("少林武僧", 5), ("少林武僧", 5), ("山贼头目", 4)],
        "description": "首次出现高防御敌人。武僧def=110+。",
    },
    {
        "stage": 7, "name": "魔教初现",
        "player_lv": 7, "player_chars": [("萧峰", {"atk":4,"hp":10}, 12), ("令狐冲", {"atk":6,"hp":8}, 10), ("段誉", {"mp":6,"hp":6}, 6)],
        "enemies": [("魔教教徒", 5), ("魔教教徒", 5), ("采花贼", 4)],
        "description": "魔教用内功攻击，采花贼高速骚扰后排。",
    },
    {
        "stage": 8, "name": "江湖险恶",
        "player_lv": 8, "player_chars": [("萧峰", {"atk":6,"hp":12}, 14), ("令狐冲", {"atk":8,"hp":8}, 12), ("段誉", {"mp":8,"hp":6}, 8)],
        "enemies": [("江湖散人", 6), ("镖师", 5), ("山贼喽啰", 4), ("山贼喽啰", 4)],
        "description": "4人敌方队，前排坦克+后排输出。",
    },
    {
        "stage": 9, "name": "黑道联盟",
        "player_lv": 9, "player_chars": [("萧峰", {"atk":6,"hp":14}, 16), ("令狐冲", {"atk":8,"hp":10}, 14), ("段誉", {"mp":10,"hp":8}, 10)],
        "enemies": [("关底BOSS", 7), ("黑衣人", 5), ("采花贼", 5), ("黑衣人", 5)],
        "description": "BOSS前哨战，BOSS血厚攻高+刺客。",
    },
    {
        "stage": 10, "name": "初遇强敌",
        "player_lv": 10, "player_chars": [("萧峰", {"atk":8,"hp":16}, 18), ("令狐冲", {"atk":10,"hp":12}, 16), ("段誉", {"mp":12,"hp":8}, 12)],
        "enemies": [("关底BOSS", 8), ("魔教教徒", 6), ("魔教教徒", 6), ("山贼头目", 5)],
        "description": "前10关压轴战，完整BOSS+魔教法术。",
    },
]

def calc_player_props(char_name, free_pts, lv):
    c = player_chars[char_name]
    b, g = c["base"], c["growth"]
    props = {}
    for stat in ["hp", "atk", "mp", "spd", "def"]:
        fp = free_pts.get(stat, 0)
        props[stat] = round(b[stat] + g[stat] * (lv - 1) + fp * FREE_VALS[stat], 1)
    return props

def calc_enemy_props(template_name, lv):
    t = enemy_templates[template_name]
    return scale_enemy(t, lv)

def enemy_skill_base(e):
    if not e["skill"]:
        return None
    sk = e["skill"]
    return e["atk"] * sk["wa"] + e["mp"] * sk["wm"] + e["spd"] * sk.get("ws", 0)

def format_battle(stage):
    s = stage
    lines = []
    lines.append(f"{'='*60}")
    lines.append(f"第{s['stage']}关：{s['name']}")
    lines.append(f"{s['description']}")
    
    # Player
    lines.append(f"\n【玩家 | Lv{s['player_lv']} | 队伍：{len(s['player_chars'])}人】")
    for p_name, fp, _ in s["player_chars"]:
        pp = calc_player_props(p_name, fp, s["player_lv"])
        lines.append(f"  {p_name}: hp={pp['hp']:.0f} atk={pp['atk']:.0f} mp={pp['mp']:.0f} spd={pp['spd']:.0f} def={pp['def']:.0f}")
    
    # Enemies
    lines.append(f"\n【敌人阵容】")
    for e_name, e_lv in s["enemies"]:
        ep = calc_enemy_props(e_name, e_lv)
        sk = ep["skill"]
        skill_info = ""
        if sk:
            sb = enemy_skill_base(ep)
            skill_info = f" | 技能={sk['name']} 基础={sb:.0f}"
        lines.append(f"  {ep['feature']}: hp={ep['hp']} atk={ep['atk']} mp={ep['mp']} spd={ep['spd']} def={ep['def']}{skill_info}")
    
    # Damage calcs
    lines.append(f"\n【攻防推算】")
    p_main_name, p_main_fp, _ = s["player_chars"][0]
    pp = calc_player_props(p_main_name, p_main_fp, s["player_lv"])
    
    for e_name, e_lv in s["enemies"]:
        ep = calc_enemy_props(e_name, e_lv)
        nd = normal_dmg(pp["atk"], ep["def"])
        lines.append(f"  {p_main_name} 普攻 {e_name}(def={ep['def']}): {nd:.1f}伤 | 需{ep['hp']/nd:.1f}击")
        sk = player_chars[p_main_name]["skill"]
        sb = pp["atk"] * sk["wa"] + pp["mp"] * sk["wm"]
        sd = skill_dmg(sb, ep["def"])
        dc = dispel_chance(ep["mp"], pp["mp"])
        dv = dispel_val(ep["mp"], pp["mp"])
        sd_after = max(sd - dv, 0.1) if dc > 0 else sd
        lines.append(f"    {sk['name']}(wa={sk['wa']},wm={sk['wm']}) 基础={sb:.0f} | 技能={sd:.1f} | 化解率={dc*100:.0f}% | 终伤={sd_after:.1f} | 需{ep['hp']/sd_after:.1f}击")
    
    lines.append(f"")
    if s["enemies"]:
        e_name, e_lv = s["enemies"][0]
        ep = calc_enemy_props(e_name, e_lv)
        nd_e = normal_dmg(ep["atk"], pp["def"])
        lines.append(f"  {e_name} 普攻 {p_main_name}(def={pp['def']:.0f}): {nd_e:.1f}伤 | 打空需{pp['hp']/nd_e:.1f}击")
        if ep["skill"]:
            sb_e = enemy_skill_base(ep)
            if sb_e:
                sd_e = skill_dmg(sb_e, pp["def"])
                dc_e = dispel_chance(pp["mp"], ep["mp"])
                dv_e = dispel_val(pp["mp"], ep["mp"])
                sd_e_after = max(sd_e - dv_e, 0.1) if dc_e > 0 else max(sd_e, 0.1)
                lines.append(f"    {ep['skill']['name']} 基础={sb_e:.0f} | 技能={sd_e:.1f} | 化解率={dc_e*100:.0f}% | 终伤={sd_e_after:.1f} | 打空需{pp['hp']/sd_e_after:.1f}击")
    
    # Summary
    survival_vs = []
    for e_name, e_lv in s["enemies"]:
        ep = calc_enemy_props(e_name, e_lv)
        nd_e = normal_dmg(ep["atk"], pp["def"])
        worst = nd_e
        if ep["skill"]:
            sb_e = enemy_skill_base(ep)
            if sb_e:
                sd_e = skill_dmg(sb_e, pp["def"])
                dv_e = dispel_val(pp["mp"], ep["mp"])
                final_dmg = max(sd_e - dv_e, 0.1)
                worst = max(worst, final_dmg)
        survival_vs.append(pp["hp"] / worst if worst > 0 else 999)
    
    max_hits = max(ep['hp'] / max(normal_dmg(pp['atk'], ep['def']), 0.1) for _, ep in [(None, calc_enemy_props(e,l)) for e,l in s['enemies']])
    min_survival = min(survival_vs)
    
    if s["stage"] <= 3:
        diff = "🟢 简单 教学关"
    elif s["stage"] <= 5:
        diff = "🟡 适中 开始需要策略"
    elif s["stage"] <= 7:
        diff = "🟠 有挑战 需要合理加点"
    else:
        diff = "🔴 困难 需要阵容搭配"
    
    lines.append(f"\n【综合评价】{diff}")
    lines.append(f"  击杀最硬敌人需{max_hits:.1f}次普攻 | 核心角色最长生存{min_survival:.1f}击\n")
    
    return "\n".join(lines)

def run():
    print("=" * 60)
    print("  武侠Q传 · 前10关对手设计数值验证")
    print("  " + "=" * 60)
    print(f"\n公式: 普攻=atk²/(atk+def×3) | 技能=base²/(base+def×3)-化解")
    print(f"玩家等级：1→10 | 自由点按推荐分配\n")
    
    for stage in stages:
        print(format_battle(stage))
    
    print("=" * 60)
    print("  前10关难度曲线总表")
    print("=" * 60)
    print(f"{'关':>3} | {'名称':<12} | {'玩家Lv':>7} | {'敌人数':>7} | {'总敌HP':>7} | {'难度'} ")
    print("-" * 60)
    for s in stages:
        total_hp = sum(calc_enemy_props(en, el)["hp"] for en, el in s["enemies"])
        diff_map = {3:"简单", 5:"适中", 7:"挑战", 10:"困难"} 
        diff_name = "简单" if s["stage"]<=3 else "适中" if s["stage"]<=5 else "挑战" if s["stage"]<=7 else "困难"
        print(f"{s['stage']:>3} | {s['name']:<12} | Lv{s['player_lv']:>3}   | {len(s['enemies']):>3}人   | {total_hp:>5}  | {diff_name}")
    print()

if __name__ == "__main__":
    run()
