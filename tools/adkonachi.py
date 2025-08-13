#!/usr/bin/env python3
"""
"עדכונחי" — מעטפת CLI מינימלית:
קולט בקשה טקסטואלית פשוטה, מפיק קובץ קונפיגורציה, ומריץ סימולציה.
זהו POC: פרסינג נאיבי + הרצה ישירה של דמו.
"""
import sys, re, json
from pathlib import Path

TEMPLATE = {
  "grid": {"nx": 10, "ny": 20, "dx": 10000, "dy": 10000},
  "drivers": {"solar_rad": 320, "precip_mm": 0, "irrigation_mm": 0},
  "winds": {"u": 5, "v": 0},
  "experiments": []
}

def parse(text: str):
    cfg = json.loads(json.dumps(TEMPLATE))
    m = re.search(r"ייעור\s+(\d+)%", text)
    if m:
        # כרגע לא מיישמים ייעור אמיתי; שומרים אינדיקציה בקונפיג
        cfg["experiments"].append({"note": f"afforest_{m.group(1)}pct"})
    m = re.search(r"תאים\s*\[(\d+):(\d+),\s*(\d+):(\d+)\]", text)
    if m:
        i0,i1,j0,j1 = map(int, m.groups())
        cfg["experiments"].append({
            "inject_patch": {"i_range":[i0,i1], "j_range":[j0,j1], "q_values":[0.015,0.025,0.015]},
            "days": 5
        })
    return cfg

def main():
    if len(sys.argv) < 2:
        print('השתמשו: adkonachi "ניסוי: ייעור 30% בתאים [3:7,2:6] ל-5 ימים"')
        sys.exit(0)
    text = sys.argv[1]
    cfg = parse(text)
    out = Path("adkonachi_config.json")
    out.write_text(json.dumps(cfg, ensure_ascii=False, indent=2))
    print("נוצר קובץ:", out.resolve())
    print(json.dumps(cfg, ensure_ascii=False, indent=2))
    print("\n(POC בלבד — להרצה מלאה השתמשו ב-examples/run_demo.py)")

if __name__ == "__main__":
    main()
