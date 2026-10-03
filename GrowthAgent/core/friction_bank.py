import random
from typing import Dict, Any

PRODUCT_CATALOG = {
    "OPERATOR_MINDSET_KIT": {
        "name": "Operator Mindset Kit",
        "url": "https://gumroad.com",
        "core_pain": "Inaction, analysis paralysis, lack of personal execution protocols",
        "target_desire": "Unshakable daily execution, sovereign focus, zero cognitive friction",
        "angle_triggers": [
            "You don't have a time management problem. You have an execution governance problem.",
            "Motivation is amateur fuel. Systems are operator infrastructure.",
            "Stop optimizing tools you don't even use."
        ]
    },
    "CLAUSEVAULT": {
        "name": "ClauseVault",
        "url": "https://gumroad.com",
        "core_pain": "Reactive life responses, emotional decision making under stress",
        "target_desire": "Structured self-mastery, personal principles, predictable emotional stability",
        "angle_triggers": [
            "If you haven't codified your personal rules, the world will write them for you.",
            "High-stress choices demand pre-written non-negotiable clauses.",
            "Your reaction to friction reveals your lack of internal systems."
        ]
    },
    "TIMELINE_REJECTION": {
        "name": "Timeline Rejection Protocol",
        "url": "https://gumroad.com",
        "core_pain": "Conforming to societal expectations, drift, passive trajectory",
        "target_desire": "Complete personal sovereignty, rapid trajectory re-engineering",
        "angle_triggers": [
            "The default path is engineered for quiet compliance.",
            "Rejecting the standard timeline requires deliberate operational friction.",
            "You are trading lifetime agency for short-term comfort."
        ]
    }
}


def get_friction_vector(product_key: str = None) -> Dict[str, Any]:
    """Retrieves a targeted friction profile for script synthesis."""
    if not product_key or product_key not in PRODUCT_CATALOG:
        product_key = random.choice(list(PRODUCT_CATALOG.keys()))

    product = PRODUCT_CATALOG[product_key]
    hook_angle = random.choice(product["angle_triggers"])

    return {
        "product_key": product_key,
        "product_name": product["name"],
        "core_pain": product["core_pain"],
        "target_desire": product["target_desire"],
        "selected_hook_angle": hook_angle,
        "cta_keyword": product_key.replace("_", "").lower()
    }


if __name__ == "__main__":
    print("[*] Testing Friction Bank Sample Vector:")
    print(get_friction_vector("OPERATOR_MINDSET_KIT"))
