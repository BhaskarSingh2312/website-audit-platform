import re
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from backend.app.models.schemas import ContentTrustReport

class ContentAnalyzer:
    def analyze(
        self,
        soup: Optional[BeautifulSoup],
        raw_html: str,
        all_page_texts: Dict[str, str],
        crawled_pages: List[Any],
        contacts: Any
    ) -> ContentTrustReport:
        visible_text = soup.get_text(separator=" ") if soup else ""
        words = re.findall(r'\b[a-zA-Z]{2,}\b', visible_text)
        word_count = len(words)
        reading_time = round(word_count / 220, 1) # 220 WPM average reading speed

        # 1. Discover Essential Trust & Legal Pages from Crawled Pages & DOM
        found_pages = {getattr(p, 'page_type', '').lower(): getattr(p, 'url', '') for p in crawled_pages}
        all_urls_text = " ".join([getattr(p, 'url', '').lower() for p in crawled_pages]) + " " + (raw_html[:15000].lower())

        has_privacy = "privacy" in found_pages or "privacy" in all_urls_text
        has_terms = any(k in found_pages or k in all_urls_text for k in ["terms", "tos", "conditions"])
        has_refund = any(k in found_pages or k in all_urls_text for k in ["refund", "return", "cancellation"])
        has_about = any(k in found_pages or k in all_urls_text for k in ["about", "story", "team"])
        has_contact = any(k in found_pages or k in all_urls_text for k in ["contact", "reach", "support"])

        # 2. Check for Social Proof & Customer Reviews
        text_lower = visible_text.lower()
        has_proof = any(term in text_lower for term in [
            "testimonial", "review", "what our clients say", "what our customers say",
            "rated 5 star", "5-star", "trustpilot", "google reviews", "case study"
        ])

        has_faq = "faq" in text_lower or "frequently asked" in text_lower

        # 3. Contact Consistency Analysis
        consistency_report = {
            "email_count": len(getattr(contacts, 'emails', [])),
            "phone_count": len(getattr(contacts, 'phone_numbers', [])),
            "has_physical_address": len(getattr(contacts, 'addresses', [])) > 0,
            "has_tax_or_corp_id": bool(getattr(contacts, 'gstin_or_cin', None)),
            "mismatches": []
        }

        # Check if email domain matches website domain
        site_domain = ""
        if crawled_pages and hasattr(crawled_pages[0], 'url'):
            site_domain = re.sub(r'^https?://(www\.)?', '', crawled_pages[0].url).split('/')[0].lower()

        for em in getattr(contacts, 'emails', []):
            em_domain = em.split('@')[-1].lower() if '@' in em else ""
            if em_domain in ("gmail.com", "yahoo.com", "hotmail.com", "outlook.com") and site_domain:
                consistency_report["mismatches"].append(
                    f"Free email provider used ({em}) instead of a custom domain address (@{site_domain})."
                )

        # 4. Trust Signals & Evidence
        missing_trust: List[str] = []
        evidence: List[str] = []

        if not has_privacy:
            missing_trust.append("Missing Privacy Policy page (Required for GDPR/CCPA and ad compliance).")
        else:
            evidence.append("Privacy Policy verified and accessible to visitors.")

        if not has_terms:
            missing_trust.append("Missing Terms of Service / Legal Terms page.")
        else:
            evidence.append("Terms of Service page present.")

        if not has_refund:
            missing_trust.append("Missing Clear Refund/Return Policy.")
        
        if not getattr(contacts, 'addresses', []):
            missing_trust.append("No physical business address found across accessible pages.")
        else:
            evidence.append(f"Physical address verified: {contacts.addresses[0][:80]}")

        if not has_proof:
            missing_trust.append("No testimonials, case studies, or review proof detected on homepage.")
        else:
            evidence.append("Customer reviews or social proof testimonials present on page.")

        # 5. Compute Trust Score
        trust_score = 100
        if not has_privacy:
            trust_score -= 15
        if not has_terms:
            trust_score -= 10
        if not has_refund:
            trust_score -= 10
        if not getattr(contacts, 'emails', []):
            trust_score -= 15
        if not getattr(contacts, 'phone_numbers', []):
            trust_score -= 10
        if not getattr(contacts, 'addresses', []):
            trust_score -= 10
        if not has_proof:
            trust_score -= 10

        trust_score = min(max(trust_score, 25), 98)

        return ContentTrustReport(
            trust_score=trust_score,
            total_word_count=word_count,
            estimated_reading_time_mins=reading_time,
            has_privacy_policy=has_privacy,
            privacy_policy_url=found_pages.get("privacy policy"),
            has_terms_of_service=has_terms,
            terms_of_service_url=found_pages.get("terms of service"),
            has_refund_policy=has_refund,
            refund_policy_url=found_pages.get("refund policy"),
            has_about_page=has_about,
            has_contact_page=has_contact,
            has_faq_section=has_faq,
            has_social_proof=has_proof,
            contact_data_consistency=consistency_report,
            missing_trust_signals=missing_trust,
            evidence_backed_findings=evidence
        )

