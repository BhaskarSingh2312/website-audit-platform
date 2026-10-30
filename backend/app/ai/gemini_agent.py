import json
import re
import asyncio
from typing import Dict, Any, Optional, List
import google.generativeai as genai
from backend.app.config import settings
from backend.app.models.schemas import AuditReport, FlawItem, ChatMessage

SUPPORTED_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro"
]

def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Safely extracts and parses JSON even if wrapped in markdown code blocks."""
    if not text:
        return None
    cleaned = text.strip()
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(1)
    elif "{" in cleaned and "}" in cleaned:
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        cleaned = cleaned[start:end]
    try:
        return json.loads(cleaned)
    except Exception:
        return None

class GeminiAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = None

        if self.api_key:
            try:
                genai.configure(api_key=self.api_key, transport="rest")
                for candidate in SUPPORTED_MODELS:
                    try:
                        self.model = genai.GenerativeModel(candidate)
                        break
                    except Exception:
                        continue
            except Exception:
                self.model = None

    async def extract_contacts_with_prompt(self, page_snippets: str) -> Optional[Dict[str, Any]]:
        if not self.model:
            return None

        prompt = f"""
You are an advanced Contact Information & Business Entity Extraction Agent.
Analyze the following website text:
{page_snippets[:5000]}

Extract:
1. "emails": List of all direct contact emails.
2. "phone_numbers": List of all phone numbers.
3. "whatsapp_numbers": WhatsApp numbers if found.
4. "addresses": Physical office/store addresses.
5. "registered_business_name": Registered company name.
6. "gstin_or_cin": GSTIN, CIN, or VAT number.
7. "support_hours": Business hours.
8. "founders_or_team": Founders or leadership names.

Respond ONLY with valid JSON:
{{
  "emails": [],
  "phone_numbers": [],
  "whatsapp_numbers": [],
  "addresses": [],
  "registered_business_name": null,
  "gstin_or_cin": null,
  "support_hours": null,
  "founders_or_team": []
}}
"""
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.model.generate_content,
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                ),
                timeout=12.0
            )
            return extract_json_from_text(response.text)
        except Exception:
            return None

    async def synthesize_audit_report(self, raw_report: Dict[str, Any]) -> Dict[str, Any]:
        if self.model:
            try:
                return await asyncio.wait_for(self._call_gemini_synthesis(raw_report), timeout=15.0)
            except Exception:
                pass
        return self._rule_based_synthesis(raw_report)

    async def _call_gemini_synthesis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        crawled_summary = [f"{p.get('path')} ({p.get('page_type')})" for p in data.get('crawled_pages', [])[:5]]
        prompt = f"""
You are an expert Chief Technology Officer, Digital Strategist, and Technical Auditor.
Comprehensive Audit Data for:
- Domain: {data.get('domain')}
- Brand: {data.get('brand_name')}
- Platform: {data.get('tech_stack', {}).get('platform')}
- Country: {data.get('country_of_operation')}
- SEO Score: {data.get('seo_audit', {}).get('seo_score')}/100
- Security Score: {data.get('security_audit', {}).get('security_score')}/100
- Performance Score: {data.get('performance_audit', {}).get('performance_score')}/100
- Advertising Footprint: {data.get('ad_intelligence', {}).get('overall_spend_profile')}
- Social Profiles Found: {data.get('social_discovery', {}).get('total_profiles_found')}
- Pages Analyzed: {', '.join(crawled_summary)}
- Top Flaws: {[f.get('title') for f in data.get('flaws', [])[:5]]}

Instructions:
1. Provide a sharp, professional 3-sentence Executive Audit Summary highlighting key strengths, critical vulnerabilities, and growth opportunities.
2. Provide an overall Health Score (0 to 100) reflecting technical condition, SEO visibility, security posture, and user experience.
3. Write an irresistible, value-first executive outreach email (Subject + Body in a consultative, authoritative tone).

Return ONLY JSON:
{{
  "health_score": 78,
  "executive_summary": "...",
  "pitch_email_subject": "...",
  "pitch_email_body": "..."
}}
"""
        response = await asyncio.to_thread(
            self.model.generate_content,
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        parsed = extract_json_from_text(response.text) or {}
        return {
            "health_score": int(parsed.get("health_score", 75)),
            "executive_summary": parsed.get("executive_summary", ""),
            "pitch_email_subject": parsed.get("pitch_email_subject", ""),
            "pitch_email_body": parsed.get("pitch_email_body", "")
        }

    def _rule_based_synthesis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        brand = data.get("brand_name") or data.get("domain", "Your Website")
        platform = data.get("tech_stack", {}).get("platform", "Modern Web")
        flaws = data.get("flaws", [])
        ad_report = data.get("ad_intelligence", {})
        has_ads = ad_report.get("has_active_ads", False)
        
        seo_score = data.get("seo_audit", {}).get("seo_score", 70)
        sec_score = data.get("security_audit", {}).get("security_score", 80)
        perf_score = data.get("performance_audit", {}).get("performance_score", 75)
        
        calculated_score = int((seo_score + sec_score + perf_score) / 3)
        critical_count = sum(1 for f in flaws if f.get("severity") == "CRITICAL")
        warning_count = sum(1 for f in flaws if f.get("severity") == "WARNING")
        
        top_flaw = flaws[0]["title"] if flaws else "mobile performance bottlenecks"
        
        exec_summary = (
            f"Comprehensive digital audit of {brand} ({platform}) yielded an overall Health Score of {calculated_score}/100. "
            f"We identified {critical_count} critical issues (including {top_flaw.lower()}) and {warning_count} optimization opportunities across SEO, security, and performance. "
        )
        if has_ads:
            exec_summary += (
                f"With active advertising tags detected, resolving these conversion bottlenecks and technical leaks "
                "will directly prevent wasted ad spend and lift customer acquisition efficiency."
            )
        else:
            exec_summary += (
                "The site currently shows untapped advertising potential; resolving technical SEO and speed bottlenecks "
                "will prepare the brand for scaled organic and paid acquisition."
            )

        subject = f"Audit findings for {brand}: Quick fixes for {top_flaw.lower()}"
        body = (
            f"Hi {brand} team,\n\n"
            f"I recently ran an in-depth technical and digital intelligence audit of {brand}'s web presence on {platform}.\n\n"
            f"Your overall architecture is solid, but I spotted a few high-impact bottlenecks—notably around {top_flaw.lower()}—"
            f"that are likely leaking organic traffic and lowering conversion rates.\n\n"
            f"Addressing these typically provides an immediate lift in search rankings, security compliance, and user retention.\n\n"
            f"Would you be open to a quick 3-minute executive summary of the highest-impact fixes?\n\n"
            f"Best regards,\n[Your Name]\nDigital Intelligence Consultant"
        )

        return {
            "health_score": calculated_score,
            "executive_summary": exec_summary,
            "pitch_email_subject": subject,
            "pitch_email_body": body
        }

    async def chat(self, user_message: str, report_context: Dict[str, Any], history: List[ChatMessage]) -> str:
        if self.model:
            try:
                system_instruction = (
                    "You are the Lead Digital Intelligence & Website Audit Copilot. "
                    "You are answering questions about an audited website.\n"
                    f"Audited Target Context:\n"
                    f"- Domain: {report_context.get('domain')}\n"
                    f"- Brand: {report_context.get('brand_name')}\n"
                    f"- Platform: {report_context.get('tech_stack', {}).get('platform')}\n"
                    f"- Health Score: {report_context.get('health_score')}/100\n"
                    f"- SEO Score: {report_context.get('seo_score')}/100\n"
                    f"- Security Score: {report_context.get('security_score')}/100\n"
                    f"- Performance Score: {report_context.get('performance_score')}/100\n"
                    f"- Contacts: {report_context.get('contacts', {})}\n"
                    f"- Social Media: {report_context.get('social_discovery', {})}\n"
                    f"- Advertising: {report_context.get('ad_intelligence', {})}\n"
                    f"- Security: {report_context.get('security_audit', {})}\n"
                    f"- Flaws: {[f.get('title') for f in report_context.get('flaws', [])]}\n\n"
                    "Provide crisp, expert, actionable responses formatted in clean GitHub markdown."
                )
                
                history_text = ""
                if history:
                    recent = history[-6:]
                    history_lines = [f"{getattr(m, 'role', 'User').capitalize()}: {getattr(m, 'content', '')}" for m in recent]
                    history_text = "\nPrevious Conversation:\n" + "\n".join(history_lines) + "\n"
                
                full_prompt = f"{system_instruction}\n{history_text}\nCurrent User Question: {user_message}"
                
                response = await asyncio.wait_for(
                    asyncio.to_thread(self.model.generate_content, full_prompt),
                    timeout=20.0
                )
                if response and response.text:
                    return response.text
            except Exception:
                pass

        msg_lower = user_message.lower()
        brand = report_context.get("brand_name") or report_context.get("domain", "the website")
        contacts = report_context.get("contacts", {})
        flaws = report_context.get("flaws", [])
        
        if "security" in msg_lower or "ssl" in msg_lower or "header" in msg_lower:
            sec = report_context.get("security_audit", {})
            ssl_info = sec.get("ssl_info", {})
            return (
                f"### 🛡️ Security Audit Summary for **{brand}**\n\n"
                f"- **Security Score:** {sec.get('security_score', 80)}/100 (Grade: {sec.get('security_grade', 'B')})\n"
                f"- **SSL Certificate:** {'Valid' if ssl_info.get('is_valid') else 'Invalid'} (Issuer: {ssl_info.get('issuer')}, Days Left: {ssl_info.get('days_remaining')})\n"
                f"- **Missing Headers:** {sec.get('missing_headers_count', 0)}\n"
                f"- **Mixed Content Issues:** {sec.get('mixed_content_count', 0)}\n"
                f"- **Exposed Sensitive Files:** {'Yes - CRITICAL' if sec.get('has_exposed_sensitive_files') else 'None detected (Safe)'}"
            )
        elif "seo" in msg_lower:
            seo = report_context.get("seo_audit", {})
            return (
                f"### 🔍 SEO Audit Summary for **{brand}**\n\n"
                f"- **SEO Score:** {seo.get('seo_score', 70)}/100\n"
                f"- **Title Tag:** {seo.get('title_tag') or 'Missing'} ({seo.get('title_status')})\n"
                f"- **Meta Description:** {seo.get('meta_desc_status')}\n"
                f"- **Broken Links:** {seo.get('broken_links_count', 0)}\n"
                f"- **Images Missing Alt:** {seo.get('images_missing_alt', 0)} / {seo.get('images_total', 0)}\n"
                f"- **Schema Markup:** {'Present' if seo.get('has_schema_markup') else 'Missing'}"
            )
        elif "contact" in msg_lower or "email" in msg_lower:
            emails = ", ".join(contacts.get("emails", [])) or "None found"
            phones = ", ".join(contacts.get("phone_numbers", [])) or "None found"
            return (
                f"### 📬 Verified Contacts for **{brand}**\n\n"
                f"- **Emails:** {emails}\n"
                f"- **Phone Numbers:** {phones}\n"
                f"- **WhatsApp:** {', '.join(contacts.get('whatsapp_numbers', [])) or 'None'}\n"
                f"- **Addresses:** {'; '.join(contacts.get('addresses', [])) or 'None'}\n"
                f"- **Entity:** {contacts.get('registered_business_name') or 'N/A'}"
            )
        else:
            return (
                f"### 📊 Intelligence Summary for **{brand}** ({report_context.get('domain')})\n\n"
                f"- **Overall Health Score:** {report_context.get('health_score', 70)}/100\n"
                f"- **SEO Score:** {report_context.get('seo_score', 70)}/100\n"
                f"- **Security Score:** {report_context.get('security_score', 80)}/100\n"
                f"- **Performance Score:** {report_context.get('performance_score', 75)}/100\n"
                f"- **Total Flaws Found:** {len(flaws)}\n\n"
                f"You can ask me to draft client outreach emails, explain technical fixes, or break down security/SEO flaws in detail!"
            )
