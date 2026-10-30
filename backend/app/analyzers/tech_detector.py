import re
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from backend.app.models.schemas import TechStackReport, TechStackItem

class TechDetector:
    def detect_tech(
        self,
        soup: Optional[BeautifulSoup],
        raw_html: str,
        headers: Dict[str, str],
        products_json: Any
    ) -> TechStackReport:
        platform = "Custom Coded"
        hosting = headers.get("server") or headers.get("x-powered-by") or "Cloud Infrastructure"
        is_ecommerce = False
        items: List[TechStackItem] = []
        analytics_pixels: List[str] = []
        apps_detected: List[str] = []
        details: Dict[str, Any] = {}

        html_lower = raw_html.lower()

        # 1. CMS & E-commerce Platform Detection
        # Check generator meta tag for version
        wp_version = None
        if soup:
            gen = soup.find('meta', attrs={'name': lambda x: x and x.lower() == 'generator'})
            if gen and gen.get('content'):
                content = gen.get('content')
                if "wordpress" in content.lower():
                    m = re.search(r'wordpress\s*([\d.]+)', content, re.I)
                    if m:
                        wp_version = m.group(1)

        if products_json or "cdn.shopify.com" in html_lower or "shopify.theme" in html_lower or "myshopify.com" in html_lower:
            platform = "Shopify"
            is_ecommerce = True
            hosting = "Shopify Cloud / Cloudflare"
            items.append(TechStackItem(name="Shopify", category="E-commerce Platform", confidence="High", detected_via="Assets & /products.json"))
        elif "wp-content" in html_lower or "wp-includes" in html_lower or wp_version:
            if "woocommerce" in html_lower or "wc-" in html_lower:
                platform = "WordPress (WooCommerce)"
                is_ecommerce = True
                items.append(TechStackItem(name="WooCommerce", category="E-commerce", confidence="High", detected_via="wp-content/plugins/woocommerce"))
            else:
                platform = "WordPress"
            items.append(TechStackItem(name="WordPress", category="CMS", confidence="High", version=wp_version, detected_via="Generator tag / wp-content paths"))
        elif "wix.com" in html_lower or "wixsite.com" in html_lower or "parastorage.com" in html_lower:
            platform = "Wix"
            if "wix-stores" in html_lower:
                is_ecommerce = True
            items.append(TechStackItem(name="Wix", category="CMS / Website Builder", confidence="High", detected_via="wix scripts"))
        elif "squarespace" in html_lower or "static1.squarespace.com" in html_lower:
            platform = "Squarespace"
            if "squarespace-commerce" in html_lower:
                is_ecommerce = True
            items.append(TechStackItem(name="Squarespace", category="CMS / Website Builder", confidence="High", detected_via="static1.squarespace.com"))
        elif "webflow" in html_lower or "assets.website-files.com" in html_lower:
            platform = "Webflow"
            if "w-commerce" in html_lower:
                is_ecommerce = True
            items.append(TechStackItem(name="Webflow", category="No-Code CMS", confidence="High", detected_via="assets.website-files.com"))
        elif "bigcommerce" in html_lower or "cdn11.bigcommerce.com" in html_lower:
            platform = "BigCommerce"
            is_ecommerce = True
            items.append(TechStackItem(name="BigCommerce", category="E-commerce Platform", confidence="High", detected_via="bigcommerce assets"))
        elif "magento" in html_lower or "mage/cookies" in html_lower:
            platform = "Magento / Adobe Commerce"
            is_ecommerce = True
            items.append(TechStackItem(name="Magento", category="Enterprise E-commerce", confidence="High", detected_via="mage scripts"))
        elif "__next" in html_lower or "next/static" in html_lower:
            platform = "Custom (Next.js / React)"
            hosting = "Vercel / AWS Cloud"
            items.append(TechStackItem(name="Next.js", category="Frontend Framework", confidence="High", detected_via="__next DOM container"))
        elif "__nuxt" in html_lower or "nuxt" in html_lower:
            platform = "Custom (Nuxt.js / Vue)"
            items.append(TechStackItem(name="Nuxt.js", category="Frontend Framework", confidence="High", detected_via="__nuxt DOM container"))
        elif "id=\"root\"" in html_lower or "vite" in html_lower:
            platform = "Custom (React / Vite SPA)"
            items.append(TechStackItem(name="React", category="Frontend Framework", confidence="High", detected_via="React DOM root"))

        # E-commerce check
        if not is_ecommerce and any(t in html_lower for t in ["add to cart", "buy now", "checkout", "/cart"]):
            is_ecommerce = True

        # 2. Frontend Libraries & CSS Frameworks
        if "react" in html_lower or "react-dom" in html_lower or "__next" in html_lower:
            if not any(it.name == "React" for it in items):
                items.append(TechStackItem(name="React", category="Frontend Library", confidence="High", detected_via="React DOM signature"))
        if "vue" in html_lower or "vuejs" in html_lower or "__nuxt" in html_lower:
            items.append(TechStackItem(name="Vue.js", category="Frontend Framework", confidence="High", detected_via="Vue runtime signature"))
        if "tailwind" in html_lower:
            items.append(TechStackItem(name="Tailwind CSS", category="CSS Framework", confidence="High", detected_via="Tailwind class signatures"))
        if "bootstrap" in html_lower:
            items.append(TechStackItem(name="Bootstrap", category="CSS Framework", confidence="High", detected_via="Bootstrap CSS"))
        if "jquery" in html_lower:
            jq_match = re.search(r'jquery[.-]([\d.]+)', html_lower)
            jq_v = jq_match.group(1) if jq_match else None
            items.append(TechStackItem(name="jQuery", category="JavaScript Library", confidence="High", version=jq_v, detected_via="Script source"))

        # 3. Analytics & Pixels
        pixel_checks = [
            ("Meta Pixel", r'connect\.facebook\.net|fbq\(', "Advertising Pixel"),
            ("Google Analytics (GA4)", r'googletagmanager\.com/gtag/js|gtag\([\'"]config[\'"],\s*[\'"]G-', "Analytics"),
            ("Google Tag Manager", r'googletagmanager\.com/gtm\.js|gtm-[a-z0-9]+', "Tag Management"),
            ("TikTok Pixel", r'analytics\.tiktok\.com|ttq\.load', "Advertising Pixel"),
            ("Pinterest Tag", r'pintrk\(|pinterest\.com/v3', "Advertising Pixel"),
            ("LinkedIn Insight", r'snap\.licdn\.com|_linkedin_partner_id', "Advertising Pixel"),
            ("Hotjar", r'static\.hotjar\.com|_hjsettings', "Behavioral Analytics"),
            ("Microsoft Clarity", r'clarity\.ms/tag', "Heatmap & Session Replay")
        ]

        for p_name, regex, cat in pixel_checks:
            if re.search(regex, raw_html, re.I):
                analytics_pixels.append(p_name)
                items.append(TechStackItem(name=p_name, category=cat, confidence="High", detected_via="Tracking Script"))

        # 4. Third-Party Apps, Chat & Payment
        tool_checks = [
            ("Klaviyo", r'klaviyo\.com|_learnq', "Marketing Automation"),
            ("Mailchimp", r'chimpstatic\.com|mailchimp', "Email Marketing"),
            ("Intercom", r'widget\.intercom\.io', "Live Chat & Support"),
            ("Zendesk", r'zdassets\.com|zopim', "Customer Support"),
            ("Tidio", r'code\.tidio\.co', "Live Chat Widget"),
            ("Crisp Chat", r'client\.crisp\.chat', "Live Chat Widget"),
            ("Stripe", r'js\.stripe\.com', "Payment Gateway"),
            ("PayPal", r'paypal\.com/sdk', "Payment Gateway"),
            ("Razorpay", r'checkout\.razorpay\.com', "Payment Gateway"),
            ("Cloudflare", r'cloudflare', "CDN & Cloud Security")
        ]

        for t_name, regex, cat in tool_checks:
            if re.search(regex, raw_html, re.I) or (t_name == "Cloudflare" and "cloudflare" in str(headers).lower()):
                apps_detected.append(t_name)
                items.append(TechStackItem(name=t_name, category=cat, confidence="High", detected_via="CDN / Script tag"))

        # Deduplicate items by name
        unique_items = []
        seen_names = set()
        for it in items:
            if it.name not in seen_names:
                seen_names.add(it.name)
                unique_items.append(it)

        return TechStackReport(
            platform=platform,
            hosting=hosting,
            is_ecommerce=is_ecommerce,
            technologies=unique_items,
            analytics_pixels=analytics_pixels,
            apps_detected=apps_detected,
            details=details
        )
