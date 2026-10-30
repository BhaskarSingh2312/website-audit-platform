import re
import json
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, urljoin
from backend.app.models.schemas import SeoAuditReport, BrokenLinkInfo

class SeoAnalyzer:
    def analyze(
        self,
        soup: Optional[BeautifulSoup],
        raw_html: str,
        crawl_data: Dict[str, Any],
        domain: str,
        base_url: str
    ) -> SeoAuditReport:
        if not soup:
            return SeoAuditReport(
                seo_score=30,
                why_stuck_summary="Search engine crawlers were unable to parse DOM HTML or received an error response.",
                ranking_blockers=["Website returned unparseable or blocked response to web crawlers."]
            )

        html_lower = raw_html.lower()
        score = 100
        blockers: List[str] = []
        quick_fixes: List[str] = []

        # 1. Title Tag Audit
        title_tag = soup.find('title')
        title_text = title_tag.get_text().strip() if title_tag else ""
        title_length = len(title_text)
        
        if not title_text:
            title_status = "MISSING"
            score -= 22
            blockers.append("Missing <title> tag: Google has no primary headline to display in SERPs, crippling organic impressions.")
            quick_fixes.append("Add a 50-60 character keyword-rich <title> tag containing your brand and core services.")
        elif title_length < 20:
            title_status = "TOO_SHORT"
            score -= 10
            blockers.append(f"Title tag is too brief ({title_length} chars: '{title_text}'), missing high-intent buyer keywords.")
            quick_fixes.append("Expand title tag to 45-60 characters with targeted industry and regional keywords.")
        elif title_length > 68:
            title_status = "TOO_LONG"
            score -= 6
            quick_fixes.append("Title tag exceeds 68 characters and will be truncated with '...' on mobile search results.")
        else:
            title_status = "OPTIMAL"

        # 2. Meta Description
        meta_desc = soup.find('meta', attrs={'name': lambda x: x and x.lower() == 'description'})
        desc_text = meta_desc.get('content', '').strip() if meta_desc else ""
        desc_length = len(desc_text)

        if not desc_text:
            meta_desc_status = "MISSING"
            score -= 18
            blockers.append("Missing meta description: Search engines generate arbitrary snippets from page text, lowering search CTR.")
            quick_fixes.append("Add a compelling 140-160 character meta description with a clear value proposition and call to action.")
        elif desc_length < 60:
            meta_desc_status = "TOO_SHORT"
            score -= 8
            blockers.append(f"Meta description is only {desc_length} chars. It lacks sufficient detail to persuade searchers to click.")
            quick_fixes.append("Expand meta description to at least 130 characters to highlight key benefits.")
        elif desc_length > 175:
            meta_desc_status = "TOO_LONG"
            score -= 4
            quick_fixes.append("Meta description is too long (>175 chars) and gets cut off on mobile Google SERPs.")
        else:
            meta_desc_status = "OPTIMAL"

        # 3. Heading Hierarchy (H1, H2, H3)
        h1_tags = [h.get_text().strip() for h in soup.find_all('h1') if h.get_text().strip()]
        h2_tags = [h.get_text().strip() for h in soup.find_all('h2') if h.get_text().strip()][:10]
        h3_tags = [h.get_text().strip() for h in soup.find_all('h3') if h.get_text().strip()][:10]

        is_spa = bool(soup.find('div', id='root') or "__next" in html_lower or "/assets/index" in html_lower)
        is_spa_indexing_risk = False

        if len(h1_tags) == 0:
            if is_spa:
                is_spa_indexing_risk = True
                score -= 12
                blockers.append("Client-side rendered H1 (React/Vite SPA): Crawlers without immediate JS execution see an empty page header.")
                quick_fixes.append("Implement Server-Side Rendering (Next.js/Remix) or Static HTML pre-rendering for top SEO keywords.")
            else:
                score -= 14
                blockers.append("Zero <h1> tags found: Google cannot determine the central topical authority of this page.")
                quick_fixes.append("Add a single, prominent <h1> tag containing your primary service or product keyword.")
        elif len(h1_tags) > 1:
            score -= 5
            quick_fixes.append(f"Page has {len(h1_tags)} <h1> tags. Consolidate into 1 primary <h1> and use <h2> for subsections.")

        # 4. Canonical Tag
        canonical_el = soup.find('link', rel=lambda x: x and 'canonical' in x)
        canonical_url = canonical_el.get('href', '').strip() if canonical_el else None
        canonical_status = "VALID"

        if not canonical_url:
            canonical_status = "MISSING"
            score -= 8
            quick_fixes.append("Add a self-referential canonical tag (<link rel='canonical'>) to prevent duplicate content dilution.")
        elif not canonical_url.startswith(("http://", "https://")):
            canonical_status = "RELATIVE"
            score -= 4
            quick_fixes.append("Canonical URL is relative; specify an absolute HTTPS URL to ensure search engines parse it reliably.")

        # 5. Robots.txt and Sitemap Validation
        has_robots = crawl_data.get("has_robots_txt", True)
        robots_url = urljoin(base_url, "/robots.txt")
        has_sitemap = crawl_data.get("has_sitemap", True)
        sitemap_url = urljoin(base_url, "/sitemap.xml")

        # 6. Indexability (Meta Robots)
        meta_robots_el = soup.find('meta', attrs={'name': lambda x: x and x.lower() == 'robots'})
        meta_robots = meta_robots_el.get('content', '') if meta_robots_el else None
        is_indexable = True
        if meta_robots and "noindex" in meta_robots.lower():
            is_indexable = False
            score -= 30
            blockers.append("CRITICAL: Meta robots tag contains 'noindex'. Search engines are instructed NOT to index this site in Google!")
            quick_fixes.append("Remove the 'noindex' directive from your robots meta tag immediately.")

        # 7. Structured Data & JSON-LD Schema Validation
        schemas_detected: List[str] = []
        schema_details: List[Dict[str, Any]] = []

        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.get_text())
                if isinstance(data, dict):
                    stype = data.get('@type')
                    if stype:
                        s_name = stype if isinstance(stype, str) else str(stype)
                        schemas_detected.append(s_name)
                        schema_details.append({"type": s_name, "valid": True})
                elif isinstance(data, list):
                    for item in data:
                        stype = item.get('@type')
                        if stype:
                            schemas_detected.append(str(stype))
                            schema_details.append({"type": str(stype), "valid": True})
            except Exception:
                schema_details.append({"type": "Invalid JSON-LD Syntax", "valid": False})

        has_schema = len(schemas_detected) > 0
        if not has_schema:
            score -= 10
            quick_fixes.append("Implement Schema.org JSON-LD (e.g. Organization, WebSite, LocalBusiness) to earn rich snippets in Google.")

        # 8. OpenGraph & Social Cards
        og_title = soup.find('meta', property='og:title')
        og_image = soup.find('meta', property='og:image')
        og_desc = soup.find('meta', property='og:description')
        has_og = bool(og_title or og_image)
        og_preview = {
            "title": og_title.get('content', '') if og_title else (title_text or ""),
            "image": og_image.get('content', '') if og_image else "",
            "description": og_desc.get('content', '') if og_desc else (desc_text or "")
        }

        has_twitter_card = bool(soup.find('meta', attrs={'name': lambda x: x and 'twitter:card' in x.lower()}))
        if not has_og:
            score -= 6
            quick_fixes.append("Add OpenGraph tags (og:title, og:image, og:description) for professional link previews on WhatsApp, Slack, and social feeds.")

        # 9. Image Optimization & Alt Attributes
        images = soup.find_all('img')
        images_total = len(images)
        images_with_alt = 0
        missing_alt_images = []

        for img in images:
            alt = img.get('alt')
            if alt is not None and alt.strip() != "":
                images_with_alt += 1
            else:
                src = img.get('src') or img.get('data-src') or ''
                if src and not src.startswith("data:"):
                    missing_alt_images.append(src[:100])

        images_missing_alt = images_total - images_with_alt
        if images_total > 0 and images_missing_alt > 0:
            score -= min(12, images_missing_alt * 2)
            quick_fixes.append(f"Add descriptive alt text to {images_missing_alt} image(s) to improve Google Image search traffic and accessibility.")

        # 10. Broken Links (From Crawl Data)
        broken_links_raw = crawl_data.get("broken_links", [])
        broken_links = [BrokenLinkInfo(**b) if isinstance(b, dict) else b for b in broken_links_raw]
        if broken_links:
            score -= min(15, len(broken_links) * 5)
            blockers.append(f"Detected {len(broken_links)} broken link(s) returning HTTP 404/500 errors.")

        # Final SEO Score
        score = min(max(score, 25), 98)

        # Why Stuck Summary
        if blockers:
            why_stuck = " ".join(blockers[:2])
        elif score < 80:
            why_stuck = "Site has baseline indexing but lacks rich schema, complete metadata, or image alt attributes to compete for top 3 Google positions."
        else:
            why_stuck = "Technical SEO foundation is solid. Focus on topical authority, backlink acquisition, and high-intent commercial content."

        return SeoAuditReport(
            seo_score=score,
            title_tag=title_text,
            title_length=title_length,
            title_status=title_status,
            meta_description=desc_text,
            meta_desc_length=desc_length,
            meta_desc_status=meta_desc_status,
            h1_tags=h1_tags,
            h2_tags=h2_tags,
            h3_tags=h3_tags,
            canonical_url=canonical_url,
            canonical_status=canonical_status,
            has_robots_txt=has_robots,
            robots_txt_url=robots_url,
            robots_txt_status="Accessible" if has_robots else "Missing",
            has_sitemap=has_sitemap,
            sitemap_url=sitemap_url,
            sitemap_status="Accessible" if has_sitemap else "Missing",
            meta_robots=meta_robots,
            is_indexable=is_indexable,
            schema_types_detected=list(set(schemas_detected)),
            has_schema_markup=has_schema,
            schema_details=schema_details,
            has_open_graph=has_og,
            og_preview=og_preview,
            has_twitter_card=has_twitter_card,
            images_total=images_total,
            images_with_alt=images_with_alt,
            images_missing_alt=images_missing_alt,
            sample_missing_alt_images=missing_alt_images[:6],
            broken_links=broken_links,
            broken_links_count=len(broken_links),
            mobile_viewport_configured=bool(soup.find('meta', attrs={'name': lambda x: x and x.lower() == 'viewport'})),
            is_spa_indexing_risk=is_spa_indexing_risk,
            why_stuck_summary=why_stuck,
            ranking_blockers=blockers,
            quick_seo_fixes=quick_fixes
        )
