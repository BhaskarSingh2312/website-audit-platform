import re
from typing import Dict, Any, List
from backend.app.models.schemas import DropshipAnalysis

DROPSHIP_KEYWORDS = [
    (r"7\s*-\s*(?:14|15|20|25)\s*(?:business\s*)?days", "Long shipping timeframe (7-20 business days) typical of overseas fulfillment"),
    (r"epacket|china\s*post|yanwen|yunexpress|cne\s*express", "Mentions Chinese logistics carriers (ePacket, Yanwen, YunExpress)"),
    (r"overseas\s*warehouse|international\s*warehouse", "Mentions fulfillment from overseas/international warehouses"),
    (r"do\s*not\s*send\s*(?:your\s*purchase\s*)?back\s*to\s*the\s*manufacturer", "Classic dropshipping return clause: 'Do not send back to manufacturer'"),
    (r"customs\s*(?:and|&)\s*import\s*taxes", "Mentions customs duties borne by customer"),
    (r"tracking\s*number\s*may\s*take\s*(?:3|5|7)\s*days\s*to\s*update", "Delayed tracking update notice common in AliExpress fulfillment"),
    (r"dsers|oberlo|zendrop|spocket|cjdropshipping|dropified", "Detected integration with dropshipping fulfillment software")
]

class DropshipDetector:
    def analyze(
        self,
        raw_html: str,
        policy_texts: Dict[str, str],
        catalog_data: Dict[str, Any],
        apps_detected: List[str],
        is_ecommerce: bool = False
    ) -> DropshipAnalysis:
        """
        Calculates dropshipping probability score and identifies specific signals.
        """
        signals: List[str] = []
        score: int = 10 # Base neutral score
        
        full_text = raw_html + " " + " ".join(policy_texts.values())
        full_text_lower = full_text.lower()

        # 1. Non-ecommerce Service / Agency check
        total_products = int(catalog_data.get("total_products_detected", 0))
        if not is_ecommerce and total_products == 0 and not any(term in full_text_lower for term in ["add to cart", "buy now", "checkout", "shipping policy"]):
            return DropshipAnalysis(
                is_dropshipping=False,
                confidence_score=0,
                signals_found=[],
                business_model="Service Agency / B2B Studio",
                reasoning="Store operates as a service agency, B2B studio, or portfolio brand with no physical e-commerce inventory."
            )

        # 2. Check Shipping & Policy Keywords
        for pattern, explanation in DROPSHIP_KEYWORDS:
            if re.search(pattern, full_text_lower):
                signals.append(explanation)
                score += 25

        # 3. Check for Dropship review apps
        review_apps = [app for app in apps_detected if any(k in app.lower() for k in ["loox", "alireviews", "judge.me"])]
        if review_apps and ("7-14" in full_text_lower or "overseas" in full_text_lower):
            signals.append(f"Uses photo review app ({', '.join(review_apps)}) alongside extended shipping policies")
            score += 15

        # 4. Check for specific dropshipping scripts in raw HTML
        if any(term in full_text_lower for term in ["dsers", "cjdropshipping", "zendrop"]):
            signals.append("Direct references to DSers / CJ Dropshipping fulfillment scripts found in page source")
            score += 30

        # 5. Check Catalog Diversity
        vendors = catalog_data.get("vendors", [])
        if len(vendors) > 8:
            signals.append(f"High vendor fragmentation ({len(vendors)} distinct supplier vendors detected in product feed)")
            score += 15

        # Cap score between 0 and 100
        score = min(max(score, 5), 98)
        is_dropship = score >= 50

        if is_dropship:
            model = "Dropshipping Store"
            reasoning = (
                f"High likelihood of dropshipping model ({score}% confidence). "
                f"Key triggers include: {', '.join(signals[:3]) if signals else 'extended shipping and fulfillment patterns'}."
            )
        elif score >= 30:
            model = "Hybrid / Unverified"
            reasoning = "Some dropshipping patterns present, but may operate as a hybrid direct-to-consumer store."
        else:
            model = "Brand / Private Label"
            reasoning = "Store displays brand hallmarks: custom inventory, localized fast shipping, and coherent brand narrative."

        return DropshipAnalysis(
            is_dropshipping=is_dropship,
            confidence_score=score,
            signals_found=signals,
            business_model=model,
            reasoning=reasoning
        )
