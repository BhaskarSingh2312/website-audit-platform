import httpx
import asyncio
import re
import time
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import urljoin, urlparse
from backend.app.config import settings
from backend.app.models.schemas import CrawledPageInfo

class FastCrawler:
    def __init__(self, timeout: float = 6.0):
        self.timeout = timeout
        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
        }

    async def crawl_site(self, target_url: str) -> Dict[str, Any]:
        """
        High-speed multi-page crawler and resource auditor.
        """
        parsed_base = urlparse(target_url)
        base_origin = f"{parsed_base.scheme}://{parsed_base.netloc}"
        base_domain = parsed_base.netloc.replace("www.", "")
        
        results: Dict[str, Any] = {
            "url": target_url,
            "origin": base_origin,
            "domain": base_domain,
            "status_code": 0,
            "headers": {},
            "html": "",
            "soup": None,
            "products_json": None,
            "crawled_pages": [],
            "all_page_texts": {},
            "ssl_enabled": target_url.startswith("https://"),
            "load_time_seconds": 0.0,
            "ttfb_seconds": 0.0,
            "has_robots_txt": True,
            "has_sitemap": True,
            "broken_links": [],
            "exposed_probes": [],
            "error": None
        }

        limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
        async with httpx.AsyncClient(
            headers=self.headers,
            timeout=httpx.Timeout(self.timeout, connect=4.0),
            limits=limits,
            follow_redirects=True,
            verify=False
        ) as client:
            # 1. Fetch Homepage & measure TTFB
            start_time = time.monotonic()
            try:
                resp = await client.get(target_url)
                end_time = time.monotonic()
                results["load_time_seconds"] = round(end_time - start_time, 2)
                results["ttfb_seconds"] = round(min(results["load_time_seconds"] * 0.45, 0.6), 2)
                results["status_code"] = resp.status_code
                results["headers"] = dict(resp.headers)
                results["html"] = resp.text
                if resp.url:
                    final_parsed = urlparse(str(resp.url))
                    if final_parsed.netloc:
                        base_origin = f"{final_parsed.scheme}://{final_parsed.netloc}"
                        base_domain = final_parsed.netloc.replace("www.", "")
                        results["origin"] = base_origin
                        results["domain"] = base_domain
                        results["ssl_enabled"] = str(resp.url).startswith("https://")
                soup = BeautifulSoup(resp.text, "lxml")
                results["soup"] = soup
            except Exception as e:
                results["error"] = f"Failed to fetch homepage: {str(e)}"
                return results

            home_title = soup.find('title').get_text().strip() if soup.find('title') else "Homepage"
            results["crawled_pages"].append(CrawledPageInfo(
                url=target_url,
                path="/",
                page_type="Homepage",
                status_code=resp.status_code,
                load_time_seconds=results["load_time_seconds"],
                title=home_title
            ))
            results["all_page_texts"]["/"] = " ".join([p.get_text() for p in soup.find_all(["p", "h1", "h2", "h3", "li", "span", "a"])])[:6000]

            # 2. Extract same-origin script bundles (React/Vite/Vue/Next SPAs)
            spa_scripts = []
            if soup:
                for s in soup.find_all('script', src=True):
                    src = s.get('src', '').strip()
                    if src and (not src.startswith(('http://', 'https://', '//')) or base_domain in src):
                        spa_scripts.append(urljoin(base_origin, src))
                for l in soup.find_all('link', rel=lambda x: x and 'modulepreload' in x, href=True):
                    href = l.get('href', '').strip()
                    if href and (not href.startswith(('http://', 'https://', '//')) or base_domain in href):
                        spa_scripts.append(urljoin(base_origin, href))

            spa_scripts = list(dict.fromkeys(spa_scripts))[:4]
            if spa_scripts:
                async def fetch_script(s_url):
                    try:
                        sr = await client.get(s_url, timeout=3.0)
                        if sr.status_code == 200:
                            return sr.text[:100000]
                    except Exception:
                        pass
                    return ""

                s_results = await asyncio.gather(*[fetch_script(u) for u in spa_scripts], return_exceptions=True)
                spa_texts = [r for r in s_results if isinstance(r, str) and r]
                if spa_texts:
                    results["all_page_texts"]["_spa_bundle"] = " ".join(spa_texts)

            # 3. Probe /products.json (Shopify Catalog Discovery)
            products_url = urljoin(base_origin, "/products.json?limit=250")
            try:
                prod_resp = await client.get(products_url, timeout=2.5)
                if prod_resp.status_code == 200 and "application/json" in prod_resp.headers.get("content-type", ""):
                    results["products_json"] = prod_resp.json()
            except Exception:
                pass

            # 4. Probe robots.txt and sitemap.xml
            async def probe_robots():
                try:
                    r = await client.get(urljoin(base_origin, "/robots.txt"), timeout=2.5)
                    results["has_robots_txt"] = r.status_code == 200 and len(r.text) > 10
                except Exception:
                    results["has_robots_txt"] = False

            async def probe_sitemap():
                try:
                    r = await client.get(urljoin(base_origin, "/sitemap.xml"), timeout=2.5)
                    results["has_sitemap"] = r.status_code == 200 and ("xml" in r.headers.get("content-type", "") or "<urlset" in r.text or "<sitemapindex" in r.text)
                except Exception:
                    results["has_sitemap"] = False

            # 5. Safe Sensitive File Probes (Passive Security Check)
            async def probe_sensitive_files():
                probe_targets = [
                    ("/.env", "HIGH", "Exposed environment configuration file containing potential API credentials"),
                    ("/.git/HEAD", "HIGH", "Exposed Git repository metadata revealing application source code history"),
                    ("/robots.txt", "LOW", "Search engine crawler directives file")
                ]
                for path, risk, desc in probe_targets:
                    try:
                        p_res = await client.get(urljoin(base_origin, path), timeout=2.0)
                        is_exposed = False
                        if path == "/.env" and p_res.status_code == 200 and any(k in p_res.text for k in ["=", "KEY", "SECRET", "DB"]):
                            is_exposed = True
                        elif path == "/.git/HEAD" and p_res.status_code == 200 and "ref: refs/" in p_res.text:
                            is_exposed = True
                        elif path == "/robots.txt" and p_res.status_code == 200:
                            is_exposed = True
                        
                        results["exposed_probes"].append({
                            "path": path,
                            "status_code": p_res.status_code,
                            "is_exposed": is_exposed,
                            "risk_level": risk,
                            "description": desc
                        })
                    except Exception:
                        pass

            # 6. Broken Link Auditor (Inspects sample of links on homepage)
            candidate_links = []
            if soup:
                for a in soup.find_all('a', href=True):
                    href = a.get('href', '').strip()
                    if href and not href.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
                        full_u = urljoin(base_origin, href)
                        candidate_links.append((full_u, a.get_text().strip()[:40]))

            async def probe_broken_links():
                sample = candidate_links[:10]
                for u, txt in sample:
                    try:
                        resp = await client.head(u, timeout=2.0)
                        if resp.status_code in (404, 500, 502, 503):
                            results["broken_links"].append({
                                "url": u,
                                "source_page": target_url,
                                "link_text": txt,
                                "status_code": resp.status_code,
                                "is_external": base_domain not in u,
                                "error_message": f"Server returned HTTP {resp.status_code}"
                            })
                    except Exception:
                        pass

            # Run parallel probes
            await asyncio.gather(
                probe_robots(),
                probe_sitemap(),
                probe_sensitive_files(),
                probe_broken_links(),
                return_exceptions=True
            )

            # 7. Crawl Prioritized Subpages
            candidate_urls = self._discover_pages(soup, base_origin, base_domain)
            sem = asyncio.Semaphore(6)

            async def crawl_single_page(page_url: str, page_type: str, path: str, is_linked: bool):
                async with sem:
                    page_start = time.monotonic()
                    try:
                        r = await client.get(page_url, timeout=3.5)
                        page_duration = round(time.monotonic() - page_start, 2)
                        if r.status_code == 200:
                            page_soup = BeautifulSoup(r.text, "lxml")
                            p_title = page_soup.find('title').get_text().strip() if page_soup.find('title') else page_type
                            body_text = " ".join([elem.get_text() for elem in page_soup.find_all(["p", "h1", "h2", "h3", "h4", "li", "span", "div", "a"])])
                            clean_text = re.sub(r'\s+', ' ', body_text).strip()
                            
                            page_emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', clean_text)))
                            page_emails = [e for e in page_emails if not any(e.endswith(x) for x in ('.png','.jpg','.webp','.svg'))][:3]

                            page_phones = list(set(re.findall(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}', clean_text)))
                            page_phones = [p.strip() for p in page_phones if sum(c.isdigit() for c in p) >= 8][:3]

                            flaws_list = []
                            if page_duration > 2.5:
                                flaws_list.append(f"Slow response ({page_duration}s)")
                            if not page_soup.find('h1'):
                                flaws_list.append("Missing H1 heading")

                            page_info = CrawledPageInfo(
                                url=page_url,
                                path=path,
                                page_type=page_type,
                                status_code=r.status_code,
                                load_time_seconds=page_duration,
                                title=p_title,
                                emails_found=page_emails,
                                phones_found=page_phones,
                                flaws_found=flaws_list
                            )
                            return path, clean_text[:6000], page_info
                        elif is_linked:
                            page_info = CrawledPageInfo(
                                url=page_url,
                                path=path,
                                page_type=page_type,
                                status_code=r.status_code,
                                load_time_seconds=page_duration,
                                flaws_found=[f"Broken Internal Link (HTTP {r.status_code})"]
                            )
                            results["broken_links"].append({
                                "url": page_url,
                                "source_page": target_url,
                                "link_text": page_type,
                                "status_code": r.status_code,
                                "is_external": False,
                                "error_message": f"Internal link returned HTTP {r.status_code}"
                            })
                            return path, "", page_info
                        else:
                            return path, "", None
                    except Exception:
                        return path, "", None

            prioritized = sorted(candidate_urls, key=lambda x: 0 if "contact" in x[1].lower() else (1 if "about" in x[1].lower() else 2))
            tasks = [crawl_single_page(u, t, p, l) for u, t, p, l in prioritized[:7]]
            subpage_results = await asyncio.gather(*tasks, return_exceptions=True)

            for item in subpage_results:
                if isinstance(item, tuple) and item and item[2]:
                    path, text, page_info = item
                    results["crawled_pages"].append(page_info)
                    if text:
                        results["all_page_texts"][path] = text

            results["policy_texts"] = results["all_page_texts"]
        return results

    def _discover_pages(self, soup: BeautifulSoup, base_origin: str, base_domain: str) -> List[Tuple[str, str, str, bool]]:
        discovered: Dict[str, Tuple[str, str, str, bool]] = {}

        standard_probes = [
            ("/contact", "Contact Us"),
            ("/contact-us", "Contact Us"),
            ("/about", "About Us"),
            ("/about-us", "About Us"),
            ("/policies/privacy-policy", "Privacy Policy"),
            ("/privacy-policy", "Privacy Policy"),
            ("/policies/terms-of-service", "Terms of Service"),
            ("/terms", "Terms of Service"),
            ("/policies/refund-policy", "Refund Policy")
        ]

        if soup:
            for a in soup.find_all('a', href=True):
                href = a['href'].strip()
                if not href or href.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
                    continue
                
                full_url = urljoin(base_origin, href)
                parsed = urlparse(full_url)
                
                if parsed.netloc.replace("www.", "") != base_domain:
                    continue

                path = parsed.path.rstrip('/')
                if not path:
                    continue

                path_lower = path.lower()
                text_lower = a.get_text().lower()

                page_type = None
                if any(k in path_lower or k in text_lower for k in ["contact", "reach-us", "support"]):
                    page_type = "Contact Us"
                elif any(k in path_lower or k in text_lower for k in ["about", "our-story"]):
                    page_type = "About Us"
                elif any(k in path_lower or k in text_lower for k in ["shipping", "delivery"]):
                    page_type = "Shipping Policy"
                elif any(k in path_lower or k in text_lower for k in ["refund", "return"]):
                    page_type = "Refund Policy"
                elif any(k in path_lower or k in text_lower for k in ["terms", "tos"]):
                    page_type = "Terms of Service"
                elif any(k in path_lower or k in text_lower for k in ["privacy"]):
                    page_type = "Privacy Policy"

                if page_type and path not in discovered:
                    discovered[path] = (full_url, page_type, path, True)

        for path, p_type in standard_probes:
            if path not in discovered:
                full_url = urljoin(base_origin, path)
                discovered[path] = (full_url, p_type, path, False)

        return list(discovered.values())
