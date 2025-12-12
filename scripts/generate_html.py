
# scripts/generate_html.py
# Converts structured client JSON into a styled HTML file under /clients/<slug>.html
# Uses string.Template (safe: no f-strings), so CSS/HTML braces won't break parsing.

import json
import sys
import os
import re
from datetime import datetime
from string import Template

def slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r'[^a-z0-9\- ]', '', s)
    s = s.replace(' ', '-')
    return s or 'client'

def safe_get(d, *keys, default=''):
    cur = d
    for k in keys:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur

def render_table(rows, headers):
    """rows: list[dict] with keys matching headers"""
    parts = ["<table><thead><tr>"]
    for h in headers:
        parts.append(f"<th>{h}</th>")
    parts.append("</tr></thead><tbody>")
    for r in rows or []:
        parts.append("<tr>")
        for h in headers:
            parts.append(f"<td>{r.get(h, '')}</td>")
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return "".join(parts)

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_html.py <input_json_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Read data
    ci = safe_get(data, "Client Information", default={})
    name = safe_get(ci, "Name", default="Unknown Client")
    date_str = safe_get(ci, "Date", default="")
    garment = safe_get(ci, "Garment", default="")
    height = safe_get(ci, "Height", default="")
    weight = safe_get(ci, "Weight", default="")
    notes = safe_get(ci, "Notes", default="")

    shirt_meas = data.get("Measurements – Shirt", [])
    trouser_meas = data.get("Measurements – Trouser", [])
    styles = data.get("Style Choices", {})
    style_shirt = styles.get("Shirt", [])
    style_trouser = styles.get("Trouser", [])
    instructions = data.get("Tailor Instructions", [])

    # Prepare output
    os.makedirs("clients", exist_ok=True)
    slug = slugify(name)
    out_path = os.path.join("clients", f"{slug}.html")

    css = """
    :root{ --bg:#fafafa; --text:#111; --muted:#555; --border:#ddd }
    *{ box-sizing:border-box }
    body{ margin:0; padding:32px; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif; background:var(--bg); color:var(--text) }
    .container{ max-width:750px; margin:0 auto; background:#fff; border:1px solid var(--border); border-radius:14px; box-shadow:0 6px 22px rgba(0,0,0,.06) }
    header{ padding:24px 24px 8px; border-bottom:1px solid var(--border) }
    h1{ margin:0 0 6px; font-size:28px }
    .meta{ color:var(--muted); font-size:14px }
    section{ padding:20px 24px }
    h2{ font-size:18px; margin:0 0 12px; color:#222 }
    h3{ font-size:16px; margin:10px 0 8px; color:#222 }
    table{ width:100%; border-collapse:collapse; margin:8px 0 16px }
