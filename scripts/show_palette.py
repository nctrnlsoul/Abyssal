import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.palette import CONTRAST_REQUIREMENTS, SEMANTIC, contrast
print(f"{'PAIR':<28}{'RATIO':>8}  {'NEEDS':>6}  RESULT")
print("-" * 58)
for fg, bg, need in CONTRAST_REQUIREMENTS:
    r = contrast(SEMANTIC[fg], SEMANTIC[bg])
    print(f"{fg + ' on ' + bg:<28}{r:>7.2f}:1{need:>7.1f}  {'PASS' if r >= need else 'FAIL'}")
