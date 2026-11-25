import os
import re
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

# Core pillars: self-improvement, masculinity, mindset, finances, and solo-operator leverage
SEED_TOPICS = [
    "self improvement system",
    "masculinity discipline",
    "mindset self recognition",
    "personal finance system",
    "wealth runway tracker",
    "dopamine focus protocol",
    "digital product launch",
    "solo business pricing"
]

# Transactional & high-friction buyer-intent modifiers
INTENT_MODIFIERS = [
    "calculator for",
    "template for",
    "system for",
    "tracker for",
    "checklist for",
    "scorecard for",
    "cost of",
    "worth it"
]

ALPHABET_SWEEP = ["", " a", " c", " f", " m", " p", " s", " w"]

BLOCKED_TERMS = [
    "psychiatry",
    "psychiatric",
    "phone number",
    "caller id",
    "diagnosis",
    "medical",
    "symptom",
    "prescription",
    "therapist",
    "insurance claim",
    "dsm-5",
    "icd-10"
]

NICHE_TERMS = [
    "self", "improvement", "masculin", "mindset", "discipline", "habit",
    "focus", "finance", "financial", "wealth", "money", "income", "savings",
    "invest", "debt", "runway", "gumroad", "digital product", "creator",
    "workflow", "system", "protocol", "scorecard", "calculator", "tracker",
    "routine", "pricing", "sovereignty", "recognition", "leverage"
]

GROQ_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant"
]

ARCHETYPE_TEMPLATES = {
    "revenue_calculator": {
        "formula_mode": "revenue_projection",
        "bridge_offer": "compression",
        "inputs": [
            {"id": "inp1", "label": "Offer Price Point ($)", "min": 10, "max": 500, "default": 47, "unit": "$", "weight": 1.0},
            {"id": "inp2", "label": "Target Weekly Buyers", "min": 1, "max": 100, "default": 12, "unit": "sales", "weight": 1.0},
            {"id": "inp3", "label": "Distribution Consistency (%)", "min": 10, "max": 100, "default": 60, "unit": "%", "weight": 1.0}
        ],
        "protocols": {
            "low": [
                "Validate buyer demand first: list one clear outcome-driven offer before building extra modules.",
                "Switch from passive posting to daily direct-intent distribution targeting active problem queries.",
                "Set a 7-day ship deadline to get your checkout link live in front of real traffic."
            ],
            "mid": [
                "Raise your front-end offer anchor or bundle a quick-start template to lift average order value.",
                "Replace manual posting with scheduled multi-channel distribution pointing to one checkout route.",
                "Track conversion rate per 100 clicks and rewrite your headline around the #1 buyer objection."
            ],
            "high": [
                "Introduce a high-margin $197+ implementation tier or flagship system alongside your entry offer.",
                "Automate traffic harvesting across search utilities and evergreen distribution loops.",
                "Reinvest surplus cashflow into scalable acquisition assets while keeping overhead near zero."
            ]
        }
    },
    "financial_runway": {
        "formula_mode": "wealth_ratio",
        "bridge_offer": "sovereignty",
        "inputs": [
            {"id": "inp1", "label": "Monthly Core Burn ($)", "min": 500, "max": 15000, "default": 3200, "unit": "$", "weight": 1.0},
            {"id": "inp2", "label": "Liquid Reserve Buffer ($)", "min": 500, "max": 100000, "default": 15000, "unit": "$", "weight": 1.0},
            {"id": "inp3", "label": "Monthly Savings / Surplus Rate (%)", "min": 0, "max": 80, "default": 22, "unit": "%", "weight": 1.0}
        ],
        "protocols": {
            "low": [
                "Audit recurring subscriptions and low-ROI spending within 24 hours to cut monthly burn by 15%.",
                "Build an immediate 3-month liquid floor before taking on volatile risks or lifestyle upgrades.",
                "Ring-fence a fixed percentage of every incoming dollar into an untouched reserve account."
            ],
            "mid": [
                "Push your liquid buffer past 6 months of core expenses to eliminate defensive decision-making.",
                "Separate operating cash from compounding capital so surplus automatically builds asymmetric upside.",
                "Cap fixed lifestyle overhead while scaling independent income streams."
            ],
            "high": [
                "Your runway gives you high strategic leverage—deploy excess capital into cash-flowing assets.",
                "Shift focus from defensive budgeting to asymmetric skill and ownership bets.",
                "Review asset allocation quarterly to prevent idle cash drag while preserving your core floor."
            ]
        }
    },
    "execution_audit": {
        "formula_mode": "time_saved",
        "bridge_offer": "compression",
        "inputs": [
            {"id": "inp1", "label": "Weekly Hours Lost to Low-Leverage Tasks", "min": 1, "max": 40, "default": 14, "unit": "hrs", "weight": 1.0},
            {"id": "inp2", "label": "Daily Context Switches / Distractions", "min": 1, "max": 30, "default": 10, "unit": "x", "weight": 1.0},
            {"id": "inp3", "label": "Deep Work Blocks Completed / Week", "min": 0, "max": 14, "default": 4, "unit": "blocks", "weight": 1.0}
        ],
        "protocols": {
            "low": [
                "Eliminate non-essential notifications and batch communications into two 20-minute windows daily.",
                "Protect one uninterrupted 90-minute execution block every morning before opening feeds.",
                "Cut or automate the single repetitive task consuming the most weekly hours."
            ],
            "mid": [
                "Standardize your top recurring workflow into a repeatable checklist or script to remove friction.",
                "Stack deep-work blocks on your highest-energy days and push admin to low-energy hours.",
                "Measure output by shipped assets per week rather than hours spent at the screen."
            ],
            "high": [
                "Your execution cadence is tight—delegate or script remaining maintenance steps to free 10+ hrs/wk.",
                "Compress multi-week projects into single-sprint launches using repeatable templates.",
                "Protect your recovered bandwidth strictly for high-leverage strategic moves."
            ]
        }
    },
    "sovereignty_diagnostic": {
        "formula_mode": "readiness_score",
        "bridge_offer": "sovereignty",
        "inputs": [
            {"id": "inp1", "label": "Self-Directed Standards vs External Validation (1-100)", "min": 1, "max": 100, "default": 58, "unit": "/100", "weight": 1.25},
            {"id": "inp2", "label": "Impulse & Dopamine Control Under Stress (1-100)", "min": 1, "max": 100, "default": 52, "unit": "/100", "weight": 1.15},
            {"id": "inp3", "label": "Daily Follow-Through Without Motivation (1-100)", "min": 1, "max": 100, "default": 60, "unit": "/100", "weight": 1.2}
        ],
        "protocols": {
            "low": [
                "Strip external noise for 72 hours: audit where social comparison or validation dictates your choices.",
                "Establish one non-negotiable daily rule you execute regardless of mood or energy.",
                "Replace reactive scrolling with deliberate physical resets and written self-audits."
            ],
            "mid": [
                "Identify the specific pressure trigger where your standards slip and install a pre-committed rule.",
                "Shift from sporadic intensity to invariant daily execution tracked objectively each evening.",
                "Audit your inner circle and information inputs to align with sovereign, self-directed standards."
            ],
            "high": [
                "Your internal frame is locked in—channel this stability into high-stakes creative or financial execution.",
                "Codify your personal operating principles so decisions require zero emotional deliberation.",
                "Expand your scope: take on larger asymmetric challenges where composure is the primary edge."
            ]
        }
    }
}


def is_niche_relevant(text):
    low = str(text).lower()
    if any(bad in low for bad in BLOCKED_TERMS):
        return False
    return any(good in low for good in NICHE_TERMS)


def fetch_json(url, headers=None, timeout=10):
    req = urllib.request.Request(
        url,
        headers=headers or {"User-Agent": "Mozilla/5.0 (compatible; FMMediaIntentHarvester/2.0)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def harvest_autocomplete(query):
    results = set()
    q_enc = urllib.parse.quote(query)

    for url in [
        f"https://suggestqueries.google.com/complete/search?client=firefox&q={q_enc}",
        f"https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q={q_enc}",
        f"https://duckduckgo.com/ac/?q={q_enc}&type=list",
    ]:
        data = fetch_json(url)
        if isinstance(data, list) and len(data) > 1:
            results.update(data[1])

    return [item for item in results if is_niche_relevant(item)]


def harvest_marketplace_proof():
    """Extracts proven commercial phrasing from Gumroad & Etsy buyer-intent probes."""
    proof_queries = []
    commercial_probes = [
        "site:gumroad.com/l/ mindset framework",
        "site:gumroad.com/l/ personal finance tracker",
        "site:gumroad.com/l/ discipline system",
        "site:etsy.com/listing/ budget runway tracker",
        "site:etsy.com/listing/ habit discipline planner"
    ]
    for probe in commercial_probes:
        proof_queries.extend(harvest_autocomplete(probe))
        time.sleep(0.3)
    return list(set(proof_queries))


def harvest_live_community_intent():
    """Fault-tolerant pull of active buyer/user questions from public Reddit & StackExchange JSON."""
    intent_phrases = set()

    # 1. StackExchange Money / Personal Finance & Productivity active questions
    se_urls = [
        "https://api.stackexchange.com/2.3/search/excerpts?order=desc&sort=votes&q=runway%20savings%20system&site=money&pagesize=15",
        "https://api.stackexchange.com/2.3/search/excerpts?order=desc&sort=votes&q=discipline%20focus%20routine&site=productivity&pagesize=15"
    ]
    for url in se_urls:
        data = fetch_json(url, timeout=8)
        if isinstance(data, dict):
            for item in data.get("items", []):
                title = item.get("title", "")
                if title and is_niche_relevant(title):
                    intent_phrases.add(title)

    # 2. Reddit public search JSON (gracefully skips if runner IP is throttled)
    reddit_queries = [
        "https://www.reddit.com/r/selfimprovement/search.json?q=system+OR+framework+OR+tracker&restrict_sr=1&sort=top&t=month&limit=15",
        "https://www.reddit.com/r/personalFinance/search.json?q=runway+OR+calculator+OR+tracker&restrict_sr=1&sort=top&t=month&limit=15",
        "https://www.reddit.com/r/Entrepreneur/search.json?q=digital+product+pricing+OR+gumroad&restrict_sr=1&sort=top&t=month&limit=15"
    ]
    for r_url in reddit_queries:
        data = fetch_json(
            r_url,
            headers={"User-Agent": "python:fmmedia.intent.harvester:v2.0 (by /u/fmmedia_bot)"},
            timeout=8
        )
        if isinstance(data, dict):
            children = data.get("data", {}).get("children", [])
            for child in children:
                title = child.get("data", {}).get("title", "")
                if title and is_niche_relevant(title):
                    intent_phrases.add(title)
        time.sleep(0.4)

    print(f"[Intent] Pulled {len(intent_phrases)} live community & Q&A buyer-intent signals.")
    return list(intent_phrases)


def harvest_gsc_telemetry():
    creds_raw = os.environ.get("GSC_CREDENTIALS_JSON", "").strip()
    site_url = os.environ.get("GSC_SITE_URL", "").strip()

    if not creds_raw or not site_url:
        print("[GSC] Credentials or GSC_SITE_URL not set yet — skipping first-party telemetry.")
        return []

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        creds_info = json.loads(creds_raw)
        credentials = service_account.Credentials.from_service_account_info(
            creds_info, scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
        )
        service = build("searchconsole", "v1", credentials=credentials)

        end_date = (datetime.utcnow() - timedelta(days=3)).strftime("%Y-%m-%d")
        start_date = (datetime.utcnow() - timedelta(days=33)).strftime("%Y-%m-%d")

        request_body = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["query"],
            "dimensionFilterGroups": [
                {
                    "filters": [
                        {
                            "dimension": "brandedClassification",
                            "operator": "equals",
                            "expression": "NON_BRANDED"
                        }
                    ]
                }
            ],
            "rowLimit": 5000,
            "dataState": "final"
        }

        response = service.searchanalytics().query(siteUrl=site_url, body=request_body).execute()
        opportunities = []
        for row in response.get("rows", []):
            query_text = row["keys"][0]
            if not is_niche_relevant(query_text):
                continue
            impressions = row.get("impressions", 0)
            position = row.get("position", 100)
            if impressions >= 10 and 7.0 <= position <= 30.0:
                opportunities.append({
                    "query": query_text,
                    "impressions": impressions,
                    "position": round(position, 1),
                    "source": "GSC"
                })
        print(f"[GSC] Extracted {len(opportunities)} niche striking-distance queries.")
        return opportunities
    except Exception as e:
        print(f"[GSC] Telemetry check skipped due to error: {e}")
        return []


def _parse_json_loose(raw_text):
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start:end + 1]
    return json.loads(cleaned)


def _pick_archetype(text, idx):
    low = text.lower()
    if any(k in low for k in ["gumroad", "digital product", "sell", "pricing", "revenue", "launch", "offer", "income"]):
        return "revenue_calculator"
    if any(k in low for k in ["finance", "money", "wealth", "invest", "savings", "debt", "budget", "runway", "cost"]):
        return "financial_runway"
    if any(k in low for k in ["time", "workflow", "routine", "focus", "dopamine", "schedule", "productivity"]):
        return "execution_audit"
    if any(k in low for k in ["mindset", "sovereignty", "recognition", "masculin", "discipline", "self improvement", "habit"]):
        return "sovereignty_diagnostic"
    order = ["sovereignty_diagnostic", "revenue_calculator", "financial_runway", "execution_audit"]
    return order[idx % len(order)]


def _enrich_utility(raw_util, idx):
    archetype = raw_util.get("archetype")
    if archetype not in ARCHETYPE_TEMPLATES:
        archetype = _pick_archetype(raw_util.get("title", "") + " " + raw_util.get("target_query", ""), idx)

    tpl = ARCHETYPE_TEMPLATES[archetype]
    raw_util["archetype"] = archetype
    raw_util["formula_mode"] = tpl["formula_mode"]
    raw_util["bridge_offer"] = raw_util.get("bridge_offer") if raw_util.get("bridge_offer") in ("sovereignty", "compression") else tpl["bridge_offer"]

    if not raw_util.get("inputs") or len(raw_util["inputs"]) < 3:
        raw_util["inputs"] = tpl["inputs"]
    else:
        for i, inp in enumerate(raw_util["inputs"][:3]):
            ref = tpl["inputs"][i]
            inp.setdefault("min", ref["min"])
            inp.setdefault("max", ref["max"])
            inp.setdefault("default", ref["default"])
            inp.setdefault("unit", ref["unit"])
            inp.setdefault("weight", ref["weight"])

    raw_util["protocols"] = raw_util.get("protocols") if isinstance(raw_util.get("protocols"), dict) else tpl["protocols"]
    for tier in ("low", "mid", "high"):
        if not raw_util["protocols"].get(tier):
            raw_util["protocols"][tier] = tpl["protocols"][tier]

    if not raw_util.get("direct_answer"):
        raw_util["direct_answer"] = (
            f"Use this interactive diagnostic to benchmark your current baseline for '{raw_util.get('target_query', raw_util.get('title', 'this system'))}', "
            f"spot your primary bottleneck, and generate a calibrated action protocol."
        )
    return raw_util


def _fallback_utilities_from_queries(raw_candidates):
    selected = []
    seen_slugs = set()

    for q in raw_candidates:
        if not is_niche_relevant(q):
            continue
        cleaned = "".join(ch if ch.isalnum() or ch == " " else " " for ch in str(q).lower()).strip()
        words = [w for w in cleaned.split() if len(w) > 1]
        if len(words) < 3:
            continue
        slug = "-".join(words[:6])[:55].strip("-")
        if not slug or slug in seen_slugs:
            continue
        seen_slugs.add(slug)

        idx = len(selected)
        archetype = _pick_archetype(str(q), idx)
        suffix_label = {
            "revenue_calculator": "Revenue Calculator",
            "financial_runway": "Runway & Margin Analyzer",
            "execution_audit": "Execution Bandwidth Audit",
            "sovereignty_diagnostic": "Self-Recognition & Sovereignty Diagnostic"
        }[archetype]

        base_title = " ".join(w.capitalize() for w in words[:5])
        util = _enrich_utility({
            "slug": slug,
            "title": f"{base_title}: {suffix_label}",
            "target_query": str(q)[:85],
            "meta_description": f"Interactive {suffix_label.lower()} and dynamic action protocol for {str(q)[:85]}.",
            "archetype": archetype
        }, idx)
        selected.append(util)
        if len(selected) >= 14:
            break

    return selected


def filter_with_groq(raw_candidates):
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        print("[Groq] Missing GROQ_API_KEY — using niche-filtered archetype fallback.")
        return _fallback_utilities_from_queries(raw_candidates)

    filtered_pool = [c for c in raw_candidates if is_niche_relevant(c)][:160]
    if not filtered_pool:
        filtered_pool = raw_candidates[:120]

    prompt = f"""You are a programmatic SEO and buyer-intent architect for a self-improvement, masculinity, mindset, personal finance, and solo-operator brand.
Analyze these raw search & buyer-intent signals:
{json.dumps(filtered_pool, indent=2)}

RULES:
1. DISCARD generic informational fluff and off-topic queries (medical, psychiatry, phone numbers).
2. KEEP ONLY high-intent user/buyer queries that justify a standalone interactive tool across 4 distinct archetypes:
   - "sovereignty_diagnostic" (mindset, self-recognition, masculinity, discipline, emotional control -> bridge_offer: "sovereignty")
   - "financial_runway" (personal finance, burn rate, savings buffer, wealth leverage -> bridge_offer: "sovereignty")
   - "revenue_calculator" (digital products, pricing, Gumroad launches, solo monetization -> bridge_offer: "compression")
   - "execution_audit" (time wasted, focus, workflow bottlenecks, deep work -> bridge_offer: "compression")
3. Distribute the 12 to 16 tools evenly across all 4 archetypes so the site has genuine functional variety.
4. For each tool, write a sharp 1-sentence "direct_answer" that immediately answers the user's underlying question, plus tailored "low", "mid", and "high" action protocols (3 steps each).

Return ONLY valid JSON:
{{
  "utilities": [
    {{
      "slug": "kebab-case-slug",
      "title": "Distinct Tool Title",
      "target_query": "exact buyer or user query",
      "meta_description": "Under 155 chars description",
      "archetype": "sovereignty_diagnostic",
      "direct_answer": "Direct plain-English answer to the user's question.",
      "bridge_offer": "sovereignty",
      "protocols": {{
        "low": ["Low tier step 1", "Low tier step 2", "Low tier step 3"],
        "mid": ["Mid tier step 1", "Mid tier step 2", "Mid tier step 3"],
        "high": ["High tier scaling step 1", "High tier scaling step 2", "High tier scaling step 3"]
      }}
    }}
  ]
}}
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; FMMediaIntentHarvester/2.0)"
    }

    for model_name in GROQ_MODELS:
        payload = json.dumps({
            "model": model_name,
            "messages": [
                {"role": "system", "content": "Output raw JSON only. Never wrap in markdown fences."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.25
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload,
            headers=headers
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                parsed = _parse_json_loose(content)
                valid_utils = []
                for idx, u in enumerate(parsed.get("utilities", [])):
                    if is_niche_relevant(u.get("title", "") + " " + u.get("target_query", "")):
                        valid_utils.append(_enrich_utility(u, idx))
                if valid_utils:
                    print(f"[Groq] Succeeded with model: {model_name} ({len(valid_utils)} distinct utilities)")
                    return valid_utils
        except urllib.error.HTTPError as e:
            err_body = ""
            try:
                err_body = e.read().decode("utf-8", errors="replace")[:250]
            except Exception:
                pass
            print(f"[Groq] {model_name} failed ({e.code}): {err_body}")
        except Exception as e:
            print(f"[Groq] {model_name} failed: {e}")

    print("[Groq] All model attempts failed — using niche-filtered archetype fallback.")
    return _fallback_utilities_from_queries(raw_candidates)


def main():
    print("Starting multi-layer user & buyer intent harvest...")
    all_queries = set()

    for topic in SEED_TOPICS:
        for mod in INTENT_MODIFIERS[:4]:
            for suffix in ALPHABET_SWEEP[:4]:
                q = f"{mod} {topic}{suffix}".strip()
                all_queries.update(harvest_autocomplete(q))
                time.sleep(0.25)

    all_queries.update(harvest_marketplace_proof())
    all_queries.update(harvest_live_community_intent())

    gsc_hits = harvest_gsc_telemetry()
    gsc_queries = [item["query"] for item in gsc_hits]

    combined_pool = gsc_queries + list(all_queries)
    print(f"Total niche-filtered buyer & user intent signals harvested: {len(combined_pool)}")

    utilities = filter_with_groq(combined_pool)
    output_payload = {
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "raw_signal_count": len(combined_pool),
        "gsc_opportunities": gsc_hits,
        "utilities": utilities
    }

    with open("validated_demand.json", "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2)

    print(f"Saved {len(utilities)} standalone utilities to validated_demand.json.")


if __name__ == "__main__":
    main()
