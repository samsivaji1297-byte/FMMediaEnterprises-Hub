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
    "sovereignty": {
        "badge": "PSYCHOLOGICAL ARCHITECTURE",
        "headline": "Mental Sovereignty Framework: Psychological Architecture for Authentic Self-Recognition",
        "subtext": "Stop outsourcing your standards to external validation. Install the complete self-recognition architecture for unshakeable clarity, discipline, and internal authority.",
        "cta": "Access Mental Sovereignty Framework →",
        "url": "https://fmframeworks.gumroad.com/l/mentalsovereigntyframework"
    },
    "compression": {
        "badge": "90-MINUTE SPRINT SYSTEM",
        "headline": "The Compression System: Build a Sellable Digital Product in 90 Minutes",
        "subtext": "Eliminate weeks of planning drag. Architect, package, and launch a high-margin digital asset in one focused execution sprint.",
        "cta": "Get The Compression System →",
        "url": f"{BASE_URL}/go/compression/"
    }
}

ARCHETYPE_LABELS = {
    "sovereignty_diagnostic": "Mindset & Sovereignty Diagnostic",
    "financial_runway": "Financial Runway & Margin Analyzer",
    "revenue_calculator": "Monetization & Revenue Calculator",
    "execution_audit": "Execution Bandwidth & Focus Audit"
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
    archetype = util.get("archetype", "sovereignty_diagnostic")
    archetype_badge = html.escape(ARCHETYPE_LABELS.get(archetype, "Interactive Utility"))
    direct_answer = html.escape(util.get("direct_answer", desc))
    formula_mode = util.get("formula_mode", "readiness_score")
    bridge = OFFER_BRIDGES.get(util.get("bridge_offer", "sovereignty"), OFFER_BRIDGES["sovereignty"])
    canonical = utility_page_url(slug)

    protocols = util.get("protocols") or {
        "low": [
            "Audit your weakest metric first and remove the primary source of drag.",
            "Lock one non-negotiable daily execution window.",
            "Re-run this diagnostic in 7 days to verify movement."
        ],
        "mid": [
            "Standardize your daily baseline so results do not depend on mood.",
            "Eliminate secondary distractions during peak focus hours.",
            "Compound your strongest lever over the next 14 days."
        ],
        "high": [
            "Scale your active output—your current bottleneck is volume, not readiness.",
            "Codify your system into repeatable assets or higher-leverage plays.",
            "Protect your standards while expanding into higher-return opportunities."
        ]
    }
    protocols_json = json.dumps(protocols)

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
        inp_unit = html.escape(str(inp.get("unit", "")))
        inp_weight = inp.get("weight", 1.0)
        inputs_html += f"""
        <div class="control-group">
          <div class="control-header">
            <label for="{inp_id}">{inp_label}</label>
            <span class="val-badge" id="val_{inp_id}" data-unit="{inp_unit}">{inp_def}</span>
          </div>
          <input type="range" id="{inp_id}" min="{inp_min}" max="{inp_max}" value="{inp_def}"
                 data-weight="{inp_weight}" data-unit="{inp_unit}" oninput="recalculate()">
        </div>
        """

    # Cross-link across different archetypes so clicking leads to genuinely distinct tools
    distinct_siblings = [u for u in all_utils if u["slug"] != slug and u.get("archetype") != archetype][:2]
    same_siblings = [u for u in all_utils if u["slug"] != slug and u.get("archetype") == archetype][:2]
    related_list = (distinct_siblings + same_siblings)[:4]
    sibling_links = "\n".join([
        f"""<a class="mini-link" href="{utility_page_url(s["slug"])}">
          <span class="mini-type">{html.escape(ARCHETYPE_LABELS.get(s.get("archetype", ""), "Utility"))}</span>
          <strong>{html.escape(s["title"])} →</strong>
        </a>"""
        for s in related_list
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
      --warn: #d29922;
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
    .top-bar {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; font-size: 0.85rem; color: var(--muted); margin-bottom: 1rem; }}
    .top-bar a {{ color: var(--accent); text-decoration: none; }}
    .type-pill {{
      display: inline-block;
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: var(--accent-hover);
      background: rgba(47, 129, 247, 0.14);
      border: 1px solid rgba(47, 129, 247, 0.35);
      padding: 0.2rem 0.65rem;
      border-radius: 999px;
      margin-bottom: 0.75rem;
    }}
    h1 {{ font-size: 1.9rem; line-height: 1.24; margin-bottom: 0.75rem; }}
    .answer-box {{
      background: var(--surface);
      border-left: 3px solid var(--accent);
      padding: 0.95rem 1.15rem;
      border-radius: 0 8px 8px 0;
      color: var(--text);
      font-size: 0.98rem;
      margin-bottom: 1.6rem;
    }}
    .panel {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.75rem;
      margin-bottom: 1.5rem;
    }}
    .preset-row {{ display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1.4rem; align-items: center; }}
    .preset-label {{ font-size: 0.82rem; color: var(--muted); margin-right: 0.25rem; }}
    .preset-btn {{
      background: var(--card-deep);
      color: var(--text);
      border: 1px solid var(--border);
      padding: 0.35rem 0.75rem;
      border-radius: 6px;
      font-size: 0.82rem;
      cursor: pointer;
    }}
    .preset-btn:hover {{ border-color: var(--accent); color: var(--accent-hover); }}
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
    .result-metric {{ font-size: 2.3rem; font-weight: 700; color: var(--accent-hover); margin: 0.25rem 0 0.45rem; }}
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
    .protocol-header {{ display: flex; justify-content: space-between; align-items: center; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 0.85rem; }}
    .tier-badge {{
      font-size: 0.76rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      padding: 0.2rem 0.6rem;
      border-radius: 6px;
      background: rgba(63, 185, 80, 0.15);
      color: var(--ok);
    }}
    .steps-list {{ padding-left: 1.25rem; display: grid; gap: 0.6rem; color: var(--text); }}
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
    .bridge-box h2 {{ font-size: 1.32rem; margin-bottom: 0.5rem; line-height: 1.3; }}
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
    .more-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 0.75rem; margin-top: 0.85rem; }}
    .mini-link {{
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
      background: var(--card-deep);
      border: 1px solid var(--border);
      padding: 0.85rem 0.95rem;
      border-radius: 8px;
      color: var(--accent);
      text-decoration: none;
      font-size: 0.9rem;
    }}
    .mini-link:hover {{ border-color: var(--accent); }}
    .mini-type {{ font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); }}
  </style>
</head>
<body>
  <div class="container">
    <div class="top-bar">
      <a href="{hub_page_url()}">← All Standalone Tools</a>
      <span>Query Intent: {target_q}</span>
    </div>

    <span class="type-pill">{archetype_badge}</span>
    <h1>{title}</h1>
    <div class="answer-box">{direct_answer}</div>

    <section class="panel">
      <div class="preset-row">
        <span class="preset-label">Quick Scenario:</span>
        <button type="button" class="preset-btn" onclick="applyPreset(0.28)">Bottlenecked Baseline</button>
        <button type="button" class="preset-btn" onclick="applyPreset(0.58)">Stabilizing Operator</button>
        <button type="button" class="preset-btn" onclick="applyPreset(0.88)">High-Leverage Scale</button>
      </div>

      {inputs_html}

      <div class="result-box">
        <div class="result-label" id="outLabel">Calculated Output</div>
        <div class="result-metric" id="outMetric">--</div>
        <div class="result-verdict" id="outVerdict">Adjust the sliders above to calibrate your output.</div>
        <div class="action-row">
          <button type="button" class="copy-btn" onclick="copySummary()">Copy Diagnostic Brief</button>
          <span class="copy-status" id="copyStatus"></span>
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="protocol-header">
        <h2 style="font-size: 1.15rem;">Dynamic Action Protocol</h2>
        <span class="tier-badge" id="tierBadge">CALIBRATING</span>
      </div>
      <ol class="steps-list" id="protocolList"></ol>
    </section>

    <section class="bridge-box">
      <span class="bridge-pill">{html.escape(bridge["badge"])}</span>
      <h2>{html.escape(bridge["headline"])}</h2>
      <p>{html.escape(bridge["subtext"])}</p>
      <a class="cta-btn" href="{bridge["url"]}">{html.escape(bridge["cta"])}</a>
    </section>

    <section class="panel">
      <h3 style="font-size: 0.98rem; color: var(--muted);">Explore Different Diagnostic & Calculator Tools</h3>
      <div class="more-grid">
        {sibling_links}
      </div>
    </section>
  </div>

  <script>
    const MODE = "{formula_mode}";
    const TOOL_TITLE = {json.dumps(util["title"])};
    const PROTOCOLS = {protocols_json};
    let latestSummary = "";

    function formatBadge(val, unit) {{
      if (unit === "$") return "$" + Number(val).toLocaleString();
      if (unit) return val + " " + unit;
      return String(val);
    }}

    function applyPreset(factor) {{
      const sliders = document.querySelectorAll('input[type="range"]');
      sliders.forEach((s, idx) => {{
        const min = parseFloat(s.min);
        const max = parseFloat(s.max);
        // For burn rate in financial_runway (first slider), invert so high-leverage scale means controlled burn
        const effectiveFactor = (MODE === "wealth_ratio" && idx === 0) ? (1 - factor * 0.7) : factor;
        s.value = Math.round(min + (max - min) * effectiveFactor);
      }});
      recalculate();
    }}

    function renderProtocol(tierKey, badgeText) {{
      const badgeEl = document.getElementById("tierBadge");
      const listEl = document.getElementById("protocolList");
      badgeEl.textContent = badgeText;
      const steps = PROTOCOLS[tierKey] || PROTOCOLS["mid"];
      listEl.innerHTML = steps.map(step => "<li>" + step + "</li>").join("");
    }}

    function recalculate() {{
      const sliders = Array.from(document.querySelectorAll('input[type="range"]'));
      const vals = sliders.map(s => {{
        const val = parseFloat(s.value);
        const unit = s.dataset.unit || "";
        document.getElementById("val_" + s.id).textContent = formatBadge(val, unit);
        return val;
      }});

      const labelEl = document.getElementById("outLabel");
      const metricEl = document.getElementById("outMetric");
      const verdictEl = document.getElementById("outVerdict");
      let tier = "mid";
      let badgeText = "TIER 2 • STABILIZING";

      if (MODE === "revenue_projection") {{
        const price = vals[0] || 47;
        const weeklyBuyers = vals[1] || 10;
        const consistency = (vals[2] || 60) / 100;
        const monthly = Math.round(price * weeklyBuyers * 4.33 * consistency);
        labelEl.textContent = "Projected Monthly Digital Revenue";
        metricEl.textContent = "$" + monthly.toLocaleString() + " / mo";
        if (monthly < 1500) {{
          tier = "low";
          badgeText = "TIER 1 • VALIDATION PHASE";
          verdictEl.textContent = "Early traction zone. Focus on shipping a sharper offer and increasing weekly buyer traffic.";
        }} else if (monthly < 6000) {{
          tier = "mid";
          badgeText = "TIER 2 • MOMENTUM PHASE";
          verdictEl.textContent = "Solid unit economics. Raising price anchor or distribution cadence unlocks the next jump.";
        }} else {{
          tier = "high";
          badgeText = "TIER 3 • HIGH-LEVERAGE SCALE";
          verdictEl.textContent = "Strong revenue velocity. Your bottleneck is packaging higher-ticket tiers and automating distribution.";
        }}
      }} else if (MODE === "wealth_ratio") {{
        const burn = Math.max(500, vals[0] || 3000);
        const reserve = vals[1] || 12000;
        const surplusPct = vals[2] || 20;
        const runwayMonths = +(reserve / burn).toFixed(1);
        labelEl.textContent = "Liquid Runway & Surplus Margin";
        metricEl.textContent = runwayMonths + " mos (" + surplusPct + "% surplus)";
        if (runwayMonths < 3 || surplusPct < 10) {{
          tier = "low";
          badgeText = "TIER 1 • TIGHT BUFFER";
          verdictEl.textContent = "Vulnerable margin zone. Cut fixed burn first to build a protective cash floor.";
        }} else if (runwayMonths < 8 || surplusPct < 25) {{
          tier = "mid";
          badgeText = "TIER 2 • PROTECTED FLOOR";
          verdictEl.textContent = "Controlled baseline. Expand your surplus rate to accelerate compounding capital.";
        }} else {{
          tier = "high";
          badgeText = "TIER 3 • SOVEREIGN RUNWAY";
          verdictEl.textContent = "High financial insulation. Deploy surplus into asymmetric assets and owned systems.";
        }}
      }} else if (MODE === "time_saved") {{
        const lostHrs = vals[0] || 12;
        const switches = vals[1] || 10;
        const deepBlocks = vals[2] || 4;
        const reclaimable = Math.max(1, Math.round(lostHrs * 0.65 + switches * 0.25));
        labelEl.textContent = "Recoverable Weekly Execution Bandwidth";
        metricEl.textContent = reclaimable + " hrs / week";
        if (deepBlocks <= 2 || lostHrs >= 22) {{
          tier = "low";
          badgeText = "TIER 1 • HIGH FRICTION DRAG";
          verdictEl.textContent = "Heavy context switching is draining output. Cut low-value loops before adding new goals.";
        }} else if (deepBlocks <= 6) {{
          tier = "mid";
          badgeText = "TIER 2 • MODERATE DRAG";
          verdictEl.textContent = "Consistent baseline, but batching admin and automating workflows frees substantial hours.";
        }} else {{
          tier = "high";
          badgeText = "TIER 3 • HIGH-OUTPUT CADENCE";
          verdictEl.textContent = "Strong focus discipline. Reinvest reclaimed bandwidth into shipping high-leverage assets.";
        }}
      }} else {{
        let weightedSum = 0;
        let maxPossible = 0;
        sliders.forEach(s => {{
          const val = parseFloat(s.value);
          const max = parseFloat(s.max);
          const w = parseFloat(s.dataset.weight || "1");
          weightedSum += val * w;
          maxPossible += max * w;
        }});
        const score = maxPossible > 0 ? Math.round((weightedSum / maxPossible) * 100) : 0;
        labelEl.textContent = "Internal Authority & Execution Score";
        metricEl.textContent = score + " / 100";
        if (score < 45) {{
          tier = "low";
          badgeText = "TIER 1 • REACTIVE DRIFT";
          verdictEl.textContent = "High external drag detected. Strip distractions and lock one non-negotiable daily standard.";
        }} else if (score < 75) {{
          tier = "mid";
          badgeText = "TIER 2 • BUILDING AUTONOMY";
          verdictEl.textContent = "Solid foundation. Tighten impulse control under stress to lock in invariant execution.";
        }} else {{
          tier = "high";
          badgeText = "TIER 3 • SOVEREIGN EXECUTION";
          verdictEl.textContent = "High internal clarity. Stop over-researching and deploy directly into asymmetric execution.";
        }}
      }}

      renderProtocol(tier, badgeText);
      latestSummary = TOOL_TITLE + " -> " + labelEl.textContent + ": " + metricEl.textContent + " [" + badgeText + "] | " + verdictEl.textContent;
    }}

    function copySummary() {{
      const statusEl = document.getElementById("copyStatus");
      if (!navigator.clipboard) {{
        statusEl.textContent = "Select and copy result manually.";
        return;
      }}
      navigator.clipboard.writeText(latestSummary).then(() => {{
        statusEl.textContent = "Copied diagnostic brief to clipboard.";
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
        arch = html.escape(ARCHETYPE_LABELS.get(u.get("archetype", ""), "Standalone Tool"))
        cards += f"""
        <a class="card" href="{utility_page_url(slug)}">
          <span class="pill">{arch}</span>
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
  <title>Standalone Operator Tools & Diagnostics | FM Media Enterprises</title>
  <meta name="description" content="Interactive calculators, sovereignty diagnostics, runway analyzers, and execution audits for self-improvement, mindset, finances, and solo builders.">
  <link rel="canonical" href="{hub_page_url()}">
  <style>
    :root {{ --bg: #0d1117; --surface: #161b22; --border: #30363d; --text: #e6edf3; --muted: #8b949e; --accent: #2f81f7; }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 2.5rem 1rem; }}
    .container {{ max-width: 940px; margin: 0 auto; }}
    h1 {{ font-size: 2.1rem; margin-bottom: 0.6rem; }}
    .lead {{ color: var(--muted); margin-bottom: 2.2rem; font-size: 1.05rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.2rem; }}
    .card {{ display: block; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 1.4rem; text-decoration: none; color: inherit; transition: border-color 0.15s; }}
    .card:hover {{ border-color: var(--accent); }}
    .pill {{ display: inline-block; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--accent); margin-bottom: 0.5rem; font-weight: 700; }}
    .card h3 {{ font-size: 1.12rem; margin-bottom: 0.5rem; color: #ffffff; line-height: 1.3; }}
    .card p {{ font-size: 0.9rem; color: var(--muted); margin-bottom: 1rem; }}
    .tag {{ font-size: 0.85rem; font-weight: 600; color: var(--accent); }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Standalone Operator Tools</h1>
    <p class="lead">Self-contained calculators, financial runway analyzers, and sovereignty diagnostics engineered to solve real bottlenecks and route action into core systems.</p>
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
        print(f"  - [{util.get('archetype', 'tool')}] {utility_page_url(util['slug'])}")

    write_sitemap_and_robots(utilities)
    print(f"\nCompiled {len(utilities)} distinct standalone utilities, hub index, sitemap.xml, and robots.txt.")


if __name__ == "__main__":
    main()
