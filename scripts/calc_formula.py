#!/usr/bin/env python3
"""
武侠Q传攻防公式测试脚本（2026-06-07 v3 — 加入AOE位置衰减）
使用方式: python3 scripts/calc_formula.py [C值]

基于原版拆包公式（定稿§4+§5+§6）:
  统一公式：原伤 = base² / (base + def × C)
  普攻：base = atk × 1.0
  技能：base = (atk×aw + mp×mw + spd×sw) × (range_mul/100)
  AOE位置衰减：第1目标100%、第2目标80%、第3目标60%，各自独立计算
  化解(仅大招)：触发率=防守mp/(防守mp+攻击mp)×0.8，值=max(防mp-攻mp,0)×0.2
  真气消耗：固定整型值（技能表配置），不按比例
  心法：被动Buff，不占用攻击回合
  暴击：15%固定 × 1.5倍
  波动：±5%

默认参数: C=3, def=+5, hp=+10
"""

import sys

LV = 60
PTS = (LV - 1) * 2  # 118

CHARS = {
    "萧峰":   {"b": {"hp":399,"atk":200,"mp":213,"spd":122,"def":133}, "g": {"hp":9,"atk":6.1,"mp":5.4,"spd":2.6,"def":1.3}},
    "段誉":   {"b": {"hp":207,"atk":77,"mp":266,"spd":124,"def":69},  "g": {"hp":5.2,"atk":5.2,"mp":8.2,"spd":3.5,"def":2.3}},
    "令狐冲": {"b": {"hp":317,"atk":182,"mp":237,"spd":211,"def":88}, "g": {"hp":7.5,"atk":5.1,"mp":5.6,"spd":1.4,"def":2.2}},
    "西门吹雪":{"b": {"hp":214,"atk":255,"mp":0,"spd":142,"def":71}, "g": {"hp":7.3,"atk":10.8,"mp":0,"spd":7.1,"def":1.7}},
    "上官金虹":{"b": {"hp":388,"atk":100,"mp":222,"spd":55,"def":200},"g": {"hp":8.5,"atk":4.4,"mp":6.81,"spd":3.3,"def":2.39}},
}

SKILLS = {
    "独孤九剑": {"aw": 0.7, "mw": 0.3, "sw": 0.0, "range_mul": 88, "range_type": "单体"},
    "六脉神剑": {"aw": 0.4, "mw": 0.6, "sw": 0.0, "range_mul": 63, "range_type": "贯穿"},
    "降龙十八掌":{"aw": 0.6, "mw": 0.4, "sw": 0.0, "range_mul": 18, "range_type": "横扫"},
    "子母龙凤环":{"aw": 0.3, "mw": 0.7, "sw": 0.0, "range_mul": 15, "range_type": "全体"},
}

FREE_VALS = {"atk": 3, "mp": 3, "spd": 2, "def": 5, "hp": 10}


def calc(name, build):
    c = CHARS[name]
    b, g = c["b"], c["g"]
    fp = {k: build.get(k, 0) for k in ["atk", "mp", "spd", "def", "hp"]}
    return {
        "atk": b["atk"] + g["atk"] * (LV - 1) + fp["atk"] * FREE_VALS["atk"],
        "mp":  b["mp"]  + g["mp"]  * (LV - 1) + fp["mp"]  * FREE_VALS["mp"],
        "spd": b["spd"] + g["spd"] * (LV - 1) + fp["spd"] * FREE_VALS["spd"],
        "def": b["def"] + g["def"] * (LV - 1) + fp["def"] * FREE_VALS["def"],
        "hp":  b["hp"]  + g["hp"]  * (LV - 1) + fp["hp"]  * FREE_VALS["hp"],
    }


def dmg(base_, ddef_, C=3):
    """统一伤害公式: base²/(base + def×C)"""
    return base_ * base_ / (base_ + ddef_ * C)


def aoe_dmg(base_, ddef_, targets=1, C=3):
    """AOE位置衰减伤害: 返回[目标1, 目标2, ..., 目标N]"""
    decay = [1.0, 0.8, 0.6, 0.5, 0.4, 0.3]
    results = []
    for i in range(targets):
        decayed = base_ * decay[i] if i > 0 else base_
        results.append(dmg(decayed, ddef_, C))
    return results


def dispel_chance(dmp, amp):
    return dmp / (dmp + amp) * 0.8 if (dmp + amp) > 0 else 0


def dispel_val(dmp, amp, base_d=0):
    return base_d + max(dmp - amp, 0) * 0.2


def run_tests(C=3):
    builds_def = {"def": PTS}
    builds_atk = {"atk": PTS}
    builds_mp  = {"mp": PTS}
    builds_hp  = {"hp": PTS}

    lh_atk = calc("令狐冲", builds_atk)
    xf_def = calc("萧峰", builds_def)
    xf_none = calc("萧峰", {})
    xf_atk = calc("萧峰", builds_atk)
    dy_mp = calc("段誉", builds_mp)
    xm_atk = calc("西门吹雪", builds_atk)
    gs_mp = calc("上官金虹", builds_mp)

    def skill_base(skill_name, props):
        s = SKILLS[skill_name]
        ws = props["atk"] * s["aw"] + props["mp"] * s["mw"] + props["spd"] * s["sw"]
        return ws * (s["range_mul"] / 100), ws, s

    print("=== 60级标准测试 (C=%d, def=+5, hp=+10) ===" % C)
    print()

    # ---- 1. 令狐冲(全武) vs 萧峰(全防) ----
    nd = dmg(lh_atk["atk"], xf_def["def"], C)
    print("1. 令狐冲(全武) vs 萧峰(全防):")
    print("   普攻=%.0f  活=%.1f击" % (nd, xf_def["hp"]/nd))

    sb, ws, sk = skill_base("独孤九剑", lh_atk)
    sd = dmg(sb, xf_def["def"], C)
    dc = dispel_chance(xf_def["mp"], lh_atk["mp"])
    dv = dispel_val(xf_def["mp"], lh_atk["mp"])
    sa = max(sd - dv, 0)
    print("   独孤九剑(单体88%%) 加权和=%.0f 基础=%.0f 原伤=%.0f" % (ws, sb, sd))
    print("   化解率=%.0f%% 化解值=%.0f 终伤=%.0f 活=%.1f击" % (dc*100, dv, sa, xf_def["hp"]/sa))
    print()

    # ---- 2. 段誉(全内) vs 萧峰(无点) ----
    print("2. 段誉(全内) vs 萧峰(无点):")
    print("   段誉: atk=%.0f mp=%.0f" % (dy_mp["atk"], dy_mp["mp"]))

    sb2, ws2, sk2 = skill_base("六脉神剑", dy_mp)
    nd2 = dmg(dy_mp["atk"], xf_none["def"], C)
    sd2 = dmg(sb2, xf_none["def"], C)
    print("   六脉神剑(贯穿63%%) 加权和=%.0f 基础=%.0f" % (ws2, sb2))
    print("   普攻=%.0f  单目标技能原伤=%.0f" % (nd2, sd2))
    
    # AOE 位置衰减：打一列3个
    aoe = aoe_dmg(sb2, xf_none["def"], 3, C)
    print("   贯穿三目标(100%%+80%%+60%%衰减): %.0f + %.0f + %.0f = 总伤=%.0f" % (
        aoe[0], aoe[1], aoe[2], sum(aoe)))
    print()

    # ---- 3. 萧峰(全武) 降龙 vs 普攻 ----
    sb3, ws3, sk3 = skill_base("降龙十八掌", xf_atk)
    nd3 = dmg(xf_atk["atk"], xf_none["def"], C)
    sd3 = dmg(sb3, xf_none["def"], C)
    aoe3 = aoe_dmg(sb3, xf_none["def"], 3, C)
    print("3. 萧峰(全武) 降龙 vs 普攻:")
    print("   降龙(横扫18%%) 加权和=%.0f 基础=%.0f" % (ws3, sb3))
    print("   普攻单目标=%.0f  降龙单目标=%.0f  打一排三目标=%.0f+%.0f+%.0f=总伤%.0f" % (
        nd3, sd3, aoe3[0], aoe3[1], aoe3[2], sum(aoe3)))
    print()

    # ---- 4. 全防 vs 全血 ----
    xf_hp = calc("萧峰", builds_hp)
    nd4 = dmg(lh_atk["atk"], xf_hp["def"], C)
    nd5 = dmg(lh_atk["atk"], xf_def["def"], C)
    print("4. 全防 vs 全血:")
    print("   全防: def=%.0f hp=%.0f 活=%.1f击" % (xf_def["def"], xf_def["hp"], xf_def["hp"]/nd5))
    print("   全血: def=%.0f hp=%.0f 活=%.1f击 (比率=%.2f)" % (
        xf_hp["def"], xf_hp["hp"], xf_hp["hp"]/nd4, (xf_hp["hp"]/nd4)/(xf_def["hp"]/nd5)))
    print()

    # ---- 5. 化解 vs 低mp ----
    sb5, ws5, sk5 = skill_base("子母龙凤环", gs_mp)
    nd5 = dmg(sb5, xm_atk["def"], C)
    dc5 = dispel_chance(xm_atk["mp"], gs_mp["mp"])
    dv5 = dispel_val(xm_atk["mp"], gs_mp["mp"])
    sa5 = max(nd5 - dv5, 0) if dc5 > 0 else nd5
    print("5. 化解效果：上官(全内,mp=%.0f) vs 西门(全武,mp=%.0f):" % (gs_mp["mp"], xm_atk["mp"]))
    print("   子母龙凤环(全体15%%) 加权和=%.0f 基础=%.0f 原伤=%.0f" % (ws5, sb5, nd5))
    print("   化解率=%.0f%% 化解值=%.0f 终伤=%.0f" % (dc5*100, dv5, sa5))
    print()

    # ---- 6. 段誉 vs 西门（极端对比）----
    print("6. 极端对比：段誉(全内) vs 西门(全武):")
    print("   段誉: atk=%.0f mp=%.0f def=%.0f hp=%.0f" % (
        dy_mp["atk"], dy_mp["mp"], dy_mp["def"], dy_mp["hp"]))
    print("   西门: atk=%.0f mp=%.0f def=%.0f hp=%.0f" % (
        xm_atk["atk"], xm_atk["mp"], xm_atk["def"], xm_atk["hp"]))

    nd6 = dmg(xm_atk["atk"], dy_mp["def"], C)
    print("   西门普攻->段誉: %.0f  需%.1f击杀" % (nd6, dy_mp["hp"]/nd6))

    sb6, ws6, sk6 = skill_base("六脉神剑", dy_mp)
    nd6b = dmg(sb6, xm_atk["def"], C)
    dc6 = dispel_chance(xm_atk["mp"], dy_mp["mp"])
    dv6 = dispel_val(xm_atk["mp"], dy_mp["mp"])
    sa6 = max(nd6b - dv6, 0) if dc6 > 0 else nd6b
    aoe6 = aoe_dmg(sb6, xm_atk["def"], 3, C)
    print("   段誉六脉(贯穿63%%)->西门: 基础=%.0f 原伤=%.0f" % (sb6, nd6b))
    print("   西门mp=0无化解, 终伤=%.0f  需%.1f击杀" % (sa6, xm_atk["hp"]/sa6))
    print("   贯穿三目标(100%%+80%%+60%%): %.0f+%.0f+%.0f=%.0f" % (
        aoe6[0], aoe6[1], aoe6[2], sum(aoe6)))


if __name__ == "__main__":
    C = float(sys.argv[1]) if len(sys.argv) > 1 else 3
    run_tests(C)
