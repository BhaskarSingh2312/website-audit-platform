import re
import asyncio
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from backend.app.models.schemas import ContactDetails

EMAIL_REGEX = re.compile(
    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    re.IGNORECASE
)

JUNK_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.svg', '.gif', '.webp', '.css', '.js', '.woff', '.woff2')
JUNK_EMAILS = (
    'sentry', 'wixpress', 'shopify', 'example.com', 'domain.com', 'schema.org',
    'test@', 'yourname@', 'email@', 'your@', 'john@', 'user@', 'name@', 'sample@',
    'demo@', 'support@example', 'hello@example', 'fake@'
)

PHONE_REGEX = re.compile(
    r'(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,5}[-.\s]?\d{4,6}'
)

INDIAN_MOBILE_REGEX = re.compile(
    r'(?:\+?91[\s\-]?)?[6789]\d{9}'
)

WHATSAPP_REGEX = re.compile(
    r'(?:wa\.me/|api\.whatsapp\.com/send\?phone=)(\+?\d{7,15})',
    re.IGNORECASE
)

SOCIAL_PATTERNS = {
    "instagram": {
        "name": "Instagram",
        "regex": re.compile(r'https?://(?:www\.)?instagram\.com/([a-zA-Z0-9_.-]+)', re.IGNORECASE),
        "icon": "instagram"
    },
    "facebook": {
        "name": "Facebook",
        "regex": re.compile(r'https?://(?:www\.)?facebook\.com/([a-zA-Z0-9_.-]+)', re.IGNORECASE),
        "icon": "facebook"
    },
    "linkedin": {
        "name": "LinkedIn",
        "regex": re.compile(r'https?://(?:www\.)?linkedin\.com/(?:company|in|school)/([a-zA-Z0-9_.-]+)', re.IGNORECASE),
        "icon": "linkedin"
    },
    "twitter": {
        "name": "Twitter / X",
        "regex": re.compile(r'https?://(?:www\.)?(?:twitter\.com|x\.com)/([a-zA-Z0-9_]+)', re.IGNORECASE),
        "icon": "twitter"
    },
    "youtube": {
        "name": "YouTube",
        "regex": re.compile(r'https?://(?:www\.)?youtube\.com/(?:c/|channel/|user/|@)?([a-zA-Z0-9_.-]+)', re.IGNORECASE),
        "icon": "youtube"
    },
    "tiktok": {
        "name": "TikTok",
        "regex": re.compile(r'https?://(?:www\.)?tiktok\.com/@?([a-zA-Z0-9_.-]+)', re.IGNORECASE),
        "icon": "tiktok"
    },
    "pinterest": {
        "name": "Pinterest",
        "regex": re.compile(r'https?://(?:www\.)?pinterest\.(?:com|co\.[a-z]{2}|[a-z]{2})/([a-zA-Z0-9_.-]+)', re.IGNORECASE),
        "icon": "pinterest"
    },
    "github": {
        "name": "GitHub",
        "regex": re.compile(r'https?://(?:www\.)?github\.com/([a-zA-Z0-9_.-]+)', re.IGNORECASE),
        "icon": "github"
    },
    "telegram": {
        "name": "Telegram",
        "regex": re.compile(r'https?://(?:t\.me|telegram\.me)/([a-zA-Z0-9_]+)', re.IGNORECASE),
        "icon": "telegram"
    },
    "discord": {
        "name": "Discord",
        "regex": re.compile(r'https?://(?:discord\.gg|discord\.com/invite)/([a-zA-Z0-9_-]+)', re.IGNORECASE),
        "icon": "discord"
    },
    "reddit": {
        "name": "Reddit",
        "regex": re.compile(r'https?://(?:www\.)?reddit\.com/(?:r|user)/([a-zA-Z0-9_]+)', re.IGNORECASE),
        "icon": "reddit"
    },
    "threads": {
        "name": "Threads",
        "regex": re.compile(r'https?://(?:www\.)?threads\.net/@?([a-zA-Z0-9_.-]+)', re.IGNORECASE),
        "icon": "threads"
    },
    "medium": {
        "name": "Medium",
        "regex": re.compile(r'https?://(?:www\.)?medium\.com/@?([a-zA-Z0-9_.-]+)', re.IGNORECASE),
        "icon": "medium"
    },
    "behance": {
        "name": "Behance",
        "regex": re.compile(r'https?://(?:www\.)?behance\.net/([a-zA-Z0-9_.-]+)', re.IGNORECASE),
        "icon": "behance"
    },
    "dribbble": {
        "name": "Dribbble",
        "regex": re.compile(r'https?://(?:www\.)?dribbble\.com/([a-zA-Z0-9_.-]+)', re.IGNORECASE),
        "icon": "dribbble"
    }
}

SOCIAL_IGNORE_PATHS = {
    'sharer', 'share', 'intent', 'sharearticle', 'pin/create', 'home', 'login', 'signup',
    'privacy', 'terms', 'help', 'search', 'hashtag', 'policies', 'dialog', 'plugins'
}

GSTIN_REGEX = re.compile(r'\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}\b')
CIN_REGEX = re.compile(r'\b[LUu]\d{5}[A-Za-z]{2}\d{4}[A-Za-z]{3}\d{6}\b')

async def extract_all_contacts(
    soup: Optional[BeautifulSoup],
    raw_html: str,
    all_page_texts: Dict[str, str],
    gemini_agent: Any = None
) -> ContactDetails:
    emails: set[str] = set()
    phone_numbers: set[str] = set()
    whatsapp_numbers: set[str] = set()
    addresses: set[str] = set()
    social_links: Dict[str, str] = {}
    social_profiles: List[Dict[str, Any]] = []
    registered_business_name: Optional[str] = None
    gstin_or_cin: Optional[str] = None
    support_hours: Optional[str] = None
    founders_or_team: List[str] = []

    visible_home_text = soup.get_text(separator=" ") if soup else ""
    all_visible_text = visible_home_text + " " + " ".join(all_page_texts.values())
    all_combined_text = raw_html + " " + " ".join(all_page_texts.values())

    # 1. Emails from mailto: links and across pages
    if soup:
        for mailto in soup.select('a[href^="mailto:"]'):
            href = mailto.get('href', '')
            clean = href.replace('mailto:', '').split('?')[0].strip().lower()
            if clean and '@' in clean:
                emails.add(clean)

    for match in EMAIL_REGEX.findall(all_combined_text):
        clean = match.strip().lower()
        if not any(clean.endswith(ext) for ext in JUNK_EXTENSIONS):
            if not any(junk in clean for junk in JUNK_EMAILS):
                emails.add(clean)

    # 2. Phones and WhatsApp Links
    if soup:
        for tel in soup.select('a[href^="tel:"]'):
            href = tel.get('href', '')
            clean = href.replace('tel:', '').split('?')[0].strip()
            if clean and sum(c.isdigit() for c in clean) >= 7:
                phone_numbers.add(clean)

    for wa_match in WHATSAPP_REGEX.findall(all_combined_text):
        clean_wa = wa_match.strip()
        if len(clean_wa) >= 10:
            if clean_wa.startswith('91') and len(clean_wa) == 12:
                formatted_wa = f"+91 {clean_wa[2:]}"
            elif not clean_wa.startswith('+'):
                formatted_wa = f"+{clean_wa}"
            else:
                formatted_wa = clean_wa
            whatsapp_numbers.add(formatted_wa)
            phone_numbers.add(formatted_wa)

    # Indian Mobile Formats (e.g. +91 9125682891 or 919125982891)
    for ind_match in INDIAN_MOBILE_REGEX.findall(all_combined_text):
        clean = ind_match.strip()
        digits = re.sub(r'\D', '', clean)
        if digits in ("9876543210", "1234567890", "0123456789", "0000000000"):
            continue
        if len(digits) == 10:
            phone_numbers.add(f"+91 {digits}")
        elif len(digits) == 12 and digits.startswith("91"):
            phone_numbers.add(f"+91 {digits[2:]}")

    # General International Phone formats
    for p_match in PHONE_REGEX.findall(all_visible_text):
        clean = p_match.strip()
        digits = re.sub(r'\D', '', clean)
        if digits in ("9876543210", "1234567890", "0123456789", "0000000000"):
            continue
        if 10 <= len(digits) <= 13:
            if not digits.startswith(("000000", "177", "178", "2024", "2025", "2026", "2027", "1306")):
                if len(set(digits)) > 3:
                    if len(digits) == 10 and not clean.startswith('+'):
                        phone_numbers.add(f"+91 {digits}")
                    else:
                        phone_numbers.add(clean)

    # 3. Omnichannel Social Profiles Extraction
    # A. Search DOM a[href] tags
    if soup:
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            for key, conf in SOCIAL_PATTERNS.items():
                if key not in social_links:
                    m = conf["regex"].search(href)
                    if m:
                        handle = m.group(1).strip('/')
                        if handle.lower() not in SOCIAL_IGNORE_PATHS:
                            clean_url = m.group(0).rstrip('/')
                            social_links[key] = clean_url
                            social_profiles.append({
                                "platform": conf["name"],
                                "key": key,
                                "url": clean_url,
                                "handle": f"@{handle}" if not handle.startswith('@') else handle,
                                "icon": conf["icon"]
                            })

    # B. Search raw text, script bundles & combined crawl text
    for key, conf in SOCIAL_PATTERNS.items():
        if key not in social_links:
            m = conf["regex"].search(all_combined_text)
            if m:
                handle = m.group(1).strip('/')
                if handle.lower() not in SOCIAL_IGNORE_PATHS:
                    clean_url = m.group(0).rstrip('/')
                    social_links[key] = clean_url
                    social_profiles.append({
                        "platform": conf["name"],
                        "key": key,
                        "url": clean_url,
                        "handle": f"@{handle}" if not handle.startswith('@') else handle,
                        "icon": conf["icon"]
                    })

    # C. Also extract WhatsApp as a social profile if present
    if whatsapp_numbers and "whatsapp" not in social_links:
        wa_num = list(whatsapp_numbers)[0]
        digits = re.sub(r'\D', '', wa_num)
        wa_url = f"https://wa.me/{digits}"
        social_links["whatsapp"] = wa_url
        social_profiles.append({
            "platform": "WhatsApp",
            "key": "whatsapp",
            "url": wa_url,
            "handle": wa_num,
            "icon": "whatsapp"
        })

    # 4. Business IDs (GSTIN / CIN)
    gst_match = GSTIN_REGEX.search(all_combined_text)
    if gst_match:
        gstin_or_cin = f"GSTIN: {gst_match.group(0)}"
    else:
        cin_match = CIN_REGEX.search(all_combined_text)
        if cin_match:
            gstin_or_cin = f"CIN: {cin_match.group(0)}"

    # 5. Physical Address via Regex (search visible human text only to avoid minified JS variables)
    addr_match = re.search(r'(?:Address|Headquarters|Registered Office|Location)[\s:]+([A-Za-z0-9\s,\-\./#]{10,120})', all_visible_text, re.I)
    if addr_match:
        clean_addr = addr_match.group(1).strip()
        clean_addr = re.sub(r'<[^>]+>', '', clean_addr).strip()
        if len(clean_addr) > 10 and not any(w in clean_addr.lower() for w in ["comment", "cookie", "http", "privacy", "policy"]):
            addresses.add(clean_addr)

    # 6. Gemini AI Prompt Extraction (Timed Out safely to prevent lag)
    if gemini_agent:
        try:
            contact_snippets = []
            for path, text in all_page_texts.items():
                if any(k in path.lower() for k in ["contact", "about", "policy", "terms", "footer", "reach"]):
                    contact_snippets.append(f"--- Page: {path} ---\n{text[:2000]}")
            
            combined_snippets = "\n".join(contact_snippets)[:5000]
            if combined_snippets:
                ai_data = await asyncio.wait_for(
                    gemini_agent.extract_contacts_with_prompt(combined_snippets),
                    timeout=5.0
                )
                if ai_data:
                    for e in ai_data.get("emails", []):
                        if e and '@' in e:
                            emails.add(e.strip().lower())
                    for p in ai_data.get("phone_numbers", []):
                        if p and sum(c.isdigit() for c in p) >= 7:
                            phone_numbers.add(p.strip())
                    for wa in ai_data.get("whatsapp_numbers", []):
                        if wa:
                            whatsapp_numbers.add(wa.strip())
                    for addr in ai_data.get("addresses", []):
                        if addr and len(addr) > 8:
                            addresses.add(addr.strip())
                    if ai_data.get("registered_business_name"):
                        registered_business_name = ai_data["registered_business_name"]
                    if ai_data.get("gstin_or_cin"):
                        gstin_or_cin = ai_data["gstin_or_cin"]
                    if ai_data.get("support_hours"):
                        support_hours = ai_data["support_hours"]
                    if ai_data.get("founders_or_team"):
                        founders_or_team = ai_data["founders_or_team"]
        except Exception:
            pass

    return ContactDetails(
        emails=sorted(list(emails))[:12],
        phone_numbers=sorted(list(phone_numbers))[:8],
        whatsapp_numbers=sorted(list(whatsapp_numbers))[:4],
        addresses=sorted(list(addresses))[:3],
        registered_business_name=registered_business_name,
        gstin_or_cin=gstin_or_cin,
        support_hours=support_hours,
        social_links=social_links,
        social_profiles=social_profiles,
        founders_or_team=founders_or_team[:5]
    )

