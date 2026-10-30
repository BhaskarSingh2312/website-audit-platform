import io
from typing import Dict, Any
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

class ReportExporter:
    def generate_excel_report(self, report: Dict[str, Any]) -> io.BytesIO:
        """
        Generates a professional, multi-sheet .xlsx audit workbook using openpyxl.
        """
        wb = Workbook()
        
        # Colors
        header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid") # Dark Slate
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        title_font = Font(name="Calibri", size=14, bold=True, color="0F172A")
        bold_font = Font(name="Calibri", size=11, bold=True)
        regular_font = Font(name="Calibri", size=11)
        
        thin_border = Border(
            left=Side(style='thin', color='E2E8F0'),
            right=Side(style='thin', color='E2E8F0'),
            top=Side(style='thin', color='E2E8F0'),
            bottom=Side(style='thin', color='E2E8F0')
        )

        def style_header(row):
            for cell in row:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        # ---------------------------------------------------------
        # SHEET 1: Executive Overview
        # ---------------------------------------------------------
        ws_overview = wb.active
        ws_overview.title = "Executive Overview"
        ws_overview.views.sheetView[0].showGridLines = True

        ws_overview.append(["WEBSITE DIGITAL AUDIT & INTELLIGENCE REPORT"])
        ws_overview.cell(row=1, column=1).font = title_font
        ws_overview.append([])

        metadata_rows = [
            ("Target URL", report.get("url", "")),
            ("Domain", report.get("domain", "")),
            ("Brand Name", report.get("brand_name", "")),
            ("Audit Timestamp", report.get("timestamp", "")),
            ("Platform / CMS", report.get("tech_stack", {}).get("platform", "Unknown")),
            ("Hosting / Infrastructure", report.get("tech_stack", {}).get("hosting", "Cloud")),
            ("Country of Operation", report.get("country_of_operation", "Unknown")),
            ("Overall Health Score", f"{report.get('health_score', 70)} / 100"),
            ("SEO Score", f"{report.get('seo_score', 70)} / 100"),
            ("Security Score", f"{report.get('security_score', 80)} / 100"),
            ("Performance Score", f"{report.get('performance_score', 75)} / 100"),
            ("Conversion / CRO Score", f"{report.get('conversion_score', 65)} / 100"),
        ]

        for label, val in metadata_rows:
            r = ws_overview.max_row + 1
            ws_overview.append([label, str(val)])
            ws_overview.cell(row=r, column=1).font = bold_font
            ws_overview.cell(row=r, column=2).font = regular_font

        ws_overview.append([])
        ws_overview.append(["Executive Summary"])
        ws_overview.cell(row=ws_overview.max_row, column=1).font = title_font
        ws_overview.append([report.get("executive_summary", "")])
        ws_overview.cell(row=ws_overview.max_row, column=1).font = regular_font

        # ---------------------------------------------------------
        # SHEET 2: Flaws & Actionable Fixes
        # ---------------------------------------------------------
        ws_flaws = wb.create_sheet(title="Flaws & Action Plan")
        ws_flaws.views.sheetView[0].showGridLines = True
        ws_flaws.append(["Category", "Severity", "Issue Title", "Description", "Recommended Fix", "Confidence"])
        style_header(ws_flaws[1])

        for flaw in report.get("flaws", []):
            ws_flaws.append([
                flaw.get("category", "Technical"),
                flaw.get("severity", "WARNING"),
                flaw.get("title", ""),
                flaw.get("description", ""),
                flaw.get("recommended_fix", ""),
                flaw.get("confidence", "Verified")
            ])

        # ---------------------------------------------------------
        # SHEET 3: Social Media & Contacts
        # ---------------------------------------------------------
        ws_social = wb.create_sheet(title="Social & Contacts")
        ws_social.views.sheetView[0].showGridLines = True

        ws_social.append(["DISCOVERED SOCIAL MEDIA PROFILES"])
        ws_social.cell(row=1, column=1).font = title_font
        ws_social.append(["Platform", "Profile URL", "Handle", "Found In Locations", "Verified Brand Match"])
        style_header(ws_social[2])

        for prof in report.get("social_discovery", {}).get("profiles", []):
            ws_social.append([
                prof.get("platform", ""),
                prof.get("url", ""),
                prof.get("handle", ""),
                ", ".join(prof.get("found_in", [])),
                "Yes" if prof.get("verified_brand_match", True) else "Review Needed"
            ])

        ws_social.append([])
        ws_social.append(["VERIFIED CONTACT DETAILS"])
        ws_social.cell(row=ws_social.max_row, column=1).font = title_font
        
        contacts = report.get("contacts", {})
        ws_social.append(["Contact Type", "Discovered Details"])
        style_header(ws_social[ws_social.max_row])
        
        ws_social.append(["Direct Emails", ", ".join(contacts.get("emails", [])) or "None"])
        ws_social.append(["Phone Numbers", ", ".join(contacts.get("phone_numbers", [])) or "None"])
        ws_social.append(["WhatsApp", ", ".join(contacts.get("whatsapp_numbers", [])) or "None"])
        ws_social.append(["Physical Addresses", "; ".join(contacts.get("addresses", [])) or "None"])
        ws_social.append(["Registered Business Name", contacts.get("registered_business_name") or "N/A"])
        ws_social.append(["Tax ID / GSTIN / CIN", contacts.get("gstin_or_cin") or "N/A"])

        # ---------------------------------------------------------
        # SHEET 4: Advertising Intelligence
        # ---------------------------------------------------------
        ws_ads = wb.create_sheet(title="Advertising Intelligence")
        ws_ads.views.sheetView[0].showGridLines = True

        ws_ads.append(["INSTALLED ADVERTISING PIXELS & CONVERSION TAGS"])
        ws_ads.cell(row=1, column=1).font = title_font
        ws_ads.append(["Advertising Platform", "Pixel / Account ID", "Detection Source"])
        style_header(ws_ads[2])

        for px in report.get("ad_intelligence", {}).get("installed_pixels", []):
            ws_ads.append([
                px.get("platform", ""),
                px.get("pixel_id") or "Detected",
                px.get("detected_via", "")
            ])

        ws_ads.append([])
        ws_ads.append(["AD PLATFORM PROFILES & CAMPAIGN LINKS"])
        ws_ads.cell(row=ws_ads.max_row, column=1).font = title_font
        ws_ads.append(["Platform", "Has Active Pixel", "Spend Profile", "Key Findings", "Transparency Link"])
        style_header(ws_ads[ws_ads.max_row])

        for pi in report.get("ad_intelligence", {}).get("platform_insights", []):
            ws_ads.append([
                pi.get("platform_name", ""),
                "Yes" if pi.get("has_active_pixel") else "No",
                pi.get("ad_spend_profile", "Inactive"),
                pi.get("key_findings", ""),
                pi.get("transparency_search_url", "")
            ])

        # ---------------------------------------------------------
        # SHEET 5: SEO Audit & Broken Links
        # ---------------------------------------------------------
        ws_seo = wb.create_sheet(title="Technical SEO")
        ws_seo.views.sheetView[0].showGridLines = True

        seo_data = report.get("seo_audit", {})
        ws_seo.append(["Metric / Element", "Status / Value"])
        style_header(ws_seo[1])
        ws_seo.append(["SEO Score", f"{seo_data.get('seo_score', 70)} / 100"])
        ws_seo.append(["Title Tag", seo_data.get("title_tag", "None")])
        ws_seo.append(["Title Status", seo_data.get("title_status", "OPTIMAL")])
        ws_seo.append(["Meta Description", seo_data.get("meta_description", "None")])
        ws_seo.append(["Meta Desc Status", seo_data.get("meta_desc_status", "OPTIMAL")])
        ws_seo.append(["Canonical URL", seo_data.get("canonical_url", "Missing")])
        ws_seo.append(["Robots.txt Status", seo_data.get("robots_txt_status", "Accessible")])
        ws_seo.append(["Sitemap.xml Status", seo_data.get("sitemap_status", "Accessible")])
        ws_seo.append(["Schema Types Detected", ", ".join(seo_data.get("schema_types_detected", [])) or "None"])
        ws_seo.append(["Total Images Analyzed", seo_data.get("images_total", 0)])
        ws_seo.append(["Images Missing Alt Text", seo_data.get("images_missing_alt", 0)])

        ws_seo.append([])
        ws_seo.append(["BROKEN LINKS DIRECTORY"])
        ws_seo.cell(row=ws_seo.max_row, column=1).font = title_font
        ws_seo.append(["Broken URL", "HTTP Status", "Source Page", "External Link?"])
        style_header(ws_seo[ws_seo.max_row])

        for bl in seo_data.get("broken_links", []):
            ws_seo.append([
                bl.get("url", ""),
                bl.get("status_code", 404),
                bl.get("source_page", ""),
                "Yes" if bl.get("is_external") else "No"
            ])

        # ---------------------------------------------------------
        # SHEET 6: Security Audit
        # ---------------------------------------------------------
        ws_sec = wb.create_sheet(title="Security Audit")
        ws_sec.views.sheetView[0].showGridLines = True

        sec_data = report.get("security_audit", {})
        ssl_data = sec_data.get("ssl_info", {})
        ws_sec.append(["SSL/TLS & CERTIFICATE INFORMATION"])
        ws_sec.cell(row=1, column=1).font = title_font
        ws_sec.append(["Property", "Value"])
        style_header(ws_sec[2])
        ws_sec.append(["SSL Valid", "Yes" if ssl_data.get("is_valid") else "No"])
        ws_sec.append(["Issuer", ssl_data.get("issuer", "Unknown")])
        ws_sec.append(["Protocol Version", ssl_data.get("protocol_version", "TLSv1.3")])
        ws_sec.append(["Days Remaining Until Expiry", ssl_data.get("days_remaining", 0)])

        ws_sec.append([])
        ws_sec.append(["SECURITY HEADERS COMPLIANCE"])
        ws_sec.cell(row=ws_sec.max_row, column=1).font = title_font
        ws_sec.append(["Header", "Status", "Severity", "Description"])
        style_header(ws_sec[ws_sec.max_row])

        for sh in sec_data.get("security_headers", []):
            ws_sec.append([
                sh.get("header", ""),
                sh.get("status", "Missing"),
                sh.get("severity", "WARNING"),
                sh.get("description", "")
            ])

        # ---------------------------------------------------------
        # SHEET 7: Technology Stack
        # ---------------------------------------------------------
        ws_tech = wb.create_sheet(title="Technology Stack")
        ws_tech.views.sheetView[0].showGridLines = True

        ws_tech.append(["Technology Name", "Category", "Confidence", "Version", "Detected Via"])
        style_header(ws_tech[1])

        for t in report.get("tech_stack", {}).get("technologies", []):
            ws_tech.append([
                t.get("name", ""),
                t.get("category", "General"),
                t.get("confidence", "High"),
                t.get("version") or "Latest",
                t.get("detected_via", "Signature")
            ])

        # Auto-fit column widths across all sheets
        for ws in wb.worksheets:
            for col in ws.columns:
                max_len = 0
                col_letter = get_column_letter(col[0].column)
                for cell in col:
                    if cell.value:
                        lines = str(cell.value).split("\n")
                        line_max = max(len(l) for l in lines)
                        if line_max > max_len:
                            max_len = line_max
                ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 55)

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)
        return stream

exporter = ReportExporter()

