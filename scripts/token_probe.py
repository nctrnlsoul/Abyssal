"""Measure what the real assets actually cost in tokens. count_tokens is free."""
import os, sys
from google import genai

client = genai.Client()
D = r"C:\Users\brian\Projects\abyssal\data"
MODEL = "gemini-3.5-flash"

targets = [
    ("nssp_2023.pdf",              "the 520-page ordinance"),
    ("reef_window_a.wav",          "60s hydrophone clip"),
    ("hab_forecast_cellcounts.png","NOAA HAB forecast image"),
    ("nasa_modis_redtide_2001.jpg","NASA MODIS bloom capture"),
]

total = 0
for name, label in targets:
    path = os.path.join(D, name)
    if not os.path.exists(path):
        print(f"{name:32} MISSING")
        continue
    try:
        f = client.files.upload(file=path)
        n = client.models.count_tokens(model=MODEL, contents=[f]).total_tokens
        total += n
        print(f"{name:32} {n:>10,} tokens   ({label}, {os.path.getsize(path):,} bytes)")
    except Exception as e:
        print(f"{name:32} ERROR {type(e).__name__}: {e}")

print(f"{'TOTAL one full pipeline pass':32} {total:>10,} tokens")
