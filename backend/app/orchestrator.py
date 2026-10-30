import uuid
import json
import asyncio
from typing import Dict, Any, AsyncGenerator, Optional
from urllib.parse import urlparse
from datetime import datetime, timezone

from backend.app.core.security import normalize_url, validate_url_for_ssrf
from backend.app.scrapers.fast_crawler import FastCrawler
from backend.app.scrapers.contact_extractor import extract_all_contacts
from backend.app.analyzers.social_analyzer import SocialAnalyzer
from backend.app.analyzers.ad_intelligence import AdIntelligenceAnalyzer
from backend.app.analyzers.seo_analyzer import SeoAnalyzer
from backend.app.analyzers.security_analyzer import SecurityAnalyzer
from backend.app.analyzers.performance_analyzer import PerformanceAnalyzer
from backend.app.analyzers.content_analyzer import ContentAnalyzer
from backend.app.analyzers.history_analyzer import HistoryAnalyzer
from backend.app.analyzers.tech_detector import TechDetector
from backend.app.analyzers.conversion_analyzer import ConversionAnalyzer
from backend.app.analyzers.flaw_detector import FlawDetector
from backend.app.analyzers.dropship_detector import DropshipDetector
from backend.app.analyzers.audit_differ import AuditDiffer
from backend.app.ai.gemini_agent import GeminiAgent
from backend.app.models.schemas import AuditReport, CatalogSummary, CatalogProduct, MetaAdsInsight
from backend.app.db.database import db

class AuditOrchestrator:
    def __init__(self):
        self.crawler = FastCrawler()
        self.social_analyzer = SocialAnalyzer()
        self.ad_analyzer = AdIntelligenceAnalyzer()
        self.seo_analyzer = SeoAnalyzer()
        self.security_analyzer = SecurityAnalyzer()
        self.perf_analyzer = PerformanceAnalyzer()
        self.content_analyzer = ContentAnalyzer()
        self.history_analyzer = HistoryAnalyzer()
        self.tech_detector = TechDetector()
        self.conversion_analyzer = ConversionAnalyzer()
        self.flaw_detector = FlawDetector()
        self.dropship_detector = DropshipDetector()
        self.differ = AuditDiffer()
        self.db = db

    async def run_audit_stream(self, target_url: str, custom_api_key: Optional[str] = None) -> AsyncGenerator[str, None]:
        audit_id = str(uuid.uuid4())[:8]
        normalized_url = normalize_url(target_url)

        # 1. SSRF & Security Validation
        is_safe, error_msg = validate_url_for_ssrf(normalized_url)
        if not is_safe:
            yield self._format_sse("error", {"message": error_msg or "URL validation blocked."})
            return

        yield self._format_sse("step", {
            "step": "connect",
            "progress": 5,
            "title": "Connecting & Initializing...",
            "details": f"Resolving domain {normalized_url}"
        })
        await asyncio.sleep(0.05)

        gemini_agent = GeminiAgent(api_key=custom_api_key)

        # 2. Multi-Page Deep Crawling
        yield self._format_sse("step", {
            "step": "crawl",
            "progress": 15,
            "title": "Multi-Page Deep Crawl Active...",
            "details": "Scanning navigation, Contact, About, Policies, robots.txt & catalog"
        })

        crawl_data = await self.crawler.crawl_site(normalized_url)
        if crawl_data.get("error"):
            yield self._format_sse("error", {"message": crawl_data["error"]})
            return

        soup = crawl_data["soup"]
        raw_html = crawl_data["html"]
        domain = crawl_data["domain"]
        headers = crawl_data["headers"]
        products_json = crawl_data.get("products_json")
        all_page_texts = crawl_data.get("all_page_texts", {})
        crawled_pages = crawl_data.get("crawled_pages", [])
        load_time = crawl_data.get("load_time_seconds", 0.0)
        ttfb = crawl_data.get("ttfb_seconds", 0.0)

        # Smart Universal Brand Name Extraction for ANY website
        clean_domain_root = domain.replace("www.", "").split(".")[0].replace("-", " ").title()
        brand_name = clean_domain_root

        if soup:
            # 1. Priority: og:site_name meta tag
            og_site = soup.find("meta", property="og:site_name") or soup.find("meta", attrs={"name": "og:site_name"})
            if og_site and og_site.get("content"):
                cand = og_site["content"].strip()
                if 2 < len(cand) < 45 and cand.lower() not in ["home", "welcome", "official"]:
                    brand_name = cand

            # 2. Priority: JSON-LD Schema Organization / WebSite name
            if brand_name == clean_domain_root:
                for script in soup.find_all("script", type="application/ld+json"):
                    try:
                        ld_data = json.loads(script.string or "")
                        items = ld_data if isinstance(ld_data, list) else [ld_data]
                        for itm in items:
                            if isinstance(itm, dict) and itm.get("@type") in ["Organization", "WebSite", "Brand", "LocalBusiness"]:
                                if itm.get("name") and 2 < len(itm["name"]) < 45:
                                    brand_name = itm["name"].strip()
                                    break
                    except Exception:
                        pass

            # 3. Fallback: Clean Title Tag parsing
            if brand_name == clean_domain_root and soup.find('title'):
                title_text = soup.find('title').get_text().strip()
                for sep in ["–", "-", "|", ":", "•", "—", "/"]:
                    if sep in title_text:
                        parts = [p.strip() for p in title_text.split(sep)]
                        cand = parts[0] if len(parts[0]) > 2 else parts[-1]
                        cand = re.sub(r"^(?:Welcome to|Official Website of|Shop at|The)\s+", "", cand, flags=re.I).strip()
                        if 2 < len(cand) < 40:
                            brand_name = cand
                        break

        # 3. Social Media Discovery & Analysis
        yield self._format_sse("step", {
            "step": "social",
            "progress": 28,
            "title": "Discovering Social Media Presence...",
            "details": "Extracting profiles, metadata tags, handles & missing platforms"
        })
        social_report = self.social_analyzer.analyze(soup, raw_html, all_page_texts, brand_name, domain)
        contacts = await extract_all_contacts(soup, raw_html, all_page_texts, gemini_agent=gemini_agent)

        # 4. Advertising Intelligence & Pixels
        yield self._format_sse("step", {
            "step": "ads",
            "progress": 40,
            "title": "Auditing Advertising Footprint...",
            "details": "Checking Meta, Google Ads Transparency, LinkedIn, TikTok & tracking pixels"
        })
        ad_report = self.ad_analyzer.analyze(
            soup, raw_html, brand_name, domain, social_profiles=social_report.profiles
        )

        # 5. Technical SEO & Schema Audit
        yield self._format_sse("step", {
            "step": "seo",
            "progress": 52,
            "title": "Auditing Technical SEO & Schema...",
            "details": "Analyzing meta tags, robots.txt, sitemaps, JSON-LD schema & broken links"
        })
        seo_report = self.seo_analyzer.analyze(soup, raw_html, crawl_data, domain, normalized_url)

        # 6. Website Security & SSL Audit
        yield self._format_sse("step", {
            "step": "security",
            "progress": 64,
            "title": "Performing Safe Security Audit...",
            "details": "Inspecting SSL/TLS certificate, security headers grade & cookie compliance"
        })
        security_report = await self.security_analyzer.analyze(
            soup, raw_html, headers, domain, normalized_url,
            exposed_probe_results=crawl_data.get("exposed_probes", [])
        )

        # 7. Performance & Responsive Audit
        yield self._format_sse("step", {
            "step": "perf",
            "progress": 75,
            "title": "Measuring Performance & Responsiveness...",
            "details": "Estimating Core Web Vitals, asset breakdown, and mobile UI readiness"
        })
        perf_report = self.perf_analyzer.analyze(soup, raw_html, load_time, ttfb)

        # 8. Content Completeness & Trust Signals
        yield self._format_sse("step", {
            "step": "content",
            "progress": 83,
            "title": "Evaluating Content Accuracy & Trust...",
            "details": "Checking legal policies, trust badges & contact data consistency"
        })
        content_report = self.content_analyzer.analyze(soup, raw_html, all_page_texts, crawled_pages, contacts)

        # 9. Technology Stack & Integrations
        yield self._format_sse("step", {
            "step": "tech",
            "progress": 88,
            "title": "Identifying Technology Stack...",
            "details": "Detecting CMS, frameworks, apps, chat widgets & version numbers"
        })
        tech_report = self.tech_detector.detect_tech(soup, raw_html, headers, products_json)

        # 10. Historical Records & Archive Timeline
        yield self._format_sse("step", {
            "step": "history",
            "progress": 92,
            "title": "Retrieving Web Archive Records...",
            "details": "Querying Wayback Machine snapshot history and domain age"
        })
        history_report = await self.history_analyzer.analyze(domain)

        # Catalog & Dropshipping (E-Commerce Analysis)
        catalog_summary = self._parse_catalog(products_json, soup)
        dropship_info = self.dropship_detector.analyze(
            raw_html,
            all_page_texts,
            catalog_summary.model_dump(),
            tech_report.apps_detected,
            is_ecommerce=tech_report.is_ecommerce
        )
        conversion_report = self.conversion_analyzer.analyze(soup, raw_html, crawl_data, is_ecommerce=tech_report.is_ecommerce)

        # 11. Comprehensive Flaw Detection across all 7 dimensions
        flaws = self.flaw_detector.detect_flaws(
            soup,
            raw_html,
            crawl_data,
            tech_info=tech_report,
            seo_report=seo_report,
            security_report=security_report,
            perf_report=perf_report,
            content_report=content_report,
            social_report=social_report,
            ad_report=ad_report,
            conversion_report=conversion_report
        )

        # 12. Retrieve Previous Audit for Comparison
        previous_audit = self.db.get_latest_audit_by_domain(domain, exclude_id=audit_id)
        current_summary_dict = {
            "health_score": int((seo_report.seo_score + security_report.security_score + perf_report.performance_score + content_report.trust_score) / 4),
            "flaws": [f.model_dump() for f in flaws]
        }
        comparison_report = self.differ.compare(current_summary_dict, previous_audit)

        # 13. Gemini AI Synthesis
        yield self._format_sse("step", {
            "step": "ai",
            "progress": 96,
            "title": "Synthesizing Executive Intelligence...",
            "details": "Google Gemini generating executive summary and strategic recommendations"
        })
        
        country = self._detect_country(domain, raw_html)
        raw_report_bundle = {
            "domain": domain,
            "brand_name": brand_name,
            "country_of_operation": country,
            "tech_stack": tech_report.model_dump(),
            "seo_audit": seo_report.model_dump(),
            "security_audit": security_report.model_dump(),
            "performance_audit": perf_report.model_dump(),
            "ad_intelligence": ad_report.model_dump(),
            "social_discovery": social_report.model_dump(),
            "flaws": [f.model_dump() for f in flaws],
            "crawled_pages": [p.model_dump() for p in crawled_pages]
        }
        
        ai_synthesis = await gemini_agent.synthesize_audit_report(raw_report_bundle)
        overall_health = ai_synthesis.get("health_score") or current_summary_dict["health_score"]

        # Backward compatibility MetaAdsInsight object
        meta_insight = MetaAdsInsight(
            active_ads_count=ad_report.total_active_ads_detected,
            has_active_ads=ad_report.has_active_ads,
            ad_spend_profile=ad_report.overall_spend_profile,
            sample_ads=ad_report.sample_creatives,
            marketing_opportunity=ad_report.marketing_opportunity
        )

        # Final Master Audit Report
        final_report = AuditReport(
            audit_id=audit_id,
            url=normalized_url,
            domain=domain,
            brand_name=brand_name,
            health_score=overall_health,
            seo_score=seo_report.seo_score,
            security_score=security_report.security_score,
            performance_score=perf_report.performance_score,
            conversion_score=conversion_report.conversion_score,
            country_of_operation=country,
            executive_summary=ai_synthesis.get("executive_summary", ""),
            contacts=contacts,
            social_discovery=social_report,
            ad_intelligence=ad_report,
            seo_audit=seo_report,
            security_audit=security_report,
            performance_audit=perf_report,
            content_trust=content_report,
            tech_stack=tech_report,
            historical_records=history_report,
            catalog=catalog_summary,
            dropship_analysis=dropship_info,
            conversion_audit=conversion_report,
            meta_ads=meta_insight,
            flaws=flaws,
            crawled_pages=crawled_pages,
            comparison=comparison_report,
            pitch_email_subject=ai_synthesis.get("pitch_email_subject", ""),
            pitch_email_body=ai_synthesis.get("pitch_email_body", ""),
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        )

        # 14. Persist to SQLite Database
        self.db.save_audit(final_report.model_dump())

        # 15. Emit Complete Event
        yield self._format_sse("complete", {
            "audit_id": audit_id,
            "progress": 100,
            "report": final_report.model_dump()
        })

    def _parse_catalog(self, products_json: Optional[Dict], soup: Any) -> CatalogSummary:
        if products_json and "products" in products_json:
            products = products_json["products"]
            total = len(products)
            vendors = list({p.get("vendor", "") for p in products if p.get("vendor")})
            sample_items: list[CatalogProduct] = []
            prices = []
            for p in products[:8]:
                variants = p.get("variants", [])
                price_str = variants[0].get("price") if variants else None
                if price_str:
                    try:
                        prices.append(float(price_str))
                    except ValueError:
                        pass
                img = p.get("images", [{}])[0].get("src") if p.get("images") else None
                sample_items.append(CatalogProduct(
                    title=p.get("title", ""),
                    price=f"${price_str}" if price_str else None,
                    image_url=img
                ))
            min_p = min(prices) if prices else None
            max_p = max(prices) if prices else None
            return CatalogSummary(
                total_products_detected=total,
                min_price=min_p,
                max_price=max_p,
                sample_products=sample_items,
                vendors=vendors[:8]
            )
        return CatalogSummary(total_products_detected=0)

    def _detect_country(self, domain: str, html: str) -> str:
        if domain.endswith(".in") or "₹" in html or "inr" in html.lower() or "rs." in html.lower():
            return "India (₹ INR)"
        elif domain.endswith(".co.uk") or domain.endswith(".uk") or "£" in html:
            return "United Kingdom (£ GBP)"
        elif domain.endswith(".ca"):
            return "Canada (CAD)"
        elif domain.endswith(".com.au") or domain.endswith(".au"):
            return "Australia (AUD)"
        elif "€" in html or "eur" in html.lower():
            return "European Union (€ EUR)"
        return "United States / Global ($ USD)"

    def _format_sse(self, event_type: str, data: Dict[str, Any]) -> str:
        return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
