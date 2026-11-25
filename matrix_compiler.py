import os
import json
import html
from datetime import datetime

DEFAULT_BASE_URL = "https://samsivaji1297-byte.github.io/FMMediaEnterprises-Hub"
TOOLS_DIR = "tools"


def resolve_base_url():
    raw = os.environ.get("GSC_SITE_URL", "").strip().rstrip("/")
    if not raw or "FMMediaEnterprises-Hub" not in raw:
        return DEFAULT_BASE_URL
    return raw


BASE_URL = resolve_base_url()

OFFER_BRIDGES = {
    "compression": {
        "badge": "SYSTEM UPGRADE • $197",
        "headline": "Build & Launch Without Dragging It Out for Weeks",
        "subtext": "The Compression System walks you step by step through packaging and shipping a sellable digital product in a single 90-minute sprint.",
        "cta": "Get The Compression System →",
        "url": f"{BASE_URL}/go/compression/"
    },
    "operator": {
        "badge": "FIELD SYSTEM • $97",
        "headline": "Lock In Daily Discipline & High-Leverage Execution",
        "subtext": "The Operator Mindset Kit gives you practical frameworks, daily resets, and decision rules so your standards hold under pressure.",
        "cta": "Get the Operator Mindset Kit →",
        "url": "https://thefinalmindset.gumroad.com/l/operatormindsetkit"
    }
}


def utility_page_url(slug):
    return f"{BASE_URL}/{TOOLS_DIR}/{slug}/index.html"


def hub_page_url():
    return f"{BASE_URL}/{TOOLS_DIR}/index.html"


def render_utility_page(util, all_utils):
    slug = util["slug"]
    title = html.escape(util["title"])
    desc = html.escape(util["meta_description"])
    target_q = html.escape(util["target_query"])
    formula_mode = util.get("formula_mode", "readiness_score")
    bridge = OFFER_BRIDGES.get(util.get("bridge_offer", "operator"), OFFER_BRIDGES["operator"])
    canonical = utility_page_url(slug)
    steps = util.get("action_steps") or [
        "Set a clear daily baseline you can execute consistently.",
        "Eliminate your biggest weekly distraction or friction point.",
        "Review your numbers every 7 days and tighten the process."
    ]
    steps_html = "\n".join([f"<li>{html.escape(str(s))}</li>" for s in steps[:4]])

    schema_json = json.dumps({
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": util["title"],
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web Browser",
        "description": util["meta_description"],
        "url": canonical,
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD"
        },
        "publisher": {
            "@type": "Organization",
            "name": "FM Media Enterprises"
        }
    }, indent=2)

    inputs_html = ""
    for inp in util.get("inputs", []):
        inp_id = html.escape(inp["id"])
        inp_label = html.escape(inp["label"])
        inp_min = inp.get("min", 1)
        inp_max = inp.get("max", 100)
        inp_def = inp.get("default", 50)
        inp_weight = inp.get("weight", 1.0)
        inputs_html += f"""
        <div class="control-group">
          <div class="control-header">
            <label for="{inp_id}">{inp_label}</label>
            <span class="val-badge" id="val_{inp_id}">{inp_def}</span>
          </div>
          <input type="range" id="{inp_id}" min="{inp_min}" max="{inp_max}" value="{inp_def}"
                 data-weight="{inp_weight}" oninput="recalculate()">
        </div>
        """

    siblings = [u for u in all_utils if u["slug"] != slug][:4]
    sibling_links = "\n".join([
        f'<a class="mini-link" href="{utility_page_url(s["slug"])}">{html.escape(s["title"])} →</a>'
        for s in siblings
    ])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | FM Media Enterprises</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{canonical}">
  <script type="application/ld+json">
{schema_json}
  </script>
  <style>
    :root {{
      --bg: #0d1117;
      --surface: #161b22;
      --card-deep: #0b0f15;
      --border: #30363d;
      --text: #e6edf3;
      --muted: #8b949e;
      --accent: #2f81f7;
      --accent-hover: #58a6ff;
      --ok: #3fb950;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      line-height: 1.6;
      padding: 2rem 1rem 3.5rem;
    }}
    .container {{ max-width: 780px; margin: 0 auto; }}
    .top-bar {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; font-size: 0.85rem; color: var(--muted); margin-bottom: 1.25rem; }}
    .top-bar a {{ color: var(--accent); text-decoration: none; }}
    h1 {{ font-size: 1.95rem; line-height: 1.22; margin-bottom: 0.65rem; }}
    .subtitle {{ color: var(--muted); margin-bottom: 1.75rem; font-size: 1.05rem; }}
    .panel {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.75rem;
      margin-bottom: 1.5rem;
    }}
    .control-group {{ margin-bottom: 1.35rem; }}
    .control-header {{ display: flex; justify-content: space-between; gap: 1rem; margin-bottom: 0.45rem; font-weight: 500; }}
    .val-badge {{
      background: rgba(47, 129, 247, 0.16);
      color: var(--accent-hover);
      padding: 0.1rem 0.65rem;
      border-radius: 6px;
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }}
    input[type="range"] {{ width: 100%; accent-color: var(--accent); cursor: pointer; }}
    .result-box {{
      background: var(--card-deep);
      border: 1px solid var(--accent);
      border-radius: 10px;
      padding: 1.4rem;
      margin-top: 1.25rem;
    }}
    .result-label {{ font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); }}
    .result-metric {{ font-size: 2.3rem; font-weight: 700; color: var(--accent-hover); margin: 0.25rem 0 0.5rem; }}
    .result-verdict {{ font-size: 0.98rem; color: var(--text); margin-bottom: 1rem; }}
    .action-row {{ display: flex; gap: 0.75rem; flex-wrap: wrap; align-items: center; }}
    .copy-btn {{
      background: #21262d;
      color: var(--text);
      border: 1px solid var(--border);
      padding: 0.5rem 0.95rem;
      border-radius: 7px;
      font-size: 0.88rem;
      font-weight: 600;
      cursor: pointer;
    }}
    .copy-btn:hover {{ border-color: var(--accent); }}
    .copy-status {{ font-size: 0.85rem; color: var(--ok); min-height: 1.2em; }}
    .steps-list {{ padding-left: 1.2rem; display: grid; gap: 0.55rem; color: var(--text); }}
    .bridge-box {{
      background: linear-gradient(135deg, #161b22 0%, #0e1d33 100%);
      border: 1px solid var(--accent);
      border-radius: 12px;
      padding: 1.75rem;
      margin-bottom: 1.75rem;
    }}
    .bridge-pill {{
      display: inline-block;
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.06em;
      color: var(--accent-hover);
      background: rgba(47, 129, 247, 0.14);
      padding: 0.2rem 0.6rem;
      border-radius: 999px;
      margin-bottom: 0.65rem;
    }}
    .bridge-box h2 {{ font-size: 1.35rem; margin-bottom: 0.5rem; }}
    .bridge-box p {{ color: var(--muted); margin-bottom: 1.2rem; }}
    .cta-btn {{
      display: inline-block;
      background: var(--accent);
      color: #ffffff;
      font-weight: 600;
      padding: 0.78rem 1.4rem;
      border-radius: 8px;
      text-decoration: none;
    }}
    .cta-btn:hover {{ background: var(--accent-hover); }}
    .more-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.65rem; margin-top: 0.75rem; }}
    .mini-link {{
      display: block;
      background: var(--card-deep);
      border: 1px solid var(--border);
      padding: 0.75rem 0.9rem;
      border-radius: 8px;
      color: var(--accent);
      text-decoration: none;
      font-size: 0.9rem;
    }}
    .mini-link:hover {{ border-color: var(--accent); }}
  </style>
</head>
<body>
  <div class="container">
    <div class="top-bar">
      <a href="{hub_page_url()}">← All Standalone Tools</a>
      <span>Focus: {target_q}</span>
    </div>

    <h1>{title}</h1>
    <p class="subtitle">{desc}</p>

    <section class="panel">
      {inputs_html}
      <div class="result-box">
        <div class="result-label" id="outLabel">Output Metric</div>
        <div class="result-metric" id="outMetric">--</div>
        <div class="result-verdict" id="outVerdict">Move the sliders to calculate your baseline.</div>
        <div class="action-row">
          <button type="button" class="copy-btn" onclick="copySummary()">Copy Diagnostic Summary</button>
          <span class="copy-status" id="copyStatus"></span>
        </div>
      </div>
    </section>

    <section class="panel">
      <h2 style="font-size: 1.15rem; margin-bottom: 0.75rem;">Immediate Action Protocol</h2>
      <ol class="steps-list">
        {steps_html}
      </ol>
    </section>

    <section class="bridge-box">
      <span class="bridge-pill">{html.escape(bridge["badge"])}</span>
      <h2>{html.escape(bridge["headline"])}</h2>
      <p>{html.escape(bridge["subtext"])}</p>
      <a class="cta-btn" href="{bridge["url"]}">{html.escape(bridge["cta"])}</a>
    </section>

    <section class="panel">
      <h3 style="font-size: 0.98rem; color: var(--muted);">More Standalone Utilities</h3>
      <div class="more-grid">
        {sibling_links}
      </div>
    </section>
  </div>

  <script>
    const MODE = "{formula_mode}";
    const TOOL_TITLE = {json.dumps(util["title"])};
    let latestSummary = "";

    function recalculate() {{
      const sliders = document.querySelectorAll('input[type="range"]');
      let weightedSum = 0;
      let maxPossible = 0;

      sliders.forEach(s => {{
        const val = parseFloat(s.value);
        const max = parseFloat(s.max);
        const weight = parseFloat(s.dataset.weight || "1");
        document.getElementById("val_" + s.id).textContent = val;
        weightedSum += val * weight;
        maxPossible += max * weight;
      }});

      const ratio = maxPossible > 0 ? (weightedSum / maxPossible) : 0;
      const labelEl = document.getElementById("outLabel");
      const metricEl = document.getElementById("outMetric");
      const verdictEl = document.getElementById("outVerdict");

      if (MODE === "revenue_projection") {{
        const monthly = Math.round(weightedSum * 45);
        labelEl.textContent = "Estimated Monthly Monetization Potential";
        metricEl.textContent = "$" + monthly.toLocaleString() + " / mo";
        verdictEl.textContent = ratio >= 0.65
          ? "Strong upside potential. Packaging and shipping speed is your main lever right now."
          : "Increase your execution consistency or offer clarity to raise monthly return.";
      }} else if (MODE === "wealth_ratio") {{
        const runwayMonths = Math.max(1, Math.round(ratio * 18));
        labelEl.textContent = "Estimated Buffer & Leverage Index";
        metricEl.textContent = runwayMonths + " mos runway index";
        verdictEl.textContent = runwayMonths >= 10
          ? "Solid margin buffer. Direct surplus into compounding assets and high-leverage skills."
          : "Tight margin zone. Trim recurring leakages and build cash buffer before taking big bets.";
      }} else if (MODE === "time_saved") {{
        const hours = Math.max(1, Math.round(ratio * 24));
        labelEl.textContent = "Recoverable Weekly Execution Time";
        metricEl.textContent = hours + " hrs / week";
        verdictEl.textContent = hours >= 12
          ? "High time recovery window. Batching and cutting low-value loops can free over 10 hours a week."
          : "Moderate time gain. Protect one uninterrupted block daily to lift output.";
      }} else {{
        const score = Math.round(ratio * 100);
        labelEl.textContent = "Execution & System Readiness Score";
        metricEl.textContent = score + " / 100";
        verdictEl.textContent = score >= 75
          ? "High readiness. Execute directly instead of spending more time researching."
          : "Below optimal threshold. Simplify your current plan and fix the weakest slider first.";
      }}

      latestSummary = TOOL_TITLE + " -> " + labelEl.textContent + ": " + metricEl.textContent + " | " + verdictEl.textContent;
    }}

    function copySummary() {{
      const statusEl = document.getElementById("copyStatus");
      if (!navigator.clipboard) {{
        statusEl.textContent = "Select and copy result manually.";
        return;
      }}
      navigator.clipboard.writeText(latestSummary).then(() => {{
        statusEl.textContent = "Copied summary to clipboard.";
        setTimeout(() => {{ statusEl.textContent = ""; }}, 2500);
      }}).catch(() => {{
        statusEl.textContent = "Clipboard permission blocked in browser.";
      }});
    }}

    recalculate();
  </script>
</body>
</html>"""


def render_hub_page(utilities):
    cards = ""
    for u in utilities:
        slug = u["slug"]
        title = html.escape(u["title"])
        desc = html.escape(u["meta_description"])
        cards += f"""
        <a class="card" href="{utility_page_url(slug)}">
          <h3>{title}</h3>
          <p>{desc}</p>
          <span class="tag">Open Standalone Tool →</span>
        </a>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Standalone Operator Tools | FM Media Enterprises</title>
  <meta name="description" content="Interactive calculators, diagnostics, and action tools for self-improvement, mindset, personal finance, and solo builders.">
  <link rel="canonical" href="{hub_page_url()}">
  <style>
    :root {{ --bg: #0d1117; --surface: #161b22; --border: #30363d; --text: #e6edf3; --muted: #8b949e; --accent: #2f81f7; }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 2.5rem 1rem; }}
    .container {{ max-width: 920px; margin: 0 auto; }}
    h1 {{ font-size: 2.1rem; margin-bottom: 0.6rem; }}
    .lead {{ color: var(--muted); margin-bottom: 2.2rem; font-size: 1.05rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(270px, 1fr)); gap: 1.2rem; }}
    .card {{ display: block; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 1.4rem; text-decoration: none; color: inherit; transition: border-color 0.15s; }}
    .card:hover {{ border-color: var(--accent); }}
    .card h3 {{ font-size: 1.15rem; margin-bottom: 0.5rem; color: #ffffff; }}
    .card p {{ font-size: 0.92rem; color: var(--muted); margin-bottom: 1rem; }}
    .tag {{ font-size: 0.85rem; font-weight: 600; color: var(--accent); }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Standalone Operator Tools</h1>
    <p class="lead">Self-contained calculators and diagnostics built to diagnose bottlenecks and route action into your core systems.</p>
    <div class="grid">
      {cards}
    </div>
  </div>
</body>
</html>"""


def write_sitemap_and_robots(utilities):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    urls = [
        f"{BASE_URL}/",
        hub_page_url()
    ] + [utility_page_url(u["slug"]) for u in utilities]

    url_entries = "\n".join([
        f"""  <url>
    <loc>{u}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
  </url>"""
        for u in urls
    ])

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{url_entries}
</urlset>"""

    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap_xml)

    robots_txt = f"""User-agent: *
Allow: /

Sitemap: {BASE_URL}/sitemap.xml
"""
    with open("robots.txt", "w", encoding="utf-8") as f:
        f.write(robots_txt)


def main():
    if not os.path.exists("validated_demand.json"):
        raise FileNotFoundError("validated_demand.json not found. Run demand_harvester.py first.")

    with open("validated_demand.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    utilities = data.get("utilities", [])
    if not utilities:
        print("No utilities found in validated_demand.json.")
        return

    os.makedirs(TOOLS_DIR, exist_ok=True)

    with open(os.path.join(TOOLS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(render_hub_page(utilities))

    print("\nGenerated standalone utility URLs:")
    print(f"  Hub: {hub_page_url()}")
    for util in utilities:
        util_dir = os.path.join(TOOLS_DIR, util["slug"])
        os.makedirs(util_dir, exist_ok=True)
        out_path = os.path.join(util_dir, "index.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(render_utility_page(util, utilities))
        print(f"  - {utility_page_url(util['slug'])}")

    write_sitemap_and_robots(utilities)
    print(f"\nCompiled {len(utilities)} standalone utilities, hub index, sitemap.xml, and robots.txt.")


if __name__ == "__main__":
    main()
