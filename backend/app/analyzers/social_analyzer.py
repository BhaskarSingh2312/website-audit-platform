import re
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from backend.app.models.schemas import DiscoveredSocialProfile, SocialDiscoveryReport, FlawItem

SOCIAL_PATTERNS = {
    "instagram": {
        "name": "Instagram",
        "regex": re.compile(r'https?://(?:www\.)?instagram\.com/([a-zA-Z0-9_.-]+)', re.I),
        "icon": "instagram",
        "essential": True
    },
    "facebook": {
        "name": "Facebook",
        "regex": re.compile(r'https?://(?:www\.)?facebook\.com/([a-zA-Z0-9_.-]+)', re.I),
        "icon": "facebook",
        "essential": True
    },
    "linkedin": {
        "name": "LinkedIn",
        "regex": re.compile(r'https?://(?:www\.)?linkedin\.com/(?:company|in|school)/([a-zA-Z0-9_.-]+)', re.I),
        "icon": "linkedin",
        "essential": True
    },
    "twitter": {
        "name": "X (Twitter)",
        "regex": re.compile(r'https?://(?:www\.)?(?:twitter\.com|x\.com)/([a-zA-Z0-9_]+)', re.I),
        "icon": "twitter",
        "essential": True
    },
    "youtube": {
        "name": "YouTube",
        "regex": re.compile(r'https?://(?:www\.)?youtube\.com/(?:c/|channel/|user/|@)?([a-zA-Z0-9_.-]+)', re.I),
        "icon": "youtube",
        "essential": True
    },
    "tiktok": {
        "name": "TikTok",
        "regex": re.compile(r'https?://(?:www\.)?tiktok\.com/@?([a-zA-Z0-9_.-]+)', re.I),
        "icon": "tiktok",
        "essential": False
    },
    "pinterest": {
        "name": "Pinterest",
        "regex": re.compile(r'https?://(?:www\.)?pinterest\.(?:com|co\.[a-z]{2}|[a-z]{2})/([a-zA-Z0-9_.-]+)', re.I),
        "icon": "pinterest",
        "essential": False
    },
    "github": {
        "name": "GitHub",
        "regex": re.compile(r'https?://(?:www\.)?github\.com/([a-zA-Z0-9_.-]+)', re.I),
        "icon": "github",
        "essential": False
    },
    "reddit": {
        "name": "Reddit",
        "regex": re.compile(r'https?://(?:www\.)?reddit\.com/(?:r|user)/([a-zA-Z0-9_]+)', re.I),
        "icon": "reddit",
        "essential": False
    },
    "threads": {
        "name": "Threads",
        "regex": re.compile(r'https?://(?:www\.)?threads\.net/@?([a-zA-Z0-9_.-]+)', re.I),
        "icon": "threads",
        "essential": False
    },
    "discord": {
        "name": "Discord",
        "regex": re.compile(r'https?://(?:discord\.gg|discord\.com/invite)/([a-zA-Z0-9_-]+)', re.I),
        "icon": "discord",
        "essential": False
    },
    "telegram": {
        "name": "Telegram",
        "regex": re.compile(r'https?://(?:t\.me|telegram\.me)/([a-zA-Z0-9_]+)', re.I),
        "icon": "telegram",
        "essential": False
    }
}

IGNORE_HANDLES = {
    'sharer', 'share', 'intent', 'sharearticle', 'pin', 'create', 'home',
    'login', 'signup', 'privacy', 'terms', 'help', 'search', 'hashtag',
    'policies', 'dialog', 'plugins', 'about', 'legal', 'feed'
}

class SocialAnalyzer:
    def analyze(
        self,
        soup: Optional[BeautifulSoup],
        raw_html: str,
        all_page_texts: Dict[str, str],
        brand_name: str,
        domain: str
    ) -> SocialDiscoveryReport:
        discovered: Dict[str, DiscoveredSocialProfile] = {}
        inconsistencies: List[str] = []

        if not soup:
            return SocialDiscoveryReport(
                total_profiles_found=0,
                profiles=[],
                missing_platforms=["Instagram", "Facebook", "LinkedIn", "X (Twitter)", "YouTube"],
                summary="Unable to parse HTML to discover social profiles."
            )

        # 1. Inspect Header & Nav
        header_el = soup.find(['header', 'nav'])
        if header_el:
            self._scan_element(header_el, "Header Navigation", discovered, brand_name)

        # 2. Inspect Footer
        footer_el = soup.find(['footer'])
        if footer_el:
            self._scan_element(footer_el, "Footer Section", discovered, brand_name)

        # 3. Inspect General Page Links
        self._scan_element(soup, "Page Content / Links", discovered, brand_name)

        # 4. Inspect Meta Tags (twitter:site, twitter:creator, og:see_also)
        for meta in soup.find_all('meta'):
            name = (meta.get('name') or meta.get('property') or '').lower()
            content = (meta.get('content') or '').strip()
            if not content:
                continue

            if name in ('twitter:site', 'twitter:creator'):
                handle = content.replace('@', '').strip()
                if handle and handle.lower() not in IGNORE_HANDLES:
                    url = f"https://x.com/{handle}"
                    if "twitter" not in discovered:
                        discovered["twitter"] = DiscoveredSocialProfile(
                            platform="X (Twitter)",
                            url=url,
                            handle=f"@{handle}",
                            icon="twitter",
                            found_in=["Metadata (twitter:site)"],
                            verified_brand_match=self._matches_brand(handle, brand_name, domain)
                        )
                    else:
                        if "Metadata (twitter:site)" not in discovered["twitter"].found_in:
                            discovered["twitter"].found_in.append("Metadata (twitter:site)")

            elif name == 'og:see_also':
                self._match_url(content, "Metadata (og:see_also)", discovered, brand_name)

        # 5. Inspect JSON-LD Schema (sameAs array)
        for s in soup.find_all('script', type='application/ld+json'):
            try:
                import json
                data = json.loads(s.get_text())
                if isinstance(data, dict):
                    same_as = data.get('sameAs') or []
                    if isinstance(same_as, str):
                        same_as = [same_as]
                    for url in same_as:
                        if isinstance(url, str):
                            self._match_url(url, "JSON-LD Schema (sameAs)", discovered, brand_name)
            except Exception:
                pass

        # 6. Evaluate placeholder / template links & brand consistency
        profile_list = list(discovered.values())
        for prof in profile_list:
            # Check for dummy handles
            clean_handle = (prof.handle or '').lower().replace('@', '')
            if clean_handle in ('yourname', 'yourpage', 'username', 'handle', 'yourbrand', 'page', '#'):
                prof.is_placeholder_or_broken = True
                inconsistencies.append(f"Template/placeholder social profile found on {prof.platform} ({prof.url})")
            elif not prof.verified_brand_match:
                inconsistencies.append(f"{prof.platform} handle '{prof.handle}' significantly differs from brand name '{brand_name}'")

        # 7. Identify Missing Essential Platforms
        missing_platforms = []
        for key, info in SOCIAL_PATTERNS.items():
            if info["essential"] and key not in discovered:
                missing_platforms.append(info["name"])

        summary = (
            f"Successfully identified {len(profile_list)} official social profile(s) across "
            f"{len(set(p.platform for p in profile_list))} platform(s). "
        )
        if missing_platforms:
            summary += f"Missing essential social integrations: {', '.join(missing_platforms[:3])}."

        return SocialDiscoveryReport(
            total_profiles_found=len(profile_list),
            profiles=profile_list,
            missing_platforms=missing_platforms,
            inconsistencies=inconsistencies,
            summary=summary
        )

    def _scan_element(
        self,
        element: Any,
        location: str,
        discovered: Dict[str, DiscoveredSocialProfile],
        brand_name: str
    ):
        for a in element.find_all('a', href=True):
            href = a['href'].strip()
            self._match_url(href, location, discovered, brand_name)

    def _match_url(
        self,
        href: str,
        location: str,
        discovered: Dict[str, DiscoveredSocialProfile],
        brand_name: str
    ):
        for key, p_data in SOCIAL_PATTERNS.items():
            match = p_data["regex"].match(href)
            if match:
                handle = match.group(1).split('?')[0].split('/')[0].strip()
                if handle.lower() in IGNORE_HANDLES or len(handle) < 2:
                    continue

                clean_url = f"{href.split('?')[0].rstrip('/')}"
                if key not in discovered:
                    discovered[key] = DiscoveredSocialProfile(
                        platform=p_data["name"],
                        url=clean_url,
                        handle=f"@{handle}" if not handle.startswith('@') else handle,
                        icon=p_data["icon"],
                        found_in=[location],
                        is_placeholder_or_broken=handle.lower() in ('#', 'yourpage', 'username'),
                        verified_brand_match=self._matches_brand(handle, brand_name, "")
                    )
                else:
                    if location not in discovered[key].found_in:
                        discovered[key].found_in.append(location)

    def _matches_brand(self, handle: str, brand_name: str, domain: str) -> bool:
        if not brand_name and not domain:
            return True
        h = re.sub(r'[^a-zA-Z0-9]', '', handle).lower()
        b = re.sub(r'[^a-zA-Z0-9]', '', brand_name).lower()
        d = re.sub(r'[^a-zA-Z0-9]', '', domain.split('.')[0]).lower()
        if not h or not b:
            return True
        return b in h or h in b or d in h or h in d

