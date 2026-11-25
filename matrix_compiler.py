import os
import json
import html
from datetime import datetime

BASE_URL = os.environ.get("GSC_SITE_URL", "https://samsivaji1297-byte.github.io/FMMediaEnterprises-Hub").rstrip("/")
TOOLS_DIR = "tools"

OFFER_BRIDGES = {
    "compression": {
        "headline": "Want to Compress Your Entire Build Into 90 Minutes?",
        "subtext": "Stop spending weeks planning. Use The Compression System to architect, package, and launch a high-margin digital product in a single focused sprint.",
        "cta": "Access The Compression System ($197) →",
        "url": f"{BASE_URL}/go/compression/"
    },
    "operator": {
        "headline": "Eliminate Execution Friction & Cognitive Drag",
        "subtext": "Install the exact mental models, calibration protocols, and decision filters used by high-agency solo operators.",
        "cta": "Get the Operator Mindset Kit ($97) →",
        "url": "https://thefinalmindset.gumroad.com/l/operatormindsetkit"
    }
}


def render_utility_page(util, all_utils):
    slug = util["slug"]
    title = html.escape(util["title"])
    desc = html.escape(util["meta_description"])
    target_q = html.escape(util["target_query"])
    formula_mode = util.get("formula_mode", "readiness_score")
    bridge = OFFER_BRIDGES.get(util.get("bridge_offer", "compression"), OFFER_BRIDGES["compression"])
    canonical = f"{BASE_URL}/{TOOLS_DIR}/{slug}/"

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

    # Internal link cluster: link to 5 sibling utilities so authority compounds across the hub
    siblings = [u for u in all_utils if u["slug"] != slug][:5]
    sibling_links = "\n".join([
        f'<li><a href="{BASE_URL}/{TOOLS_DIR}/{s["slug"]}/">{html.escape(s["title"])}</a></li>'
        for s in siblings
    ])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | FM Media Systems</title>
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
      --border: #30363d;
      --text: #e6edf3;
      --muted: #8b949e;
      --accent: #2f81f7;
      --accent-hover: #58a6ff;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      line-height: 1.6;
      padding: 2rem 1rem;
    }}
    .container {{ max-width: 760px; margin: 0 auto; }}
    .breadcrumb {{ font-size: 0.85rem; color: var(--muted); margin-bottom: 1.25rem; }}
    .breadcrumb a {{ color: var(--accent); text-decoration: none; }}
    h1 {{ font-size: 1.9rem; line-height: 1.25; margin-bottom: 0.75rem; }}
    .subtitle {{ color: var(--muted); margin-bottom: 2rem; font-size: 1.05rem; }}
    .tool-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.75rem;
      margin-bottom: 2rem;
    }}
    .control-group {{ margin-bottom: 1.4rem; }}
    .control-header {{ display: flex; justify-content: space-between; margin-bottom: 0.45rem; font-weight: 500; }}
    .val-badge {{
      background: rgba(47, 129, 247, 0.15);
      color: var(--accent-hover);
      padding: 0.1rem 0.6rem;
      border-radius: 6px;
      font-variant-numeric: tabular-nums;
    }}
    input[type="range"] {{
      width: 100%;
      accent-color: var(--accent);
      cursor: pointer;
    }}
    .output-box {{
      background: #090d13;
      border: 1px solid var(--accent);
      border-radius: 10px;
      padding: 1.4rem;
      margin-top: 1.5rem;
      text-align: center;
    }}
    .output-label {{ font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); }}
    .output-metric {{ font-size: 2.4rem; font-weight: 700; color: var(--accent-hover); margin: 0.35rem 0; }}
    .output-insight {{ font-size: 0.95rem; color: var(--text); }}
    .bridge-box {{
      background: linear-gradient(135deg, #161b22 0%, #0f1c2e 100%);
      border: 1px solid var(--accent);
      border-radius: 12px;
      padding: 1.75rem;
      margin-bottom: 2.5rem;
    }}
    .bridge-box h2 {{ font-size: 1.3rem; margin-bottom: 0.5rem; }}
    .bridge-box p {{ color: var(--muted); margin-bottom: 1.2rem; }}
    .cta-btn {{
      display: inline-block;
      background: var(--accent);
      color: #ffffff;
      font-weight: 600;
      padding: 0.75rem 1.35rem;
      border-radius: 8px;
      text-decoration: none;
    }}
    .cta-btn:hover {{ background: var(--accent-hover); }}
    .cluster-nav {{ border-top: 1px solid var(--border); padding-top: 1.5rem; }}
    .cluster-nav h3 {{ font-size: 1rem; color: var(--muted); margin-bottom: 0.75rem; }}
    .cluster-nav ul {{ list-style: none; display: grid; gap: 0.5rem; }}
    .cluster-nav a {{ color: var(--accent); text-decoration: none; font-size: 0.95rem; }}
  </style>
</head>
<body>
  <div class="container">
    <nav class="breadcrumb">
      <a href="{BASE_URL}/{TOOLS_DIR}/">← All Operator Utilities</a> / <span>{target_q}</span>
    </nav>
    <h1>{title}</h1>
    <p class="subtitle">{desc}</p>

    <div class="tool-card">
      {inputs_html}
      <div class="output-box">
        <div class="output-label" id="outLabel">Calculated Output</div>
        <div class="output-metric" id="outMetric">--</div>
        <div class="output-insight" id="outInsight">Adjust the sliders above to run your diagnostic.</div>
      </div>
    </div>

    <div class="bridge-box">
      <h2>{html.escape(bridge["headline"])}</h2>
      <p>{html.escape(bridge["subtext"])}</p>
      <a class="cta-btn" href="{bridge["url"]}">{html.escape(bridge["cta"])}</a>
    </div>

    <div class="cluster-nav">
      <h3>Related Interactive Utilities</h3>
      <ul>
        {sibling_links}
      </ul>
    </div>
  </div>

  <script>
    const MODE = "{formula_mode}";
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
      const metricEl = document.getElementById("outMetric");
      const labelEl = document.getElementById("outLabel");
      const insightEl = document.getElementById("outInsight");

      if (MODE === "revenue_projection") {{
        const projected = Math.round(weightedSum * 42);
        labelEl.textContent = "Estimated Monthly Leverage Potential";
        metricEl.textContent = "$" + projected.toLocaleString() + " / mo";
        insightEl.textContent = ratio > 0.65
          ? "High unit economics detected. Your bottleneck is speed-to-ship, not market demand."
          : "Increase your price anchor or distribution volume to unlock asymmetric margin.";
      }} else if (MODE === "time_saved") {{
        const hours = Math.round(ratio * 28);
        labelEl.textContent = "Reclaimed Execution Bandwidth";
        metricEl.textContent = hours + " hrs / week";
        insightEl.textContent = hours >= 15
          ? "Significant operational drag identified. Automating or compressing these steps frees nearly half a workweek."
          : "Moderate friction. Consolidating your workflow into a single sprint removes context switching.";
      }} else {{
        const score = Math.round(ratio * 100);
        labelEl.textContent = "System Readiness Score";
        metricEl.textContent = score + " / 100";
        insightEl.textContent = score >= 75
          ? "Strong structural alignment. Ready for immediate deployment without further planning."
          : "Critical constraint detected below 75. Strip non-essential steps before scaling.";
      }}
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
        <a class="card" href="{BASE_URL}/{TOOLS_DIR}/{slug}/">
          <h3>{title}</h3>
          <p>{desc}</p>
          <span class="tag">Launch Utility →</span>
        </a>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Operator Micro-Utilities & Calculators | FM Media Enterprises</title>
  <meta name="description" content="Interactive calculators, readiness diagnostics, and workflow planners for solo digital product builders and high-agency operators.">
  <link rel="canonical" href="{BASE_URL}/{TOOLS_DIR}/">
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
    <h1>Operator Micro-Utilities</h1>
    <p class="lead">Zero-fluff calculators and diagnostic scorecards built for solo creators and digital product operators.</p>
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
        f"{BASE_URL}/{TOOLS_DIR}/"
    ] + [f"{BASE_URL}/{TOOLS_DIR}/{u['slug']}/" for u in utilities]

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

    # Write central hub page
    with open(os.path.join(TOOLS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(render_hub_page(utilities))

    # Write each micro-utility page
    for util in utilities:
        util_dir = os.path.join(TOOLS_DIR, util["slug"])
        os.makedirs(util_dir, exist_ok=True)
        with open(os.path.join(util_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(render_utility_page(util, utilities))

    write_sitemap_and_robots(utilities)
    print(f"Compiled {len(utilities)} interactive micro-utilities, hub index, sitemap.xml, and robots.txt.")


if __name__ == "__main__":
    main()
