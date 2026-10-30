import re
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from backend.app.models.schemas import (
    PerformanceAuditReport,
    AssetWeightBreakdown,
    CoreWebVitalsEstimate,
    ResponsiveAuditInfo
)

class PerformanceAnalyzer:
    def analyze(
        self,
        soup: Optional[BeautifulSoup],
        raw_html: str,
        load_time_seconds: float,
        ttfb_seconds: float
    ) -> PerformanceAuditReport:
        html_bytes = len(raw_html.encode('utf-8'))
        html_kb = round(html_bytes / 1024, 1)

        scripts_count = 0
        styles_count = 0
        images_count = 0
        fonts_count = 0
        responsive_images_count = 0
        has_media_queries = False

        if soup:
            scripts = soup.find_all('script')
            scripts_count = len(scripts)

            link_styles = soup.find_all('link', rel=lambda r: r and 'stylesheet' in r)
            style_tags = soup.find_all('style')
            styles_count = len(link_styles) + len(style_tags)

            images = soup.find_all('img')
            images_count = len(images)
            for img in images:
                if img.get('srcset') or img.get('sizes'):
                    responsive_images_count += 1

            for s in style_tags:
                if '@media' in s.get_text():
                    has_media_queries = True
                    break

            fonts = soup.find_all('link', rel=lambda r: r and 'font' in str(r).lower())
            fonts_count = len(fonts)

        # Estimate asset sizes based on counts and standard web averages
        est_scripts_kb = round(scripts_count * 38.5, 1)
        est_styles_kb = round(styles_count * 22.0, 1)
        est_images_kb = round(images_count * 65.0, 1)
        total_kb = round(html_kb + est_scripts_kb + est_styles_kb + est_images_kb, 1)

        assets_breakdown = AssetWeightBreakdown(
            total_kb=total_kb,
            html_kb=html_kb,
            scripts_count=scripts_count,
            scripts_kb=est_scripts_kb,
            styles_count=styles_count,
            styles_kb=est_styles_kb,
            images_count=images_count,
            images_kb=est_images_kb,
            fonts_count=fonts_count
        )

        # Responsive Audit
        has_viewport = False
        viewport_val = None
        layout_issues = []
        if soup:
            vp = soup.find('meta', attrs={'name': lambda x: x and x.lower() == 'viewport'})
            if vp:
                has_viewport = True
                viewport_val = vp.get('content', '')
                if 'width=device-width' not in viewport_val.lower():
                    layout_issues.append("Viewport tag is missing 'width=device-width', causing mobile scaling distortion.")
            else:
                layout_issues.append("Missing <meta name='viewport'> tag: mobile browsers will render a zoomed-out desktop page.")

        if not has_media_queries and styles_count > 0:
            layout_issues.append("No inline @media queries detected in page markup. Verify external stylesheet responsiveness.")

        if images_count > 4 and responsive_images_count == 0:
            layout_issues.append("Images lack srcset/sizes attributes; mobile devices download desktop-resolution assets.")

        responsive_info = ResponsiveAuditInfo(
            has_viewport_meta=has_viewport,
            viewport_content=viewport_val,
            has_media_queries=has_media_queries or styles_count > 0,
            uses_responsive_images=responsive_images_count > 0,
            desktop_ready=True,
            tablet_ready=has_viewport,
            mobile_ready=has_viewport and len(layout_issues) == 0,
            layout_issues=layout_issues
        )

        # Estimated Core Web Vitals
        fcp = round(max(0.4, ttfb_seconds + 0.5), 2)
        lcp = round(max(0.9, load_time_seconds * 0.95), 2)
        cls = 0.04 if has_viewport else 0.28
        inp = "Good (<200ms)" if scripts_count < 25 else "Needs Improvement (>200ms)"

        cwv = CoreWebVitalsEstimate(
            fcp_seconds=fcp,
            lcp_seconds=lcp,
            cls_score=cls,
            inp_rating=inp
        )

        # Performance Scoring
        perf_score = 100
        bottlenecks = []
        recommendations = []

        if load_time_seconds > 3.0:
            perf_score -= 25
            bottlenecks.append(f"High total page load time ({load_time_seconds}s). 40%+ of mobile visitors abandon pages loading >3s.")
            recommendations.append("Implement asset CDN caching, gzip/brotli compression, and lazy-load below-the-fold images.")
        elif load_time_seconds > 2.0:
            perf_score -= 12
            bottlenecks.append(f"Moderate load latency ({load_time_seconds}s). Room to improve Core Web Vitals LCP score.")

        if ttfb_seconds > 0.8:
            perf_score -= 15
            bottlenecks.append(f"Sluggish server response / TTFB ({ttfb_seconds}s). Edge caching or server optimization needed.")
            recommendations.append("Deploy Cloudflare or Vercel Edge caching to achieve <200ms server response times worldwide.")

        if scripts_count > 30:
            perf_score -= 12
            bottlenecks.append(f"Heavy JavaScript payload ({scripts_count} script tags). Script execution blocks the main browser thread.")
            recommendations.append("Audit and defer non-critical analytics and tracking scripts using 'defer' or async loading.")

        if total_kb > 2500:
            perf_score -= 10
            bottlenecks.append(f"Estimated page size ({total_kb} KB) exceeds 2.5 MB recommended maximum.")
            recommendations.append("Compress images into WebP/AVIF and minify CSS/JS bundles.")

        perf_score = min(max(perf_score, 30), 98)

        # Responsiveness Score
        resp_score = 100
        if not has_viewport:
            resp_score -= 50
        resp_score -= len(layout_issues) * 15
        resp_score = min(max(resp_score, 25), 100)

        return PerformanceAuditReport(
            performance_score=perf_score,
            responsiveness_score=resp_score,
            load_time_seconds=load_time_seconds,
            ttfb_seconds=ttfb_seconds,
            assets=assets_breakdown,
            estimated_cwv=cwv,
            responsive_audit=responsive_info,
            performance_bottlenecks=bottlenecks,
            recommended_optimizations=recommendations
        )

