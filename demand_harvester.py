import os
import re
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

# Focused domain seeds aligned with $27 Mental Sovereignty Framework & $197 The Compression System
SEED_TOPICS = [
    "self improvement",
    "masculinity discipline",
    "mindset shift",
    "self recognition",
    "mental sovereignty",
    "personal finance",
    "financial runway",
    "wealth building",
    "dopamine detox",
    "deep work",
    "digital product",
    "gumroad product",
    "solo business",
    "solo operator"
]

# Interactive utility-grade modifiers (prioritizes calculators, scorecards, and audits over generic templates)
INTENT_MODIFIERS = [
    "calculator",
    "scorecard",
    "audit",
    "system",
    "diagnostic",
    "planner",
    "checklist",
    "tracker"
]

ALPHABET_SWEEP = ["", " a", " c", " f", " m", " p", " s", " w"]

# Hard blocklist for informational definitions, finance admin/tax/accounting, spreadsheets, coding tutorials, and clinical/B2B noise
BLOCKED_PHRASES = [
    "what is ",
    "who is ",
    "define ",
    "definition",
    "meaning of",
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
    "for act",
    "act test",
    "sat test",
    "vehicle",
    "gps",
    "car tracker",
    "payroll",
    "hr software",
    "veterans",
    "amazon price",
    "price drop",
    "coupon",
    "software demo",
    "accounting",
    "agreement",
    "filing",
    "statement",
    "invoice",
    "contract",
    "tax return",
    "coding project",
    "free excel",
    "excel",
    "python",
    "apple numbers",
    "passport",
    "supply chain",
    "espr",
    "apa ",
    "spreadsheet",
    "google sheets",
    "notion template",
    "bank statement",
    "balance sheet",
    "income statement",
    "tax ",
    "irs ",
    "llc ",
    "dropshipping",
    "amazon fba",
    "credit score",
    "mortgage",
    "student loan"
]

WORD_BOUNDARY_BLOCKS = {
    "excel", "python", "espr", "apa", "gps", "for act", "act test", "sat test",
    "irs", "llc", "tax", "statement", "filing", "invoice", "contract", "agreement"
}

# Unambiguous domain anchors aligned with the four core utility pillars
REQUIRED_DOMAIN_ANCHORS = [
    "self improvement",
    "self-improvement",
    "masculinity",
    "masculine",
    "mindset",
    "self recognition",
    "self-recognition",
    "sovereignty",
    "discipline",
    "dopamine",
    "habit",
    "focus",
    "deep work",
    "personal finance",
    "wealth",
    "savings",
    "net worth",
    "financial runway",
    "budget",
    "debt payoff",
    "digital product",
    "gumroad",
    "solo business",
    "solo operator",
    "creator",
    "side hustle",
    "monetization"
]

# Active GroqCloud models
GROQ_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b"
]

ARCHETYPE_ORDER = [
    "sovereignty_diagnostic",
    "revenue_calculator",
    "financial_runway",
    "execution_audit"
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

CURATED_EVERGREEN_UTILITIES = [
    {
        "slug": "mental-sovereignty-self-recognition-audit",
        "title": "Mental Sovereignty & Self-Recognition Audit",
        "target_query": "self recognition mindset discipline scorecard",
        "meta_description": "Benchmark your internal frame, self-directed standards, and impulse control under pressure.",
        "archetype": "sovereignty_diagnostic",
        "direct_answer": "Score your internal validation independence, stress impulse control, and non-negotiable daily follow-through to locate your primary mindset leak."
    },
    {
        "slug": "masculine-discipline-consistency-diagnostic",
        "title": "Masculine Discipline & Frame Consistency Diagnostic",
        "target_query": "masculinity discipline system scorecard",
        "meta_description": "Measure daily execution consistency without motivation and identify external validation traps.",
        "archetype": "sovereignty_diagnostic",
        "direct_answer": "Quantify how reliably your standards hold under fatigue and distraction, then install a concrete daily sovereignty protocol."
    },
    {
        "slug": "mindset-shift-composure-readiness-scorecard",
        "title": "Mindset Shift & Emotional Composure Scorecard",
        "target_query": "mindset shift self improvement diagnostic",
        "meta_description": "Evaluate emotional neutrality, internal locus of control, and daily habit adherence.",
        "archetype": "sovereignty_diagnostic",
        "direct_answer": "Measure how strongly external feedback sways your decisions and generate a focused protocol to lock in self-directed standards."
    },
    {
        "slug": "digital-product-gumroad-revenue-calculator",
        "title": "Digital Product & Gumroad Revenue Calculator",
        "target_query": "gumroad digital product pricing revenue calculator",
        "meta_description": "Model offer price point, weekly buyer volume, and distribution consistency for solo digital products.",
        "archetype": "revenue_calculator",
        "direct_answer": "Project your realistic monthly cashflow by multiplying offer price, weekly buyer velocity, and distribution consistency."
    },
    {
        "slug": "solo-operator-offer-compression-calculator",
        "title": "Solo Operator Offer & Monetization Calculator",
        "target_query": "solo business monetization system calculator",
        "meta_description": "Calculate revenue upside from raising offer price anchors and tightening distribution cadence.",
        "archetype": "revenue_calculator",
        "direct_answer": "Determine whether your fastest revenue lever is lifting front-end ticket price, increasing weekly buyer conversion, or fixing distribution consistency."
    },
    {
        "slug": "creator-side-hustle-pricing-yield-calculator",
        "title": "Creator Product Pricing & Yield Calculator",
        "target_query": "digital product side hustle revenue calculator",
        "meta_description": "Forecast weekly and monthly revenue across entry and flagship digital product tiers.",
        "archetype": "revenue_calculator",
        "direct_answer": "Calculate exact weekly buyer volume required at your current price point to hit your monthly solo income target."
    },
    {
        "slug": "personal-finance-runway-leverage-calculator",
        "title": "Personal Finance Runway & Margin Calculator",
        "target_query": "personal finance runway wealth calculator",
        "meta_description": "Calculate months of sovereign financial runway from core burn, liquid reserves, and monthly surplus rate.",
        "archetype": "financial_runway",
        "direct_answer": "Measure how many months of independent operating runway your liquid reserve provides and how fast your current surplus rate expands your margin."
    },
    {
        "slug": "wealth-building-burn-buffer-analyzer",
        "title": "Wealth Building Burn & Buffer Analyzer",
        "target_query": "wealth building savings runway analyzer",
        "meta_description": "Benchmark your liquid floor against monthly overhead to unlock asymmetric decision-making.",
        "archetype": "financial_runway",
        "direct_answer": "Identify whether high fixed burn or a thin savings rate is keeping you in defensive mode, and generate a staged capital buffer plan."
    },
    {
        "slug": "net-worth-surplus-velocity-calculator",
        "title": "Net Worth & Savings Surplus Velocity Calculator",
        "target_query": "net worth savings rate financial runway calculator",
        "meta_description": "Estimate how quickly monthly surplus compounds into a 12-month sovereign reserve floor.",
        "archetype": "financial_runway",
        "direct_answer": "Compare your monthly burn against liquid reserves and surplus rate to see when you cross a resilient 6-to-12-month operating floor."
    },
    {
        "slug": "dopamine-detox-deep-work-bandwidth-audit",
        "title": "Dopamine Detox & Deep Work Bandwidth Audit",
        "target_query": "dopamine detox focus system audit",
        "meta_description": "Quantify weekly hours lost to context switching and calculate recoverable deep-work output.",
        "archetype": "execution_audit",
        "direct_answer": "Audit how many productive hours you lose each week to context switches and low-leverage tasks, then reclaim uninterrupted deep-work blocks."
    },
    {
        "slug": "solo-operator-execution-bottleneck-audit",
        "title": "Solo Operator Execution & Habit System Audit",
        "target_query": "habit discipline execution system audit",
        "meta_description": "Measure focus fragmentation against weekly shipped assets to eliminate operational drag.",
        "archetype": "execution_audit",
        "direct_answer": "Diagnose execution drag by comparing weekly distraction load against completed deep-work blocks to compress project ship cycles."
    },
    {
        "slug": "deep-work-time-compression-calculator",
        "title": "Deep Work & Time Compression Audit",
        "target_query": "deep work focus distraction audit calculator",
        "meta_description": "Calculate recoverable weekly execution hours by cutting context switches and batching low-leverage admin.",
        "archetype": "execution_audit",
        "direct_answer": "Estimate how many high-leverage hours you recover each month by eliminating context switches and protecting morning execution blocks."
    }
]


def is_niche_relevant(text):
    low = " " + re.sub(r"\s+", " ", str(text).lower().strip()) + " "
    for bad in BLOCKED_PHRASES:
        token = bad.strip()
        if token in WORD_BOUNDARY_BLOCKS:
            if re.search(rf"(?<!\w){re.escape(token)}(?!\w)", low):
                return False
        else:
            if bad in low:
                return False
    return any(anchor in low for anchor in REQUIRED_DOMAIN_ANCHORS)


def fetch_json_with_status(url, headers=None, timeout=10):
    req = urllib.request.Request(
        url,
        headers=headers or {"User-Agent": "Mozilla/5.0 (compatible; FMMediaIntentHarvester/2.3)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status_code = getattr(resp, "status", None) or resp.getcode()
            raw_text = resp.read().decode("utf-8", errors="replace")
            if not raw_text.strip():
                return None, status_code, "Empty response body"
            return json.loads(raw_text), status_code, None
    except urllib.error.HTTPError as e:
        err_snippet = ""
        try:
            err_snippet = e.read().decode("utf-8", errors="replace")[:200]
        except Exception:
            pass
        return None, e.code, f"HTTP {e.code}: {err_snippet}"
    except Exception as e:
        return None, None, str(e)


def harvest_autocomplete(query):
    results = set()
    q_enc = urllib.parse.quote(query)

    for url in [
        f"https://suggestqueries.google.com/complete/search?client=firefox&q={q_enc}",
        f"https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q={q_enc}",
        f"https://duckduckgo.com/ac/?q={q_enc}&type=list",
    ]:
        data, _, _ = fetch_json_with_status(url, timeout=10)
        if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
            results.update(str(item) for item in data[1] if item)

    return [item for item in results if is_niche_relevant(item)]


def harvest_marketplace_proof():
    """Extracts proven commercial phrasing from Gumroad buyer-intent probes."""
    proof_queries = []
    commercial_probes = [
        "site:gumroad.com/l/ mindset framework",
        "site:gumroad.com/l/ discipline system",
        "site:gumroad.com/l/ self improvement",
        "site:gumroad.com/l/ digital product",
        "site:gumroad.com/l/ personal finance runway",
        "site:gumroad.com/l/ solo business"
    ]
    for probe in commercial_probes:
        proof_queries.extend(harvest_autocomplete(probe))
        time.sleep(0.25)
    return list(set(proof_queries))


AUTOCOMPLETE_ARCHETYPE_PROBES = {
    "revenue_calculator": [
        "gumroad fee",
        "digital product pricing",
        "how to calculate digital product",
        "calculator for gumroad",
        "solo business monetization calculator",
        "creator side hustle pricing"
    ],
    "financial_runway": [
        "solo founder runway",
        "months of runway",
        "how to calculate financial runway",
        "calculator for personal finance",
        "personal finance months of runway",
        "savings financial runway calculator",
        "wealth building budget calculator"
    ],
    "execution_audit": [
        "burnout recovery audit",
        "dopamine detox tracker",
        "focus score audit",
        "execution checklist",
        "deep work execution checklist",
        "habit discipline burnout audit",
        "how to calculate deep work focus"
    ],
    "sovereignty_diagnostic": [
        "mental sovereignty mindset",
        "self recognition mindset",
        "masculinity discipline checklist",
        "self improvement discipline scorecard",
        "mindset shift self improvement",
        "how to measure self discipline",
        "calculator for habit discipline"
    ]
}


def harvest_google_autocomplete():
    """Lightweight unauthenticated Google Autocomplete signal pull across all 4 core archetypes."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        )
    }
    raw_count = 0
    probe_count = 0
    failures = []
    deduped = []
    seen_lower = set()

    for archetype, probes in AUTOCOMPLETE_ARCHETYPE_PROBES.items():
        for probe in probes:
            probe_count += 1
            q_enc = urllib.parse.quote(probe)
            url = f"https://suggestqueries.google.com/complete/search?client=firefox&q={q_enc}"
            data, status, err = fetch_json_with_status(url, headers=headers, timeout=5)
            if err:
                failures.append(f"{archetype}:'{probe}' -> {err}")
                time.sleep(0.15)
                continue

            if not (isinstance(data, list) and len(data) > 1 and isinstance(data[1], list)):
                failures.append(f"{archetype}:'{probe}' -> HTTP {status} unexpected payload")
                time.sleep(0.15)
                continue

            for item in data[1]:
                suggestion = re.sub(r"\s+", " ", str(item)).strip()
                if not suggestion:
                    continue
                raw_count += 1
                key = suggestion.lower()
                if key in seen_lower:
                    continue
                if is_niche_relevant(suggestion):
                    seen_lower.add(key)
                    deduped.append(suggestion)

            time.sleep(0.15)

    print(
        f"[Intent] Pulled {len(deduped)} live Google Autocomplete queries "
        f"({raw_count} raw suggestions across {probe_count} archetype probes)."
    )
    if failures:
        print(f"[Intent] Google Autocomplete notices: {' | '.join(failures[:3])}")

    return deduped

def harvest_gsc_telemetry():
    creds_raw = os.environ.get("GSC_CREDENTIALS_JSON", "").strip()
    site_url = os.environ.get("GSC_SITE_URL", "").strip()

    if not creds_raw or not site_url:
        print("[GSC] GSC_CREDENTIALS_JSON or GSC_SITE_URL not configured — skipping first-party telemetry.")
        return [], {}

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        creds_info = json.loads(creds_raw)
        credentials = service_account.Credentials.from_service_account_info(
            creds_info, scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
        )
        service = build("searchconsole", "v1", credentials=credentials)

        now_utc = datetime.now(timezone.utc)
        end_date = (now_utc - timedelta(days=3)).strftime("%Y-%m-%d")
        start_date = (now_utc - timedelta(days=33)).strftime("%Y-%m-%d")

        query_body = {
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

        query_resp = service.searchanalytics().query(siteUrl=site_url, body=query_body).execute()
        rows = query_resp.get("rows", [])
        niche_matched = 0
        opportunities = []

        for row in rows:
            query_text = row["keys"][0]
            if not is_niche_relevant(query_text):
                continue
            niche_matched += 1
            impressions = row.get("impressions", 0)
            position = row.get("position", 100)
            if impressions >= 10 and 7.0 <= position <= 30.0:
                opportunities.append({
                    "query": query_text,
                    "impressions": impressions,
                    "position": round(position, 1),
                    "source": "GSC"
                })

        page_body = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["page"],
            "rowLimit": 1000,
            "dataState": "final"
        }
        page_resp = service.searchanalytics().query(siteUrl=site_url, body=page_body).execute()
        page_metrics = {}
        for row in page_resp.get("rows", []):
            page_url = row["keys"][0]
            page_metrics[page_url] = {
                "clicks": int(row.get("clicks", 0)),
                "impressions": int(row.get("impressions", 0)),
                "position": round(float(row.get("position", 0.0)), 1)
            }

        if len(rows) == 0 and len(page_metrics) == 0:
            print(f"[GSC] Auth succeeded for {site_url}, but API returned 0 query/page rows ({start_date} to {end_date}).")
        else:
            print(
                f"[GSC] Query rows: {len(rows)} raw -> {niche_matched} niche-relevant -> "
                f"{len(opportunities)} striking-distance | Page rows tracked: {len(page_metrics)}."
            )
        return opportunities, page_metrics
    except Exception as e:
        print(f"[GSC] Telemetry check skipped safely due to error: {e}")
        return [], {}


def _parse_json_loose(raw_text):
    if raw_text is None:
        raise ValueError("Model returned None content")
    cleaned = str(raw_text).strip()
    cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL | re.IGNORECASE).strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    if not cleaned:
        raise ValueError("Model content was empty after stripping reasoning tags and markdown fences")

    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, list):
            return {"utilities": parsed}
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    obj_start, obj_end = cleaned.find("{"), cleaned.rfind("}")
    arr_start, arr_end = cleaned.find("["), cleaned.rfind("]")
    candidates = []
    if obj_start != -1 and obj_end > obj_start:
        candidates.append((obj_start, cleaned[obj_start:obj_end + 1]))
    if arr_start != -1 and arr_end > arr_start:
        candidates.append((arr_start, cleaned[arr_start:arr_end + 1]))
    candidates.sort(key=lambda x: x[0])

    for _, snippet in candidates:
        try:
            parsed = json.loads(snippet)
            if isinstance(parsed, list):
                return {"utilities": parsed}
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue

    raise ValueError(f"Could not extract valid JSON object/array from model output: {cleaned[:180]}")


def _pick_archetype(text, idx):
    low = text.lower()
    if any(k in low for k in ["gumroad", "digital product", "sell", "pricing", "revenue", "launch", "offer", "monetization", "side hustle", "solo business", "solo operator", "creator"]):
        return "revenue_calculator"
    if any(k in low for k in ["personal finance", "wealth", "savings", "net worth", "budget", "debt", "runway"]):
        return "financial_runway"
    if any(k in low for k in ["focus", "dopamine", "habit", "deep work", "productivity", "workflow", "routine", "execution"]):
        return "execution_audit"
    if any(k in low for k in ["mindset", "sovereignty", "recognition", "masculin", "discipline", "self improvement", "self-improvement"]):
        return "sovereignty_diagnostic"
    return ARCHETYPE_ORDER[idx % len(ARCHETYPE_ORDER)]


def _sanitize_slug(raw_slug, fallback_text):
    candidate = raw_slug or fallback_text or "diagnostic-tool"
    slug = re.sub(r"[^a-z0-9]+", "-", str(candidate).lower()).strip("-")
    slug = re.sub(r"^how-to-", "", slug).strip("-")
    return slug[:60].strip("-") or "diagnostic-tool"


def _enrich_utility(raw_util, idx):
    util = dict(raw_util)
    archetype = util.get("archetype")
    if archetype not in ARCHETYPE_TEMPLATES:
        archetype = _pick_archetype(f"{util.get('title', '')} {util.get('target_query', '')}", idx)

    tpl = ARCHETYPE_TEMPLATES[archetype]
    util["archetype"] = archetype
    util["formula_mode"] = tpl["formula_mode"]
    util["bridge_offer"] = tpl["bridge_offer"]
    util["slug"] = _sanitize_slug(util.get("slug", ""), util.get("title", "") or util.get("target_query", ""))
    util["title"] = str(util.get("title") or "Interactive Utility").strip()[:110]
    util["target_query"] = str(util.get("target_query") or util["title"]).strip()[:100]
    util["meta_description"] = str(util.get("meta_description") or f"Interactive diagnostic and calibrated action protocol for {util['target_query']}.").strip()[:155]

    raw_inputs = util.get("inputs")
    if not isinstance(raw_inputs, list) or len(raw_inputs) < 3:
        util["inputs"] = [dict(item) for item in tpl["inputs"]]
    else:
        normalized_inputs = []
        for i, inp in enumerate(raw_inputs[:3]):
            ref = tpl["inputs"][i]
            item = dict(inp) if isinstance(inp, dict) else {}
            item.setdefault("id", ref["id"])
            item.setdefault("label", ref["label"])
            item.setdefault("min", ref["min"])
            item.setdefault("max", ref["max"])
            item.setdefault("default", ref["default"])
            item.setdefault("unit", ref["unit"])
            item.setdefault("weight", ref["weight"])
            normalized_inputs.append(item)
        util["inputs"] = normalized_inputs

    raw_protocols = util.get("protocols") if isinstance(util.get("protocols"), dict) else {}
    normalized_protocols = {}
    for tier in ("low", "mid", "high"):
        steps = raw_protocols.get(tier)
        if isinstance(steps, list) and len([s for s in steps if str(s).strip()]) >= 2:
            normalized_protocols[tier] = [str(s).strip() for s in steps[:3]]
        else:
            normalized_protocols[tier] = list(tpl["protocols"][tier])
    util["protocols"] = normalized_protocols

    if not util.get("direct_answer"):
        util["direct_answer"] = (
            f"Use this interactive diagnostic to benchmark your current baseline for '{util['target_query']}', "
            f"spot your primary bottleneck, and generate a calibrated action protocol."
        )
    else:
        util["direct_answer"] = str(util["direct_answer"]).strip()

    return util


def _build_query_utility(query, idx, forced_archetype=None):
    cleaned = "".join(ch if ch.isalnum() or ch == " " else " " for ch in str(query).lower()).strip()
    words = [w for w in cleaned.split() if len(w) > 1]
    if words[:2] == ["how", "to"]:
        words = words[2:]
    if len(words) < 2:
        return None
    slug = "-".join(words[:6])[:55].strip("-")
    if not slug:
        return None

    archetype = forced_archetype or _pick_archetype(str(query), idx)
    suffix_label = {
        "revenue_calculator": "Revenue Calculator",
        "financial_runway": "Runway & Margin Analyzer",
        "execution_audit": "Execution Bandwidth Audit",
        "sovereignty_diagnostic": "Self-Recognition & Sovereignty Diagnostic"
    }[archetype]
    base_title = " ".join(w.capitalize() for w in words[:5])
    return _enrich_utility({
        "slug": slug,
        "title": f"{base_title}: {suffix_label}",
        "target_query": str(query)[:85],
        "meta_description": f"Interactive {suffix_label.lower()} and dynamic action protocol for {str(query)[:85]}.",
        "archetype": archetype
    }, idx)


def balance_utilities(primary_utilities, raw_candidates, target_total=14, max_per_archetype=4):
    """Caps single-archetype dominance and maintains even coverage across all 4 utility archetypes."""
    buckets = {arch: [] for arch in ARCHETYPE_ORDER}
    seen_slugs = set()
    seen_titles = set()

    def _try_add(util, target_bucket=None):
        arch = target_bucket or util["archetype"]
        if arch not in buckets or len(buckets[arch]) >= max_per_archetype:
            return False
        slug = util["slug"]
        title_key = util["title"].lower()
        if slug in seen_slugs or title_key in seen_titles:
            return False
        seen_slugs.add(slug)
        seen_titles.add(title_key)
        buckets[arch].append(util)
        return True

    for u in primary_utilities:
        _try_add(u)

    for arch in ARCHETYPE_ORDER:
        if len(buckets[arch]) >= 3:
            continue
        for idx, q in enumerate(raw_candidates):
            if len(buckets[arch]) >= 3:
                break
            if not is_niche_relevant(q):
                continue
            if _pick_archetype(str(q), idx) != arch:
                continue
            candidate_util = _build_query_utility(q, idx, forced_archetype=arch)
            if candidate_util:
                _try_add(candidate_util, target_bucket=arch)

    for idx, blueprint in enumerate(CURATED_EVERGREEN_UTILITIES):
        arch = blueprint["archetype"]
        if len(buckets[arch]) >= 3:
            continue
        enriched = _enrich_utility(blueprint, idx)
        _try_add(enriched, target_bucket=arch)

    balanced = []
    pos = 0
    while len(balanced) < target_total:
        added_this_round = False
        for arch in ARCHETYPE_ORDER:
            if pos < len(buckets[arch]) and len(balanced) < target_total:
                balanced.append(buckets[arch][pos])
                added_this_round = True
        if not added_this_round:
            break
        pos += 1

    counts = {arch: len([u for u in balanced if u["archetype"] == arch]) for arch in ARCHETYPE_ORDER}
    print(f"[Balance] Final utility distribution across archetypes: {counts}")
    return balanced


def _fallback_utilities_from_queries(raw_candidates):
    selected = []
    seen_slugs = set()

    for idx, q in enumerate(raw_candidates):
        if not is_niche_relevant(q):
            continue
        util = _build_query_utility(q, idx)
        if not util or util["slug"] in seen_slugs:
            continue
        seen_slugs.add(util["slug"])
        selected.append(util)
        if len(selected) >= 32:
            break

    return balance_utilities(selected, raw_candidates, target_total=14, max_per_archetype=4)


def _resolve_groq_models(headers):
    """Checks active models on the Groq key so unavailable IDs are skipped cleanly."""
    data, status, err = fetch_json_with_status(
        "https://api.groq.com/openai/v1/models",
        headers=headers,
        timeout=10
    )
    if err or not isinstance(data, dict) or not isinstance(data.get("data"), list):
        print(f"[Groq] Model catalog check unavailable ({err or f'HTTP {status}'}) — using default model list.")
        return list(GROQ_MODELS)

    available_ids = {m.get("id") for m in data["data"] if isinstance(m, dict) and m.get("id")}
    prioritized = [m for m in GROQ_MODELS if m in available_ids]
    if prioritized:
        print(f"[Groq] Active preferred models detected: {prioritized}")
        return prioritized

    excluded_tokens = ("whisper", "guard", "orpheus", "tts", "safeguard")
    dynamic_chat = sorted(
        mid for mid in available_ids
        if not any(tok in mid.lower() for tok in excluded_tokens)
    )
    if dynamic_chat:
        print(f"[Groq] Preferred models not found; trying available catalog models: {dynamic_chat[:4]}")
        return dynamic_chat[:4]

    return list(GROQ_MODELS)


def _call_groq_model(model_name, prompt, headers, use_reasoning_effort=True):
    body = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "Output raw JSON only. Never wrap in markdown fences or extra prose."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.25,
        "max_completion_tokens": 4096
    }
    if use_reasoning_effort:
        if model_name.startswith("openai/gpt-oss"):
            body["reasoning_effort"] = "low"
        elif model_name.startswith("qwen/"):
            body["reasoning_effort"] = "none"

    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        headers=headers
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        status_code = getattr(resp, "status", None) or resp.getcode()
        raw_body = resp.read().decode("utf-8", errors="replace")
        return status_code, raw_body


def filter_with_groq(raw_candidates):
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        print("[Groq] Missing GROQ_API_KEY — using niche-filtered balanced archetype fallback.")
        return _fallback_utilities_from_queries(raw_candidates)

    filtered_pool = [c for c in raw_candidates if is_niche_relevant(c)][:160]
    if not filtered_pool:
        filtered_pool = raw_candidates[:120]

    prompt = f"""You are a programmatic SEO and buyer-intent architect for a self-improvement, masculinity, mindset, personal finance, and solo-operator brand pointing toward two flagship offers: $27 Mental Sovereignty Framework ("sovereignty") and $197 The Compression System ("compression").
Analyze these raw search & buyer-intent signals:
{json.dumps(filtered_pool, indent=2)}

RULES:
1. DISCARD generic informational definitions ("what is...", "how to..."), accounting/tax/invoice/contract forms, Excel/spreadsheet/Python templates, vehicle GPS trackers, B2B payroll/HR software, and clinical/medical queries.
2. KEEP ONLY high-intent user/buyer queries that justify a standalone interactive tool across 4 distinct archetypes:
   - "sovereignty_diagnostic" (mindset, self-recognition, masculinity, discipline, emotional control -> bridge_offer: "sovereignty")
   - "financial_runway" (personal finance, burn rate, savings buffer, wealth leverage -> bridge_offer: "sovereignty")
   - "revenue_calculator" (digital products, pricing, Gumroad launches, solo monetization -> bridge_offer: "compression")
   - "execution_audit" (time wasted, focus, dopamine control, workflow bottlenecks -> bridge_offer: "compression")
3. Distribute 12 to 16 tools EVENLY across all 4 archetypes (3 to 4 per archetype — do NOT let any single archetype dominate). Use clean tool-style slugs (calculator, scorecard, audit, diagnostic, analyzer, planner) and never start a slug with "how-to-".
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
        "User-Agent": "Mozilla/5.0 (compatible; FMMediaIntentHarvester/2.3)"
    }

    models_to_try = _resolve_groq_models(headers)

    for model_name in models_to_try:
        for allow_reasoning_param in (True, False):
            try:
                status_code, raw_body = _call_groq_model(
                    model_name,
                    prompt,
                    headers,
                    use_reasoning_effort=allow_reasoning_param
                )
                if status_code != 200 or not raw_body.strip():
                    print(f"[Groq] {model_name} HTTP {status_code} empty/non-200 body: {raw_body[:300]}")
                    break

                try:
                    data = json.loads(raw_body)
                except json.JSONDecodeError as je:
                    print(f"[Groq] {model_name} HTTP {status_code} returned non-JSON body ({je}): {raw_body[:300]}")
                    break

                choices = data.get("choices") or []
                choice = choices[0] if choices else {}
                finish_reason = choice.get("finish_reason")
                message = choice.get("message") or {}
                content = message.get("content")

                if not content or not str(content).strip():
                    print(
                        f"[Groq] {model_name} HTTP {status_code} returned empty message content "
                        f"(finish_reason={finish_reason}): {raw_body[:300]}"
                    )
                    break

                parsed = _parse_json_loose(content)
                valid_utils = []
                for idx, u in enumerate(parsed.get("utilities", [])):
                    if not isinstance(u, dict):
                        continue
                    check_text = f"{u.get('title', '')} {u.get('target_query', '')}"
                    if is_niche_relevant(check_text):
                        valid_utils.append(_enrich_utility(u, idx))

                if valid_utils:
                    print(f"[Groq] Succeeded with {model_name} (HTTP {status_code}, {len(valid_utils)} niche-valid utilities before balancing)")
                    return balance_utilities(valid_utils, filtered_pool, target_total=14, max_per_archetype=4)

                print(f"[Groq] {model_name} HTTP {status_code} produced 0 niche-valid utilities. Content snippet: {str(content)[:300]}")
                break

            except urllib.error.HTTPError as e:
                err_body = ""
                try:
                    err_body = e.read().decode("utf-8", errors="replace")[:300]
                except Exception:
                    pass
                print(f"[Groq] {model_name} HTTP {e.code} error: {err_body}")
                if e.code == 400 and allow_reasoning_param and "reasoning_effort" in err_body:
                    print(f"[Groq] Retrying {model_name} without reasoning_effort parameter...")
                    continue
                break
            except Exception as e:
                print(f"[Groq] {model_name} failed ({type(e).__name__}): {e}")
                break

    print("[Groq] All model attempts failed — using niche-filtered balanced archetype fallback.")
    return _fallback_utilities_from_queries(raw_candidates)


def main():
    print("Starting multi-layer user & buyer intent harvest...")
    all_queries = set()

    for topic in SEED_TOPICS:
        for mod in INTENT_MODIFIERS[:4]:
            for suffix in ALPHABET_SWEEP[:4]:
                q = f"{topic} {mod}{suffix}".strip()
                all_queries.update(harvest_autocomplete(q))
                time.sleep(0.25)

    all_queries.update(harvest_marketplace_proof())
    all_queries.update(harvest_google_autocomplete())

    gsc_hits, gsc_page_metrics = harvest_gsc_telemetry()
    gsc_queries = [item["query"] for item in gsc_hits]

    combined_pool = gsc_queries + list(all_queries)
    print(f"Total niche-filtered buyer & user intent signals harvested: {len(combined_pool)}")

    utilities = filter_with_groq(combined_pool)
    output_payload = {
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "raw_signal_count": len(combined_pool),
        "gsc_opportunities": gsc_hits,
        "gsc_page_metrics": gsc_page_metrics,
        "utilities": utilities
    }

    with open("validated_demand.json", "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2)

    print(f"Saved {len(utilities)} balanced standalone utilities to validated_demand.json.")


if __name__ == "__main__":
    main()
