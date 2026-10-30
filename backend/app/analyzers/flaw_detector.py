import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from backend.app.models.schemas import FlawItem

class FlawDetector:
    def detect_flaws(
        self,
        soup: Optional[BeautifulSoup],
        raw_html: str,
        crawl_data: Dict[str, Any],
        tech_info: Any = None,
        seo_report: Any = None,
        security_report: Any = None,
        perf_report: Any = None,
        content_report: Any = None,
        social_report: Any = None,
        ad_report: Any = None,
        conversion_report: Any = None
    ) -> List[FlawItem]:
        flaws: List[FlawItem] = []

        if not soup:
            return [
                FlawItem(
                    category="Technical",
                    title="Website Inaccessible / Empty DOM Shell",
                    severity="CRITICAL",
                    description="The server failed to return valid HTML or blocked the crawler.",
                    client_impact="Visitors and search engine bots cannot access your website, resulting in 100% loss of potential leads.",
                    recommended_fix="Verify DNS records, firewall configurations, and web server health.",
                    agency_pitch_angle="Emergency technical hosting and infrastructure triage.",
                    confidence="Verified"
                )
            ]

        # 1. SEO FLAWS (from seo_report)
        if seo_report:
            if seo_report.title_status == "MISSING":
                flaws.append(FlawItem(
                    category="SEO",
                    title="Missing Page Title Tag",
                    severity="CRITICAL",
                    description="The website has no <title> tag, preventing Google from understanding what the site is about.",
                    client_impact="Without a title tag, search engines cannot index your page headline, starving your business of organic search leads.",
                    recommended_fix="Add a 50-60 character keyword-focused <title> tag containing your brand and core services.",
                    agency_pitch_angle="Pitch On-Page SEO optimization to immediately boost organic Google impressions.",
                    confidence="Verified"
                ))
            elif seo_report.title_status == "TOO_SHORT":
                flaws.append(FlawItem(
                    category="SEO",
                    title=f"Short Title Tag ({seo_report.title_length} chars)",
                    severity="WARNING",
                    description=f"Title tag is only {seo_report.title_length} characters ('{seo_report.title_tag}'), under-utilizing commercial search terms.",
                    client_impact="Competitors with descriptive keyword titles rank ahead of you on Google for lucrative search terms.",
                    recommended_fix="Expand title tag to 45-60 characters with targeted industry and regional keywords.",
                    agency_pitch_angle="Pitch keyword metadata overhaul to capture untapped category search volume.",
                    confidence="Verified"
                ))

            if seo_report.meta_desc_status == "MISSING":
                flaws.append(FlawItem(
                    category="SEO",
                    title="Missing Meta Description Tag",
                    severity="CRITICAL",
                    description="No meta description is specified in the page head.",
                    client_impact="Google creates automated snippets from random text fragments. Low click-through rates (CTR) waste first-page search impressions.",
                    recommended_fix="Write a persuasive 150-160 character meta description highlighting benefits and a clear call to action.",
                    agency_pitch_angle="Pitch conversion-optimized copywriting for homepage and core landing pages.",
                    confidence="Verified"
                ))

            if len(seo_report.h1_tags) == 0:
                flaws.append(FlawItem(
                    category="SEO",
                    title="Zero <h1> Headings Detected",
                    severity="CRITICAL",
                    description="The page lacks a primary <h1> heading tag, violating HTML hierarchy standards.",
                    client_impact="Search engines cannot determine the central topical authority of this page, depressing keyword rankings.",
                    recommended_fix="Add a single <h1> heading tag featuring your primary offering above the fold.",
                    agency_pitch_angle="On-page structural content audit to lift organic search placement.",
                    confidence="Verified"
                ))
            elif len(seo_report.h1_tags) > 1:
                flaws.append(FlawItem(
                    category="SEO",
                    title=f"Multiple ({len(seo_report.h1_tags)}) <h1> Headings Found",
                    severity="WARNING",
                    description="The document contains multiple <h1> tags, diluting keyword signals.",
                    client_impact="Confuses search engine crawlers regarding primary topical focus.",
                    recommended_fix="Consolidate headings into a single <h1> tag and use <h2> and <h3> for secondary sections.",
                    agency_pitch_angle="Header hierarchy optimization.",
                    confidence="Verified"
                ))

            if seo_report.canonical_status == "MISSING":
                flaws.append(FlawItem(
                    category="SEO",
                    title="Missing Canonical Tag",
                    severity="WARNING",
                    description="No self-referential canonical tag is configured (<link rel='canonical'>).",
                    client_impact="Parameters, UTM tags, and duplicate URLs dilute link equity and cause internal ranking competition.",
                    recommended_fix="Add an absolute canonical tag to each page pointing to the preferred canonical URL.",
                    agency_pitch_angle="Technical SEO cleanup to consolidate domain authority.",
                    confidence="Verified"
                ))

            if seo_report.images_missing_alt > 0:
                flaws.append(FlawItem(
                    category="SEO",
                    title=f"{seo_report.images_missing_alt} Image(s) Missing Alt Text",
                    severity="WARNING",
                    description="Several images lack descriptive alt attributes.",
                    client_impact="Damages image search indexing in Google and fails ADA web accessibility compliance.",
                    recommended_fix="Add descriptive, keyword-rich alt text to all informative images.",
                    agency_pitch_angle="Accessibility & Google Image SEO optimization.",
                    confidence="Verified"
                ))

            if seo_report.broken_links_count > 0:
                flaws.append(FlawItem(
                    category="SEO",
                    title=f"{seo_report.broken_links_count} Broken Link(s) Found (HTTP 404/500)",
                    severity="CRITICAL",
                    description=f"Crawlers encountered broken links that return HTTP error codes.",
                    client_impact="Users hit dead ends and bounce; search bots waste crawl budget on broken paths.",
                    recommended_fix="Update or remove dead URLs and implement 301 redirects to relevant active pages.",
                    agency_pitch_angle="Link hygiene and crawl budget recovery.",
                    confidence="Verified"
                ))

            if not seo_report.has_schema_markup:
                flaws.append(FlawItem(
                    category="SEO",
                    title="Missing Schema.org Structured Data",
                    severity="OPPORTUNITY",
                    description="No JSON-LD schema markup was detected.",
                    client_impact="Site misses out on Google rich snippets (star ratings, prices, organization knowledge panels).",
                    recommended_fix="Inject JSON-LD structured data for Organization, WebSite, and relevant entity types.",
                    agency_pitch_angle="Rich Schema implementation to dramatically lift search CTR.",
                    confidence="Verified"
                ))

        # 2. SECURITY FLAWS (from security_report)
        if security_report:
            if not security_report.ssl_info.is_valid or not security_report.ssl_info.is_https_enforced:
                flaws.append(FlawItem(
                    category="Security",
                    title="Insecure HTTP / Invalid SSL Certificate",
                    severity="CRITICAL",
                    description="The website is served over unencrypted HTTP or has an invalid/expired SSL certificate.",
                    client_impact="Browsers display prominent 'Not Secure' warnings, causing 90%+ of visitors to immediately leave.",
                    recommended_fix="Install a valid SSL/TLS certificate and enforce automatic HTTP-to-HTTPS 301 redirection.",
                    agency_pitch_angle="Emergency SSL installation and security hardening.",
                    confidence="Verified"
                ))

            if security_report.mixed_content_count > 0:
                flaws.append(FlawItem(
                    category="Security",
                    title=f"Mixed Content Warnings ({security_report.mixed_content_count} Insecure Resources)",
                    severity="CRITICAL",
                    description="The HTTPS page loads external assets (images/scripts) over unencrypted HTTP.",
                    client_impact="Modern browsers block these resources or flag the site as partially insecure.",
                    recommended_fix="Update all resource URLs to use https:// or protocol-relative paths.",
                    agency_pitch_angle="Mixed content remediation and certificate compliance.",
                    confidence="Verified"
                ))

            if security_report.has_exposed_sensitive_files:
                flaws.append(FlawItem(
                    category="Security",
                    title="Publicly Accessible Configuration / Repository Files",
                    severity="CRITICAL",
                    description="Publicly exposed sensitive files (e.g. .env, .git) were detected on the web server.",
                    client_impact="Attackers can inspect credentials, database keys, or repository source code history.",
                    recommended_fix="Configure web server rules (Nginx/Apache/Cloudflare) to deny public access to dotfiles.",
                    agency_pitch_angle="Server infrastructure hardening and credential audit.",
                    confidence="Verified"
                ))

            missing_headers = [h.header for h in security_report.security_headers if h.status == "Missing"]
            if "Strict-Transport-Security" in missing_headers:
                flaws.append(FlawItem(
                    category="Security",
                    title="Missing HSTS Security Header",
                    severity="WARNING",
                    description="HTTP Strict Transport Security (HSTS) header is not sent by the server.",
                    client_impact="Leaves users vulnerable to SSL-stripping man-in-the-middle attacks on public Wi-Fi networks.",
                    recommended_fix="Add 'Strict-Transport-Security: max-age=31536000; includeSubDomains' to response headers.",
                    agency_pitch_angle="Browser security compliance and HSTS header deployment.",
                    confidence="Verified"
                ))

            if "Content-Security-Policy" in missing_headers:
                flaws.append(FlawItem(
                    category="Security",
                    title="Missing Content-Security-Policy (CSP)",
                    severity="WARNING",
                    description="No Content Security Policy header is configured.",
                    client_impact="Increases vulnerability to Cross-Site Scripting (XSS) and unauthorized third-party script injection.",
                    recommended_fix="Define a tailored Content-Security-Policy restricting unauthorized script sources.",
                    agency_pitch_angle="Application defense-in-depth and CSP configuration.",
                    confidence="Verified"
                ))

        # 3. PERFORMANCE & DESIGN FLAWS (from perf_report)
        if perf_report:
            if perf_report.load_time_seconds > 2.8:
                flaws.append(FlawItem(
                    category="Performance",
                    title=f"Slow Total Page Load Time ({perf_report.load_time_seconds}s)",
                    severity="CRITICAL",
                    description=f"Initial page took {perf_report.load_time_seconds} seconds to finish loading.",
                    client_impact="Over 40% of mobile users abandon a website that takes longer than 3 seconds to load.",
                    recommended_fix="Implement edge caching, gzip/brotli compression, and lazy-load below-the-fold media.",
                    agency_pitch_angle="Full-stack speed optimization to prevent ad spend waste.",
                    confidence="Verified"
                ))

            if not perf_report.responsive_audit.has_viewport_meta:
                flaws.append(FlawItem(
                    category="Performance",
                    title="Missing Mobile Viewport Configuration",
                    severity="CRITICAL",
                    description="The HTML document does not include a <meta name='viewport'> tag.",
                    client_impact="Mobile phones render the desktop layout in miniature, breaking UI interactions and failing Google Mobile-Friendly tests.",
                    recommended_fix="Add <meta name='viewport' content='width=device-width, initial-scale=1.0'> to the <head>.",
                    agency_pitch_angle="Mobile responsiveness and responsive UI overhaul.",
                    confidence="Verified"
                ))

        # 4. CONTENT & TRUST FLAWS (from content_report)
        if content_report:
            if not content_report.has_privacy_policy:
                flaws.append(FlawItem(
                    category="Content",
                    title="Missing Privacy Policy Page",
                    severity="CRITICAL",
                    description="No accessible Privacy Policy link or page was detected.",
                    client_impact="Violates Google Ads / Meta Ads policies and data protection regulations (GDPR, CCPA). Ad accounts face suspension.",
                    recommended_fix="Publish a comprehensive, compliant Privacy Policy page linked in the footer.",
                    agency_pitch_angle="Regulatory privacy compliance and ad account safety.",
                    confidence="Verified"
                ))

            if not content_report.has_terms_of_service:
                flaws.append(FlawItem(
                    category="Content",
                    title="Missing Terms of Service / Conditions",
                    severity="WARNING",
                    description="No Terms of Service agreement was located.",
                    client_impact="Leaves the business legally unprotected in disputes and reduces buyer confidence.",
                    recommended_fix="Add a clear Terms of Service link in the footer.",
                    agency_pitch_angle="Legal boilerplate & trust enhancement.",
                    confidence="Verified"
                ))

            if content_report.contact_data_consistency.get("mismatches"):
                for m in content_report.contact_data_consistency["mismatches"]:
                    flaws.append(FlawItem(
                        category="Content",
                        title="Free Email Provider Used for Business Inquiries",
                        severity="WARNING",
                        description=m,
                        client_impact="Reduces perceived credibility and brand legitimacy for high-ticket clients.",
                        recommended_fix="Set up branded Google Workspace or Microsoft 365 email addresses (@yourdomain.com).",
                        agency_pitch_angle="Corporate email setup and brand authority elevation.",
                        confidence="Verified"
                    ))

        # 5. SOCIAL MEDIA FLAWS (from social_report)
        if social_report:
            if social_report.inconsistencies:
                for inc in social_report.inconsistencies:
                    flaws.append(FlawItem(
                        category="Social",
                        title="Social Media Link Issue",
                        severity="WARNING",
                        description=inc,
                        client_impact="Visitors clicking broken or template social icons hit dead ends or see generic template pages.",
                        recommended_fix="Update social links in header and footer to direct to active, verified profiles.",
                        agency_pitch_angle="Omnichannel social profile audit and cleanup.",
                        confidence="Verified"
                    ))

            if len(social_report.missing_platforms) >= 3:
                flaws.append(FlawItem(
                    category="Social",
                    title=f"Missing Key Social Channels ({', '.join(social_report.missing_platforms[:3])})",
                    severity="OPPORTUNITY",
                    description=f"No links found for major customer acquisition channels: {', '.join(social_report.missing_platforms[:3])}.",
                    client_impact="Competitors capture search share and social traffic on untapped platforms.",
                    recommended_fix="Claim official handles and embed branded profile links.",
                    agency_pitch_angle="Multi-channel social media marketing and brand footprint expansion.",
                    confidence="Verified"
                ))

        # 6. CRO FLAWS (from conversion_report)
        if conversion_report and not conversion_report.has_above_the_fold_cta:
            flaws.append(FlawItem(
                category="CRO",
                title="No Primary Call-to-Action (CTA) Above the Fold",
                severity="CRITICAL",
                description="Visitors landing on the page cannot immediately see a prominent action button.",
                client_impact="Over 60% of visitors bounce within 5 seconds without understanding what action to take.",
                recommended_fix="Place a high-contrast CTA button (e.g. 'Get Started', 'Shop Now', 'Book a Call') in the hero section.",
                agency_pitch_angle="Hero section conversion rate redesign.",
                confidence="Verified"
            ))

        return flaws
