
# --- ADD THIS HELPER (place it near other helpers) ---
def get_list(d, names):
    for n in names:
        if n in d:
            return d[n]
    return []

# --- REPLACE THESE LINES ---
# shirt_meas = data.get("Measurements – Shirt", [])
# trouser_meas = data.get("Measurements – Trouser", [])
# styles = data.get("Style Choices", {})

# --- WITH# --- WITH THESE ---
shirt_meas   = get_list(data, ["Measurements – Shirt", "Measurements - Shirt"])
trouser_meas = get_list(data, ["Measurements – Trouser", "Measurements - Trouser"])

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
    th, td{ border:1px solid var(--border); padding:10px 12px; text-align:left; vertical-align:top }
    th{ background:#f4f6f8; font-weight:600 }
    ul{ margin:8px 0 0 20px }
    li{ margin:6px 0 }
    .info-grid{ display:grid; grid-template-columns: 1fr 1fr; gap:10px }
    footer{ padding:16px 24px 24px; color:var(--muted); font-size:12px }
    """

    info_html = (
        f"""
      <div class="info-grid">
        <div><strong>Name:</strong> {name}</div>
        <div><strong>Height:</strong> {height}</div>
        <div><strong>Weight:</strong> {weight}</div>
        <div><strong>Notes:</strong> {notes}</div>
      </div>
    """
    )

    shirt_table = render_table(shirt_meas, ["Area", "Measurement", "Notes"])
    trouser_table = render_table(trouser_meas, ["Area", "Measurement", "Notes"])

    style_shirt_html = "".join([f"<li>{item}</li>" for item in style_shirt])
    style_trouser_html = "".join([f"<li>{item}</li>" for item in style_trouser])
    instructions_html = "".join([f"<li>{item}</li>" for item in instructions])

    tpl = Template(
        """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Client Sheet – $name</title>
  <style>$css</style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Client Sheet – $name</h1>
      <div class="meta">Date: $date_str · Garment: $garment</div>
    </header>

    <section>
      <h2>Section 1: Client Information</h2>
      $info_html
    </section>

    <section>
      <h2>Section 2: Measurements</h2>

      <h3>Shirt</h3>
      $shirt_table

      <h3>Trouser</h3>
      $trouser_table
    </section>

    <section>
      <h2>Section 3: Style Choices</h2>
      <h3>Shirt</h3>
      <ul>$style_shirt_html</ul>
      <h3>Trouser</h3>
      <ul>$style_trouser_html</ul>
    </section>

    <section>
      <h2>Section 4: Tailor Instructions</h2>
      <ul>$instructions_html</ul>
    </section>

    <footer>
      Generated on $generated_on
    </footer>
  </div>
</body>
</html>
"""
    )

    html = tpl.substitute(
        name=name,
        date_str=date_str,
        garment=garment,
        css=css,
        info_html=info_html,
        shirt_table=shirt_table,
        trouser_table=trouser_table,
        style_shirt_html=style_shirt_html,
        style_trouser_html=style_trouser_html,
        instructions_html=instructions_html,
        generated_on=datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
    )

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Created: {out_path}")


if __name__ == "__main__":
    main()
