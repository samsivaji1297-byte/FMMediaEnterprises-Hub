import os
import re
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

SEED_TOPICS = [
    "self improvement system",
    "masculinity framework",
    "mindset discipline",
    "personal finance system",
    "wealth building tracker",
    "focus and dopamine control",
    "digital product launch",
    "solo operator workflow"
]

TOOL_MODIFIERS = [
    "calculator for",
    "scorecard for",
    "diagnostic for",
    "tracker for",
    "plan for",
    "audit for",
    "blueprint for",
    "ratio calculator"
]

ALPHABET_SWEEP = ["", " a", " b", " c", " d", " f", " m", " s", " w"]

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
    "invest", "debt", "gumroad", "digital product", "creator", "workflow",
    "system", "protocol", "scorecard", "calculator", "tracker", "routine"
]

GROQ_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant"
]


def is_niche_relevant(text):
    low = str(text).lower()
    if any(bad in low for bad in BLOCKED_TERMS):
        return False
    return any(good in low for good in NICHE_TERMS)


def fetch_json(url, headers=None, timeout=10):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "Mozilla/5.0"})
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
    proof_queries = []
    commercial_probes = [
        "site:gumroad.com/l/ mindset system",
        "site:gumroad.com/l/ finance tracker",
        "site:gumroad.com/l/ habit protocol",
        "site:etsy.com/listing/ personal finance tracker"
    ]
    for probe in commercial_probes:
        proof_queries.extend(harvest_autocomplete(probe))
        time.sleep(0.35)
    return list(set(proof_queries))


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


def _infer_bridge_and_mode(text, idx):
    low = text.lower()
    if any(k in low for k in ["gumroad", "digital product", "sell", "pricing", "revenue", "launch", "offer"]):
        return "revenue_projection", "compression"
    if any(k in low for k in ["finance", "money", "wealth", "invest", "savings", "debt", "budget", "income"]):
        return "wealth_ratio", "operator"
    if any(k in low for k in ["time", "workflow", "routine", "habit", "focus", "dopamine", "schedule"]):
        return "time_saved", "operator"
    modes = ["readiness_score", "time_saved", "wealth_ratio", "revenue_projection"]
    bridges = ["operator", "compression"]
    return modes[idx % len(modes)], bridges[idx % len(bridges)]


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
        mode, bridge = _infer_bridge_and_mode(str(q), idx)
        title = " ".join(w.capitalize() for w in words[:6]) + " Tool"
        selected.append({
            "slug": slug,
            "title": title,
            "target_query": str(q)[:80],
            "meta_description": f"Standalone interactive calculator and action plan for {str(q)[:92]}.",
            "tool_type": "calculator",
            "inputs": [
                {"id": "inp1", "label": "Baseline Consistency (1-100)", "min": 1, "max": 100, "default": 50, "weight": 1.2},
                {"id": "inp2", "label": "Execution Friction / Drag (1-100)", "min": 1, "max": 100, "default": 55, "weight": 1.0},
                {"id": "inp3", "label": "Weekly Target Commitment (1-100)", "min": 1, "max": 100, "default": 65, "weight": 1.15}
            ],
            "formula_mode": mode,
            "bridge_offer": bridge,
            "action_steps": [
                "Lock one non-negotiable daily block before checking feeds or messages.",
                "Cut the single lowest-leverage task dragging your weekly execution score.",
                "Review your numbers every Sunday and adjust targets based on real output."
            ]
        })
        if len(selected) >= 14:
            break

    return selected


def filter_with_groq(raw_candidates):
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        print("[Groq] Missing GROQ_API_KEY — using niche-filtered fallback.")
        return _fallback_utilities_from_queries(raw_candidates)

    filtered_pool = [c for c in raw_candidates if is_niche_relevant(c)][:160]
    if not filtered_pool:
        filtered_pool = raw_candidates[:120]

    prompt = f"""You are a programmatic SEO and conversion architect for a self-improvement, masculinity, mindset, personal finance, and solo-operator brand.
Analyze these raw search queries:
{json.dumps(filtered_pool, indent=2)}

RULES:
1. DISCARD generic informational fluff and off-topic queries (medical, psychiatry, phone numbers, unrelated software).
2. KEEP ONLY high-intent queries where a standalone interactive calculator, diagnostic, or planner delivers immediate practical value and leads naturally to a paid system.
3. Produce 12 to 16 distinct, standalone micro-utilities.

Return ONLY valid JSON matching this exact structure:
{{
  "utilities": [
    {{
      "slug": "kebab-case-slug",
      "title": "Standalone Tool Title",
      "target_query": "primary query",
      "meta_description": "Under 155 chars description",
      "tool_type": "calculator",
      "inputs": [
        {{"id": "inp1", "label": "Specific input 1", "min": 1, "max": 100, "default": 50, "weight": 1.2}},
        {{"id": "inp2", "label": "Specific input 2", "min": 1, "max": 100, "default": 55, "weight": 1.0}},
        {{"id": "inp3", "label": "Specific input 3", "min": 1, "max": 100, "default": 65, "weight": 1.15}}
      ],
      "formula_mode": "readiness_score",
      "bridge_offer": "operator",
      "action_steps": [
        "Step 1 concrete action",
        "Step 2 concrete action",
        "Step 3 concrete action"
      ]
    }}
  ]
}}
Allowed formula_mode values: "revenue_projection", "wealth_ratio", "time_saved", "readiness_score".
Allowed bridge_offer values: "compression", "operator".
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; FMMediaHarvester/1.0)"
    }

    for model_name in GROQ_MODELS:
        payload = json.dumps({
            "model": model_name,
            "messages": [
                {"role": "system", "content": "Output raw JSON only. Never wrap in markdown code blocks."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
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
                utilities = [
                    u for u in parsed.get("utilities", [])
                    if is_niche_relevant(u.get("title", "") + " " + u.get("target_query", ""))
                ]
                if utilities:
                    for idx, u in enumerate(utilities):
                        if not u.get("action_steps"):
                            u["action_steps"] = [
                                "Set a daily floor you can hit even on low-energy days.",
                                "Remove distractions during your primary execution block.",
                                "Track weekly results and double down on what moves the needle."
                            ]
                        if not u.get("bridge_offer"):
                            _, b = _infer_bridge_and_mode(u.get("title", ""), idx)
                            u["bridge_offer"] = b
                    print(f"[Groq] Succeeded with model: {model_name} ({len(utilities)} utilities)")
                    return utilities
        except urllib.error.HTTPError as e:
            err_body = ""
            try:
                err_body = e.read().decode("utf-8", errors="replace")[:250]
            except Exception:
                pass
            print(f"[Groq] {model_name} failed ({e.code}): {err_body}")
        except Exception as e:
            print(f"[Groq] {model_name} failed: {e}")

    print("[Groq] All model attempts failed — using niche-filtered fallback.")
    return _fallback_utilities_from_queries(raw_candidates)


def main():
    print("Starting multi-layer niche demand harvest...")
    all_queries = set()

    for topic in SEED_TOPICS:
        for mod in TOOL_MODIFIERS[:4]:
            for suffix in ALPHABET_SWEEP[:4]:
                q = f"{mod} {topic}{suffix}".strip()
                all_queries.update(harvest_autocomplete(q))
                time.sleep(0.25)

    all_queries.update(harvest_marketplace_proof())

    gsc_hits = harvest_gsc_telemetry()
    gsc_queries = [item["query"] for item in gsc_hits]

    combined_pool = gsc_queries + list(all_queries)
    print(f"Total niche-filtered raw signals harvested: {len(combined_pool)}")

    utilities = filter_with_groq(combined_pool)
    output_payload = {
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "raw_signal_count": len(combined_pool),
        "gsc_opportunities": gsc_hits,
        "utilities": utilities
    }

    with open("validated_demand.json", "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2)

    print(f"Saved {len(utilities)} validated standalone utilities to validated_demand.json.")


if __name__ == "__main__":
    main()
