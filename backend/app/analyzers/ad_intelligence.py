import re
import urllib.parse
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from backend.app.models.schemas import (
    AdIntelligenceReport,
    AdPixelInfo,
    AdvertisingPlatformInsight
)

class AdIntelligenceAnalyzer:
    def _clean_brand_name(self, brand_name: str, domain: str) -> str:
        """Derive a clean, searchable brand name suitable for ad libraries for ANY website."""
        cand = brand_name.strip() if brand_name else ""
        if not cand or cand.lower() in ["home", "welcome", "official", "shop", "store"]:
            cand = domain.replace("www.", "").split('.')[0].replace('-', ' ').title()
        
        # Remove common title delimiters and trailing fluff
        for sep in ["–", "-", "|", ":", "•", "—", "/"]:
            if sep in cand:
                parts = [p.strip() for p in cand.split(sep)]
                cand = parts[0] if len(parts[0]) > 2 else parts[-1]
                break
        
        # Strip generic marketing prefixes
        cand = re.sub(r"^(?:Welcome to|Official Website of|Shop at|The)\s+", "", cand, flags=re.I).strip()
        # Keep alphanumeric, spaces, and clean text
        cand = re.sub(r"[^\w\s\.-]", "", cand).strip()
        return cand if cand else domain.replace("www.", "").split('.')[0].title()

    def _extract_handles(self, social_profiles: Optional[List[Any]]) -> Dict[str, str]:
        """Extract social media handles from discovered profiles for ANY website."""
        handles = {}
        if not social_profiles:
            return handles

        for prof in social_profiles:
            platform = getattr(prof, 'platform', None) or (prof.get('platform') if isinstance(prof, dict) else '')
            handle = getattr(prof, 'handle', None) or (prof.get('handle') if isinstance(prof, dict) else '')
            url = getattr(prof, 'url', None) or (prof.get('url') if isinstance(prof, dict) else '')
            
            p_lower = str(platform).lower()
            if not handle and url:
                match = re.search(r"(?:facebook\.com|instagram\.com|x\.com|twitter\.com)/([a-zA-Z0-9_\.\-]+)", url)
                if match and match.group(1) not in ['share', 'sharer', 'intent', 'p', 'explore', 'pages', 'plugins']:
                    handle = match.group(1)

            if handle:
                clean_h = handle.lstrip('@').strip().rstrip('/')
                if 'facebook' in p_lower and 'facebook' not in handles:
                    handles['facebook'] = clean_h
                elif 'instagram' in p_lower and 'instagram' not in handles:
                    handles['instagram'] = clean_h
                elif ('twitter' in p_lower or 'x' in p_lower) and 'twitter' not in handles:
                    handles['twitter'] = clean_h
                elif 'linkedin' in p_lower and 'linkedin' not in handles:
                    handles['linkedin'] = clean_h

        return handles

    def analyze(
        self,
        soup: Optional[BeautifulSoup],
        raw_html: str,
        brand_name: str,
        domain: str,
        social_profiles: Optional[List[Any]] = None
    ) -> AdIntelligenceReport:
        installed_pixels: List[AdPixelInfo] = []
        platform_insights: List[AdvertisingPlatformInsight] = []
        past_campaign_evidence: List[str] = []
        
        clean_brand = self._clean_brand_name(brand_name, domain)
        handles = self._extract_handles(social_profiles)
        html_text = raw_html or ""

        # Check for UTM / campaign tracking artifacts in page HTML across any site
        utm_matches = list(set(re.findall(r"(?:utm_source|utm_campaign|utm_medium|fbclid|gclid|msclkid|ttclid)", html_text, re.I)))

        # -------------------------------------------------------------
        # 1. Meta / Facebook & Instagram Advertising
        # -------------------------------------------------------------
        meta_ids = list(set(re.findall(r"fbq\([\'\"]init[\'\"],\s*[\'\"](\d+)[\'\"]", html_text)))
        # Config / tr signals / Shopify / WooCommerce apps
        meta_signals = list(set(re.findall(r"connect\.facebook\.net/signals/config/(\d+)", html_text)))
        meta_tr = list(set(re.findall(r"facebook\.com/tr\?[^\'\"\s]*id=(\d+)", html_text)))
        meta_json = list(set(re.findall(r"[\'\"](?:facebook_pixel_id|fb_pixel_id|pixel_id)[\'\"]\s*:\s*[\'\"](\d+)[\'\"]", html_text, re.I)))
        
        all_meta_ids = list(dict.fromkeys(meta_ids + meta_signals + meta_tr + meta_json))
        has_generic_fb = "connect.facebook.net" in html_text or "_fbp" in html_text or "fbevents.js" in html_text
        if not all_meta_ids and has_generic_fb:
            all_meta_ids = ["Detected (Generic Script)"]
        
        # Check meta tags for Facebook App ID / Page ID
        fb_app_id = None
        if soup:
            meta_app = soup.find("meta", property="fb:app_id") or soup.find("meta", attrs={"name": "fb:app_id"})
            if meta_app and meta_app.get("content"):
                fb_app_id = meta_app["content"].strip()

        has_meta = len(all_meta_ids) > 0 or fb_app_id is not None
        for pid in all_meta_ids:
            installed_pixels.append(AdPixelInfo(
                platform="Meta (Facebook & Instagram)",
                pixel_id=pid if "Generic" not in pid else None,
                detected_via="Script Tag (fbq / fbevents)" if "Generic" not in pid else "fbevents.js / _fbp script"
            ))

        if fb_app_id:
            installed_pixels.append(AdPixelInfo(
                platform="Meta App ID (fb:app_id)",
                pixel_id=fb_app_id,
                detected_via="<meta property='fb:app_id'>"
            ))

        # Build Universal Meta transparency URLs
        meta_active_url = (
            f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all"
            f"&country=ALL&q={urllib.parse.quote(clean_brand)}"
        )
        meta_past_url = (
            f"https://www.facebook.com/ads/library/?active_status=inactive&ad_type=all"
            f"&country=ALL&q={urllib.parse.quote(clean_brand)}"
        )
        meta_all_url = (
            f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all"
            f"&country=ALL&q={urllib.parse.quote(clean_brand)}"
        )

        fb_handle = handles.get('facebook') or handles.get('instagram')
        handle_search_url = None
        if fb_handle:
            handle_search_url = (
                f"https://www.facebook.com/ads/library/?active_status=all&ad_type=all"
                f"&country=ALL&q={urllib.parse.quote(fb_handle)}"
            )

        meta_historical_notes = []
        if has_meta:
            detected_id = all_meta_ids[0] if all_meta_ids else fb_app_id
            meta_historical_notes.append(f"Meta Pixel installed ({detected_id}). The website has active conversion tracking for Meta Ads.")
            past_campaign_evidence.append(f"Meta Pixel ({detected_id}): Configured conversion tracking for Facebook & Instagram ad campaigns.")
        else:
            meta_historical_notes.append("No Meta Pixel detected on page. No evidence of active or recent Meta ad conversion funnels.")

        platform_insights.append(AdvertisingPlatformInsight(
            platform_name="Meta Ads (Facebook & Instagram)",
            has_active_pixel=has_meta,
            pixel_ids=[pid for pid in all_meta_ids if "Generic" not in pid],
            campaign_status="Active Retargeting Configured" if has_meta else "Untapped / Inactive",
            estimated_active_ads=1 if has_meta else 0,
            transparency_search_url=meta_all_url,
            active_ads_search_url=meta_active_url,
            past_ads_search_url=meta_past_url,
            all_ads_search_url=meta_all_url,
            target_handle=fb_handle,
            handle_search_url=handle_search_url,
            historical_ad_indicators=meta_historical_notes,
            ad_spend_profile="Active Retargeting / Scaling" if has_meta else "Untapped",
            key_findings=(
                f"Meta Pixel ({all_meta_ids[0] if all_meta_ids else 'active'}) tracks conversions for Facebook & Instagram campaigns."
                if has_meta else
                "No Meta Pixel found on page source. Check Meta Ad Library to verify any un-pixeled brand awareness ads or historical ads."
            )
        ))

        # -------------------------------------------------------------
        # 2. Google Ads & Tag Manager (AW-XXXXX / GTM-XXXXX)
        # -------------------------------------------------------------
        google_ads_ids = list(set(re.findall(r"[\'\"](AW-\d+)[\'\"]", html_text, re.I)))
        gtm_ids = list(set(re.findall(r"[\'\"](GTM-[A-Z0-9]+)[\'\"]", html_text, re.I)))
        floodlight_ids = list(set(re.findall(r"[\'\"](DC-\d+)[\'\"]", html_text, re.I)))
        has_google_ads = len(google_ads_ids) > 0 or len(gtm_ids) > 0 or len(floodlight_ids) > 0

        for gid in google_ads_ids:
            installed_pixels.append(AdPixelInfo(
                platform="Google Ads Conversion Tag",
                pixel_id=gid,
                detected_via="gtag script config"
            ))
            past_campaign_evidence.append(f"Google Ads Conversion Tag ({gid}): Account setup for Search/Display/Shopping ads.")

        for gid in gtm_ids:
            installed_pixels.append(AdPixelInfo(
                platform="Google Tag Manager (GTM)",
                pixel_id=gid,
                detected_via="gtm.js script container"
            ))

        for fid in floodlight_ids:
            installed_pixels.append(AdPixelInfo(
                platform="Google Floodlight / Campaign Manager 360",
                pixel_id=fid,
                detected_via="Doubleclick tag"
            ))
            past_campaign_evidence.append(f"Google Floodlight Tag ({fid}): Enterprise ad campaign tracking.")

        google_transparency_url = (
            f"https://adstransparency.google.com/?region=anywhere&domain={urllib.parse.quote(domain)}"
        )
        google_brand_url = (
            f"https://adstransparency.google.com/?region=anywhere&q={urllib.parse.quote(clean_brand)}"
        )

        google_historical_notes = []
        if google_ads_ids:
            google_historical_notes.append(f"Google Conversion Tag ({', '.join(google_ads_ids)}) active on site.")
        elif gtm_ids:
            google_historical_notes.append(f"Google Tag Manager container ({gtm_ids[0]}) deployed.")
        else:
            google_historical_notes.append("No Google Ads conversion tags found.")

        platform_insights.append(AdvertisingPlatformInsight(
            platform_name="Google Ads (Search, Display & YouTube)",
            has_active_pixel=has_google_ads,
            pixel_ids=google_ads_ids + gtm_ids + floodlight_ids,
            campaign_status="Active Tracking Configured" if has_google_ads else "Untapped",
            estimated_active_ads=1 if has_google_ads else 0,
            transparency_search_url=google_transparency_url,
            active_ads_search_url=google_transparency_url,
            past_ads_search_url=google_transparency_url,
            all_ads_search_url=google_brand_url,
            target_handle=domain,
            handle_search_url=google_transparency_url,
            historical_ad_indicators=google_historical_notes,
            ad_spend_profile="Active Search/Display Advertiser" if google_ads_ids else ("Tag Manager Installed" if gtm_ids else "Inactive"),
            key_findings=(
                f"Google Conversion Tag ({', '.join(google_ads_ids)}) active on site. Paid search or Shopping campaigns in use."
                if google_ads_ids else
                (f"Google Tag Manager ({gtm_ids[0]}) deployed. Marketing and conversion tags are managed dynamically."
                 if gtm_ids else "No Google Ads conversion tags found. Organic Google traffic is not augmented with paid Search.")
            )
        ))

        # -------------------------------------------------------------
        # 3. LinkedIn Insight Tag
        # -------------------------------------------------------------
        linkedin_ids = list(set(re.findall(r"_linkedin_partner_id\s*=\s*[\'\"]?(\d+)[\'\"]?", html_text)))
        has_linkedin = len(linkedin_ids) > 0 or "snap.licdn.com" in html_text
        if has_linkedin:
            lid = linkedin_ids[0] if linkedin_ids else "Active"
            installed_pixels.append(AdPixelInfo(
                platform="LinkedIn Insight Tag",
                pixel_id=lid if lid != "Active" else None,
                detected_via="snap.licdn.com partner tag"
            ))
            past_campaign_evidence.append(f"LinkedIn Insight Tag ({lid}): Configured for B2B retargeting.")
        
        linkedin_ad_url = f"https://www.linkedin.com/ad-library/search?keyword={urllib.parse.quote(clean_brand)}"
        platform_insights.append(AdvertisingPlatformInsight(
            platform_name="LinkedIn Sponsored Content & Ads",
            has_active_pixel=has_linkedin,
            pixel_ids=linkedin_ids,
            campaign_status="Active B2B Tracking" if has_linkedin else "Untapped",
            transparency_search_url=linkedin_ad_url,
            active_ads_search_url=linkedin_ad_url,
            all_ads_search_url=linkedin_ad_url,
            target_handle=handles.get('linkedin'),
            ad_spend_profile="Active B2B Advertiser" if has_linkedin else "Inactive",
            key_findings=(
                f"LinkedIn Insight Tag ({linkedin_ids[0] if linkedin_ids else 'active'}) detected. Site runs B2B retargeting or lead gen campaigns."
                if has_linkedin else "No LinkedIn tracking pixel detected. High potential for B2B accounts."
            )
        ))

        # -------------------------------------------------------------
        # 4. TikTok Ads Pixel
        # -------------------------------------------------------------
        tiktok_ids = list(set(re.findall(r"ttq\.load\([\'\"]([A-Z0-9]+)[\'\"]\)", html_text, re.I)))
        has_tiktok = len(tiktok_ids) > 0 or "analytics.tiktok.com" in html_text
        if has_tiktok:
            tid = tiktok_ids[0] if tiktok_ids else "Active"
            installed_pixels.append(AdPixelInfo(
                platform="TikTok Ads Pixel",
                pixel_id=tid if tid != "Active" else None,
                detected_via="analytics.tiktok.com script"
            ))
            past_campaign_evidence.append(f"TikTok Ads Pixel ({tid}): Configured for video conversion tracking.")
        
        platform_insights.append(AdvertisingPlatformInsight(
            platform_name="TikTok Ads",
            has_active_pixel=has_tiktok,
            pixel_ids=tiktok_ids,
            campaign_status="Active Gen-Z Audience Reach" if has_tiktok else "Untapped",
            transparency_search_url="https://library.tiktok.com/ads",
            all_ads_search_url="https://library.tiktok.com/ads",
            ad_spend_profile="Active Video Advertiser" if has_tiktok else "Inactive",
            key_findings=(
                f"TikTok Pixel ({tiktok_ids[0] if tiktok_ids else 'active'}) active. Site leverages short-form video advertising."
                if has_tiktok else "No TikTok Pixel detected. Opportunity for viral creative acquisition."
            )
        ))

        # -------------------------------------------------------------
        # 5. Pinterest, Twitter/X, Microsoft Bing, Snapchat, Criteo, Taboola
        # -------------------------------------------------------------
        # Pinterest Tag
        pinterest_ids = list(set(re.findall(r"pintrk\([\'\"]load[\'\"],\s*[\'\"]([A-Z0-9]+)[\'\"]\)", html_text, re.I)))
        if len(pinterest_ids) > 0 or "pintrk" in html_text:
            installed_pixels.append(AdPixelInfo(
                platform="Pinterest Tag",
                pixel_id=pinterest_ids[0] if pinterest_ids else None,
                detected_via="pintrk script"
            ))
            past_campaign_evidence.append("Pinterest Tag: Configured for shopping & catalog ads.")

        # X / Twitter Ads Pixel
        twitter_ids = list(set(re.findall(r"twq\([\'\"]init[\'\"],\s*[\'\"]([a-z0-9]+)[\'\"]\)", html_text, re.I)))
        if len(twitter_ids) > 0 or "static.ads-twitter.com" in html_text:
            installed_pixels.append(AdPixelInfo(
                platform="X (Twitter) Ads Pixel",
                pixel_id=twitter_ids[0] if twitter_ids else None,
                detected_via="static.ads-twitter.com script"
            ))
            past_campaign_evidence.append("X/Twitter Ads Pixel: Configured for social campaign tracking.")

        # Microsoft Bing UET
        bing_ids = list(set(re.findall(r"bat\.bing\.com/bat\.js|uetq\.push", html_text, re.I)))
        if bing_ids:
            installed_pixels.append(AdPixelInfo(
                platform="Microsoft Advertising (Bing UET)",
                detected_via="bat.bing.com script"
            ))
            past_campaign_evidence.append("Microsoft Advertising (Bing UET): Configured for Bing Search ads.")

        # Snapchat Pixel
        if "sc-static.net" in html_text or "snaptr(" in html_text:
            installed_pixels.append(AdPixelInfo(platform="Snapchat Pixel", detected_via="snaptr script"))
            past_campaign_evidence.append("Snapchat Pixel: Installed for mobile audience ads.")
        
        # Criteo Dynamic Retargeting
        if "static.criteo.net" in html_text or "criteo_q" in html_text:
            installed_pixels.append(AdPixelInfo(platform="Criteo Dynamic Retargeting", detected_via="criteo script"))
            past_campaign_evidence.append("Criteo Dynamic Retargeting: Configured for e-commerce catalog retargeting.")

        # Taboola / Outbrain Content Discovery
        if "_tfa.push" in html_text or "tr.taboola.com" in html_text:
            installed_pixels.append(AdPixelInfo(platform="Taboola Pixel", detected_via="tr.taboola.com script"))
            past_campaign_evidence.append("Taboola Pixel: Native advertising network tracking.")
        if "OBR.extern" in html_text or "widgets.outbrain.com" in html_text:
            installed_pixels.append(AdPixelInfo(platform="Outbrain Pixel", detected_via="widgets.outbrain.com script"))
            past_campaign_evidence.append("Outbrain Pixel: Native advertising network tracking.")

        # Check UTM artifacts
        if utm_matches:
            past_campaign_evidence.append(
                f"Campaign tracking artifacts found in page source: {', '.join(utm_matches)}. "
                "Indicates external marketing campaigns, newsletter promos, or partner referral links."
            )

        past_advertiser_detected = len(installed_pixels) > 0 or len(utm_matches) > 0

        # Summary spend profile
        total_active_pixels = len(installed_pixels)
        if total_active_pixels >= 3:
            overall_spend = "Omnichannel (Multi-Platform Ad Footprint)"
            opportunity = (
                f"Brand maintains an active omnichannel ad tracking footprint across {total_active_pixels} platforms. "
                "Any landing page load delay or broken checkout link directly drains substantial ad budget."
            )
        elif total_active_pixels >= 1:
            overall_spend = "Active Advertiser (Targeted Channels)"
            opportunity = (
                f"Active tracking detected on {', '.join([p.platform_name.split()[0] for p in platform_insights if p.has_active_pixel])}. "
                "High leverage to audit conversion funnels and eliminate friction."
            )
        elif utm_matches:
            overall_spend = "Campaign Marketer (UTM / Referral Tracking)"
            opportunity = (
                "UTM parameters and campaign tokens observed in page content. Brand has active or past campaign workflows, "
                "but lacks dedicated Meta or Google retargeting pixels."
            )
        else:
            overall_spend = "Inactive / Untapped Ad Footprint"
            opportunity = (
                "No major advertising pixels detected. Competitors are actively bidding on commercial search keywords "
                "and social feeds without competition from this brand."
            )

        if not past_campaign_evidence:
            past_campaign_evidence.append(
                "No conversion pixels (Meta Pixel, Google Ads AW-, TikTok, etc.) or tracking tags detected in page source. "
                "No historical ad funnel configuration found."
            )

        return AdIntelligenceReport(
            overall_spend_profile=overall_spend,
            has_active_ads=total_active_pixels > 0,
            past_advertiser_detected=past_advertiser_detected,
            past_campaign_evidence=past_campaign_evidence,
            total_active_ads_detected=total_active_pixels,
            installed_pixels=installed_pixels,
            platform_insights=platform_insights,
            sample_creatives=[
                {"platform": "Meta Ad Library (Active)", "url": meta_active_url},
                {"platform": "Meta Ad Library (Historical)", "url": meta_past_url},
                {"platform": "Google Ads Transparency", "url": google_transparency_url},
                {"platform": "LinkedIn Ad Library", "url": linkedin_ad_url}
            ],
            marketing_opportunity=opportunity
        )
