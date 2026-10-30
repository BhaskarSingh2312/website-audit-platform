import re
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from backend.app.models.schemas import ClientConversionAudit

CTA_PATTERNS = [
    r'book\s+a\s+(?:call|demo|consultation|discovery)',
    r'get\s+(?:a\s+)?(?:quote|proposal|started|estimate|in\s+touch)',
    r'request\s+(?:a\s+)?(?:quote|consultation|audit|call)',
    r'start\s+(?:free\s+)?(?:trial|project|now)',
    r'contact\s+us',
    r'hire\s+us',
    r'schedule\s+(?:a\s+)?(?:call|meeting)',
    r'buy\s+now',
    r'order\s+now',
    r'shop\s+now',
    r'claim\s+(?:your\s+)?offer',
    r'work\s+with\s+us'
]

PROOF_KEYWORDS = [
    'testimonial', 'case stud', 'client review', 'trusted by', 'what our clients say',
    'customer review', 'success stor', 'results delivered', 'our portfolio', 'our partners',
    'featured in', 'star-rating', 'stars', '5-star', 'google review', 'trustpilot', 'clutch'
]

INSTANT_CHAT_INDICATORS = [
    'wa.me/', 'api.whatsapp.com', 'whatsapp', 'tawk.to', 'crisp.chat', 'intercom',
    'livechat', 'tidio', 'zendesk', 'hubspot-messages', 'chat-widget'
]

class ConversionAnalyzer:
    def analyze(
        self,
        soup: Optional[BeautifulSoup],
        raw_html: str,
        crawl_data: Dict[str, Any],
        is_ecommerce: bool = False
    ) -> ClientConversionAudit:
        """
        Analyzes client acquisition roadblocks, conversion rate optimization (CRO) leaks,
        trust deficits, and synthesizes exactly why visitors bounce without buying or contacting.
        """
        if not soup:
            return ClientConversionAudit(
                conversion_score=30,
                why_not_getting_clients=["Site returned unparseable content, preventing prospect conversion."]
            )

        html_lower = raw_html.lower()
        visible_text = soup.get_text(separator=" ").lower()
        score = 100
        why_not_getting_clients: List[str] = []
        cro_checklist: Dict[str, bool] = {}
        recovery_strategy: List[str] = []

        # 1. Primary Call-to-Action (CTA) Detection
        primary_cta: Optional[str] = None
        has_above_the_fold_cta = False
        
        # Search buttons, anchor tags with button styling or classes
        buttons = soup.find_all(['button', 'a'])
        for b in buttons:
            txt = b.get_text().strip()
            if not txt or len(txt) > 40:
                continue
            for pat in CTA_PATTERNS:
                if re.search(pat, txt, re.IGNORECASE):
                    primary_cta = txt
                    has_above_the_fold_cta = True
                    break
            if primary_cta:
                break

        cro_checklist["Above-the-Fold Primary CTA"] = bool(primary_cta)
        if not primary_cta:
            score -= 22
            why_not_getting_clients.append(
                "No clear, immediate Call-To-Action (CTA): Visitors landing on the page don't have a single, obvious action to take (e.g., 'Book a Discovery Call' or 'Get an Instant Quote'). Without friction-free guidance, 70%+ of prospects bounce."
            )
            recovery_strategy.append(
                "Add a prominent, high-contrast CTA button in the hero section above the fold with action-oriented copy."
            )

        # 2. Lead Capture / Inquiry Form
        forms = soup.find_all('form')
        has_lead_capture = False
        for f in forms:
            inputs = f.find_all(['input', 'textarea', 'select'])
            email_or_phone_input = any(
                (inp.get('type') in ['email', 'tel'] or any(k in (inp.get('name') or '').lower() for k in ['email', 'phone', 'contact', 'msg', 'message']))
                for inp in inputs
            )
            if email_or_phone_input:
                has_lead_capture = True
                break

        cro_checklist["Inquiry / Lead Capture Form"] = has_lead_capture
        if not has_lead_capture:
            score -= 18
            why_not_getting_clients.append(
                "No embedded lead capture form: Forcing interested buyers to open a separate email client or click away creates friction. Sites with embedded 2-3 field inquiry forms capture 3x more inbound leads."
            )
            recovery_strategy.append(
                "Embed a simple 3-field contact form (Name, Work Email/Phone, Project Requirement) directly on the homepage."
            )

        # 3. Social Proof & Credibility Indicators
        has_social_proof = any(keyword in visible_text or keyword in html_lower for keyword in PROOF_KEYWORDS)
        cro_checklist["Social Proof & Client Testimonials"] = has_social_proof
        if not has_social_proof:
            score -= 20
            why_not_getting_clients.append(
                "Zero verified social proof or client results: Modern B2B buyers and consumers suffer from trust anxiety. Without visible client logos, ratings, case studies, or video testimonials, visitors assume the business is untested or risky."
            )
            recovery_strategy.append(
                "Feature 3-4 verifiable client testimonials with names, logos, and measurable outcomes ('Increased revenue by 35%')."
            )

        # 4. Instant Direct Contact (WhatsApp / Live Chat)
        has_instant_chat = any(chat in html_lower for chat in INSTANT_CHAT_INDICATORS)
        cro_checklist["Instant Chat / WhatsApp Direct Line"] = has_instant_chat
        if not has_instant_chat:
            score -= 14
            why_not_getting_clients.append(
                "Missing instant messaging channel (WhatsApp / Live Chat): Over 55% of modern visitors prefer one-click chat over sending a cold email. Without a floating WhatsApp or live chat widget, high-intent impulse leads go unanswered."
            )
            recovery_strategy.append(
                "Deploy a floating WhatsApp click-to-chat button with an automated welcoming prompt to engage mobile visitors instantly."
            )

        # 5. Clear Offer & Pricing Transparency
        has_pricing_offer = any(w in visible_text for w in [
            'pricing', 'package', 'starting at', 'plans', '₹', '$', '€', '£',
            'fixed price', 'per month', 'quote calculator', 'services'
        ])
        cro_checklist["Clear Service Offerings & Scope"] = has_pricing_offer
        if not has_pricing_offer:
            score -= 12
            why_not_getting_clients.append(
                "Vague service offerings / no transparent packages: Visitors cannot quickly grasp what deliverables they receive or expected price ranges, causing them to leave for competitors with clearly tiered packages."
            )
            recovery_strategy.append(
                "Outline 2-3 structured service packages or an interactive pricing estimator to remove budget hesitation."
            )

        # 6. Performance & Page Speed Friction
        load_time = crawl_data.get("load_time_seconds", 0.0)
        has_speed_friction = load_time > 2.2
        cro_checklist["Fast Mobile Load Speed (<2s)"] = not has_speed_friction
        if has_speed_friction:
            score -= 14
            why_not_getting_clients.append(
                f"Page latency delay ({load_time}s load time): Every additional second of loading reduces mobile conversion rates by 7% and drives impatient visitors back to Google search results."
            )
            recovery_strategy.append(
                "Compress oversized image assets and defer non-critical JS bundles to push page load under 1.8 seconds."
            )

        final_conversion_score = max(25, min(95, score))

        # Build fallback recovery strategy if site scored high
        if not recovery_strategy:
            recovery_strategy = [
                "Implement A/B split testing on primary headline copy to increase click-through.",
                "Introduce risk-reversal guarantees (e.g. 100% Satisfaction or Milestone-based billing).",
                "Add an exit-intent popup offering a free checklist, audit, or consultation."
            ]

        return ClientConversionAudit(
            conversion_score=final_conversion_score,
            primary_call_to_action=primary_cta,
            has_above_the_fold_cta=bool(primary_cta),
            has_lead_capture_form=has_lead_capture,
            has_social_proof=has_social_proof,
            has_instant_chat=has_instant_chat,
            has_clear_pricing_or_offer=has_pricing_offer,
            friction_points_count=len(why_not_getting_clients),
            why_not_getting_clients=why_not_getting_clients,
            cro_checklist=cro_checklist,
            client_recovery_strategy=recovery_strategy
        )
