import os
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

# Seed modifiers engineered to surface "maximizer" queries (tools, calculators, diagnostics)
# that AI Overviews cannot compress into a two-sentence summary.
SEED_TOPICS = [
    "digital product",
    "gumroad product",
    "solo founder",
    "notion template",
    "mindset system",
    "content workflow",
    "habit tracker",
    "personal operating system"
]

TOOL_MODIFIERS = [
    "calculator for",
    "checklist for",
    "template for",
    "diagnostic for",
    "pricing calculator",
    "generator for",
    "audit for",
    "scorecard for"
]

ALPHABET_SWEEP = ["", " a", " b", " c", " f", " g", " m", " p", " s", " t"]


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

    # Layer 1A: Google Suggest
    g_data = fetch_json(f"https://suggestqueries.google.com/complete/search?client=firefox&q={q_enc}")
    if isinstance(g_data, list) and len(g_data) > 1:
        results.update(g_data[1])

    # Layer 1B: YouTube Suggest
    yt_data = fetch_json(f"https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q={q_enc}")
    if isinstance(yt_data, list) and len(yt_data) > 1:
        results.update(yt_data[1])

    # Layer 1C: DuckDuckGo Suggest fallback
    ddg_data = fetch_json(f"https://duckduckgo.com/ac/?q={q_enc}&type=list")
    if isinstance(ddg_data, list) and len(ddg_data) > 1:
        results.update(ddg_data[1])

    return list(results)


def harvest_marketplace_proof():
    """Pulls proven commercial patterns via DuckDuckGo Instant/HTML query fallbacks."""
    proof_queries = []
    commercial_probes = [
        "site:gumroad.com/l/ system",
        "site:gumroad.com/l/ protocol",
        "site:gumroad.com/l/ tracker",
        "site:etsy.com/listing/ notion operating system"
    ]
    for probe in commercial_probes:
        suggestions = harvest_autocomplete(probe)
        proof_queries.extend(suggestions)
        time.sleep(0.4)
    return list(set(proof_queries))


def harvest_gsc_telemetry():
    """Pulls non-branded queries in positions 8-25 from Google Search Console API."""
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
            impressions = row.get("impressions", 0)
            position = row.get("position", 100)
            # Striking-distance filter: page 2-3 impressions where a dedicated tool jumps to page 1
            if impressions >= 10 and 7.0 <= position <= 30.0:
                opportunities.append({
                    "query": query_text,
                    "impressions": impressions,
                    "position": round(position, 1),
                    "source": "GSC"
                })
        print(f"[GSC] Extracted {len(opportunities)} striking-distance queries.")
        return opportunities
    except Exception as e:
        print(f"[GSC] Telemetry check skipped due to error: {e}")
        return []


def _fallback_utilities_from_queries(raw_candidates):
    """Builds interactive utility definitions deterministically if Groq is unreachable or 403."""
    modes = ["readiness_score", "time_saved", "revenue_projection"]
    bridges = ["compression", "operator"]
    selected = []
    seen_slugs = set()

    for q in raw_candidates:
        cleaned = "".join(ch if ch.isalnum() or ch == " " else " " for ch in str(q).lower()).strip()
        words = [w for w in cleaned.split() if len(w) > 1]
        if len(words) < 3:
            continue
        slug = "-".join(words[:6])[:55].strip("-")
        if not slug or slug in seen_slugs:
            continue
        seen_slugs.add(slug)

        idx = len(selected)
        title = " ".join(w.capitalize() for w in words[:6]) + " Calculator"
        selected.append({
            "slug": slug,
            "title": title,
            "target_query": str(q)[:80],
            "meta_description": f"Interactive browser calculator and diagnostic for {str(q)[:95]}.",
            "tool_type": "calculator",
            "inputs": [
                {"id": "inp1", "label": "Current Execution Pace (1-100)", "min": 1, "max": 100, "default": 45, "weight": 1.2},
                {"id": "inp2", "label": "Workflow Bottleneck Severity (1-100)", "min": 1, "max": 100, "default": 60, "weight": 1.0},
                {"id": "inp3", "label": "Weekly Output Consistency (1-100)", "min": 1, "max": 100, "default": 50, "weight": 1.1}
            ],
            "formula_mode": modes[idx % len(modes)],
            "bridge_offer": bridges[idx % len(bridges)]
        })
        if len(selected) >= 14:
            break

    return selected


def filter_with_groq(raw_candidates):
    """Uses GroqCloud to filter fluff and structure interactive tools, with safe fallback."""
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        print("[Groq] Missing GROQ_API_KEY — using deterministic fallback filter.")
        return _fallback_utilities_from_queries(raw_candidates)

    prompt = f"""You are a programmatic SEO architect. Analyze these raw search queries and commercial signals:
{json.dumps(raw_candidates[:180], indent=2)}

RULES:
1. DISCARD any generic informational query that can be answered in 2 sentences (e.g., "what is a digital product", "how to stay motivated"). AI Overviews absorb those.
2. KEEP ONLY high-friction "maximizer" queries that justify a standalone interactive browser utility (calculator, diagnostic scorecard, readiness audit, pricing estimator, or scope planner).
3. Consolidate duplicates into 12 to 18 razor-sharp, distinct micro-utilities aligned with solo creators, digital product builders, and high-agency personal systems.

Return ONLY a valid JSON object with a single key "utilities" containing an array of objects, each with:
- "slug": URL-safe lowercase hyphenated slug (e.g., "digital-product-pricing-calculator")
- "title": Clear, high-CTR tool title (e.g., "Digital Product Pricing & Margin Calculator")
- "target_query": The exact primary search query targeted
- "meta_description": Under 155 characters, action-oriented
- "tool_type": One of ["calculator", "diagnostic", "planner"]
- "inputs": Array of 3 to 4 objects with {{"id": "inp1", "label": "Question or metric label", "min": 1, "max": 100, "default": 50, "weight": 1.0}}
- "formula_mode": One of ["revenue_projection", "readiness_score", "time_saved"]
- "bridge_offer": Either "compression" (for digital product/building/monetization tools) or "operator" (for mindset/focus/execution tools)
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; FMMediaHarvester/1.0)"
    }

    for model_name in ["openai/gpt-oss-120b", "llama-3.1-8b-instant"]:
        payload = json.dumps({
            "model": model_name,
            "messages": [
                {"role": "system", "content": "Output strict valid JSON only. No markdown fences."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
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
                parsed = json.loads(content)
                utilities = parsed.get("utilities", [])
                if utilities:
                    return utilities
        except urllib.error.HTTPError as e:
            err_body = ""
            try:
                err_body = e.read().decode("utf-8", errors="replace")[:300]
            except Exception:
                pass
            print(f"[Groq] {model_name} failed ({e.code}): {err_body}")
        except Exception as e:
            print(f"[Groq] {model_name} failed: {e}")

    print("[Groq] All model attempts failed — using deterministic fallback filter.")
    return _fallback_utilities_from_queries(raw_candidates)

def main():
    print("Starting multi-layer demand harvest...")
    all_queries = set()

    for topic in SEED_TOPICS:
        for mod in TOOL_MODIFIERS[:4]:
            for suffix in ALPHABET_SWEEP[:4]:
                q = f"{mod} {topic}{suffix}".strip()
                hits = harvest_autocomplete(q)
                all_queries.update(hits)
                time.sleep(0.25)

    marketplace_hits = harvest_marketplace_proof()
    all_queries.update(marketplace_hits)

    gsc_hits = harvest_gsc_telemetry()
    gsc_queries = [item["query"] for item in gsc_hits]

    combined_pool = gsc_queries + list(all_queries)
    print(f"Total raw signals harvested: {len(combined_pool)}")

    utilities = filter_with_groq(combined_pool)
    output_payload = {
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "raw_signal_count": len(combined_pool),
        "gsc_opportunities": gsc_hits,
        "utilities": utilities
    }

    with open("validated_demand.json", "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2)

    print(f"Saved {len(utilities)} validated interactive utilities to validated_demand.json.")


if __name__ == "__main__":
    main()
