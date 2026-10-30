from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class AuditRequest(BaseModel):
    url: str = Field(..., description="Target website URL to audit", example="https://example.com")
    gemini_api_key: Optional[str] = Field(None, description="Optional custom Gemini API Key override")

class CrawledPageInfo(BaseModel):
    url: str
    path: str
    page_type: str = "Standard Page" # Homepage, Contact, About, Policies, Catalog, Services
    status_code: int = 200
    load_time_seconds: float = 0.0
    title: Optional[str] = None
    emails_found: List[str] = Field(default_factory=list)
    phones_found: List[str] = Field(default_factory=list)
    flaws_found: List[str] = Field(default_factory=list)

class BrokenLinkInfo(BaseModel):
    url: str
    source_page: str
    link_text: str = ""
    status_code: int
    is_external: bool = False
    error_message: Optional[str] = None

class FlawItem(BaseModel):
    category: str = Field(..., description="SEO, Security, Performance, Advertising, Content, Social, CRO, Technical")
    title: str
    severity: str = Field(..., description="CRITICAL, WARNING, or OPPORTUNITY")
    description: str
    client_impact: str = Field(default="", description="Why this causes loss of traffic, revenue, trust or security risks")
    recommended_fix: str = Field(default="", description="Recommended action to resolve this issue")
    agency_pitch_angle: str = Field(default="", description="How to position this fix for clients or stakeholders")
    page_affected: Optional[str] = "Sitewide / Homepage"
    confidence: str = Field(default="Verified", description="Verified, Estimated, or Inferred")

# 1. Social Media Discovery & Analysis
class DiscoveredSocialProfile(BaseModel):
    platform: str
    url: str
    handle: Optional[str] = None
    icon: Optional[str] = None
    found_in: List[str] = Field(default_factory=list) # e.g. ["Header", "Footer", "Meta Tag", "Schema"]
    is_placeholder_or_broken: bool = False
    verified_brand_match: bool = True

class SocialDiscoveryReport(BaseModel):
    total_profiles_found: int = 0
    profiles: List[DiscoveredSocialProfile] = Field(default_factory=list)
    missing_platforms: List[str] = Field(default_factory=list)
    inconsistencies: List[str] = Field(default_factory=list)
    summary: str = ""

# Contacts & Business Entity
class ContactDetails(BaseModel):
    emails: List[str] = Field(default_factory=list)
    phone_numbers: List[str] = Field(default_factory=list)
    whatsapp_numbers: List[str] = Field(default_factory=list)
    addresses: List[str] = Field(default_factory=list)
    registered_business_name: Optional[str] = None
    gstin_or_cin: Optional[str] = None
    support_hours: Optional[str] = None
    social_links: Dict[str, str] = Field(default_factory=dict)
    social_profiles: List[Dict[str, Any]] = Field(default_factory=list)
    founders_or_team: List[str] = Field(default_factory=list)

# 2. Advertising Intelligence & Campaign Analysis
class AdPixelInfo(BaseModel):
    platform: str # Meta, Google, LinkedIn, TikTok, Pinterest, Twitter, Snapchat, Criteo
    pixel_id: Optional[str] = None
    script_snippet: Optional[str] = None
    detected_via: str = "Script Tag"

class AdvertisingPlatformInsight(BaseModel):
    platform_name: str
    has_active_pixel: bool = False
    pixel_ids: List[str] = Field(default_factory=list)
    campaign_status: str = "Unknown" # Active, Inactive, Untapped, Requires Account Access
    estimated_active_ads: int = 0
    transparency_search_url: Optional[str] = None
    active_ads_search_url: Optional[str] = None
    past_ads_search_url: Optional[str] = None
    all_ads_search_url: Optional[str] = None
    target_handle: Optional[str] = None
    handle_search_url: Optional[str] = None
    historical_ad_indicators: List[str] = Field(default_factory=list)
    ad_spend_profile: str = "Inactive" # Testing, Scaling, Inactive, Untapped
    key_findings: str = ""

class AdIntelligenceReport(BaseModel):
    overall_spend_profile: str = "Inactive"
    has_active_ads: bool = False
    past_advertiser_detected: bool = False
    past_campaign_evidence: List[str] = Field(default_factory=list)
    total_active_ads_detected: int = 0
    installed_pixels: List[AdPixelInfo] = Field(default_factory=list)
    platform_insights: List[AdvertisingPlatformInsight] = Field(default_factory=list)
    sample_creatives: List[Dict[str, Any]] = Field(default_factory=list)
    marketing_opportunity: str = ""
    # Provenance tags
    data_provenance: Dict[str, str] = Field(
        default_factory=lambda: {
            "pixels_installed": "Verified (Detected from DOM script tags)",
            "meta_campaigns": "Verified Public Library Query",
            "google_transparency": "Verified Public Advertiser Directory",
            "exact_spend_and_roas": "Requires Private Account Access (Unavailable publicly)"
        }
    )

# 3. SEO Audit & Search Engine Analysis
class ImageOptimizationIssue(BaseModel):
    src: str
    alt: Optional[str] = None
    is_missing_alt: bool = True
    is_oversized: bool = False

class SeoAuditReport(BaseModel):
    seo_score: int = 70
    title_tag: Optional[str] = None
    title_length: int = 0
    title_status: str = "OPTIMAL" # OPTIMAL, TOO_SHORT, TOO_LONG, MISSING
    meta_description: Optional[str] = None
    meta_desc_length: int = 0
    meta_desc_status: str = "OPTIMAL" # OPTIMAL, TOO_SHORT, TOO_LONG, MISSING
    h1_tags: List[str] = Field(default_factory=list)
    h2_tags: List[str] = Field(default_factory=list)
    h3_tags: List[str] = Field(default_factory=list)
    canonical_url: Optional[str] = None
    canonical_status: str = "VALID" # VALID, MISSING, MISMATCH, RELATIVE
    has_robots_txt: bool = True
    robots_txt_url: Optional[str] = None
    robots_txt_status: str = "ACCESSIBLE"
    has_sitemap: bool = True
    sitemap_url: Optional[str] = None
    sitemap_status: str = "ACCESSIBLE"
    meta_robots: Optional[str] = None
    is_indexable: bool = True
    schema_types_detected: List[str] = Field(default_factory=list)
    has_schema_markup: bool = False
    schema_details: List[Dict[str, Any]] = Field(default_factory=list)
    has_open_graph: bool = False
    og_preview: Dict[str, str] = Field(default_factory=dict)
    has_twitter_card: bool = False
    images_total: int = 0
    images_with_alt: int = 0
    images_missing_alt: int = 0
    sample_missing_alt_images: List[str] = Field(default_factory=list)
    broken_links: List[BrokenLinkInfo] = Field(default_factory=list)
    broken_links_count: int = 0
    mobile_viewport_configured: bool = True
    is_spa_indexing_risk: bool = False
    why_stuck_summary: str = ""
    ranking_blockers: List[str] = Field(default_factory=list)
    quick_seo_fixes: List[str] = Field(default_factory=list)

# 4. Website Security Audit
class SslCertificateInfo(BaseModel):
    is_valid: bool = True
    issuer: str = "Unknown"
    subject: str = "Unknown"
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    days_remaining: int = 0
    protocol_version: str = "TLSv1.2 / TLSv1.3"
    is_expired: bool = False
    is_https_enforced: bool = True

class SecurityHeaderDetail(BaseModel):
    header: str
    status: str # Present, Missing, Incomplete
    value: Optional[str] = None
    description: str
    recommended_value: str
    severity: str # CRITICAL, WARNING, OPPORTUNITY

class CookieSecurityInfo(BaseModel):
    name: str
    has_secure: bool = False
    has_httponly: bool = False
    samesite: Optional[str] = None
    is_compliant: bool = True

class ExposedFileFinding(BaseModel):
    path: str
    status_code: int
    is_exposed: bool
    risk_level: str # HIGH, MEDIUM, LOW
    description: str

class SecurityAuditReport(BaseModel):
    security_score: int = 80
    security_grade: str = "B" # A+, A, B, C, D, F
    ssl_info: SslCertificateInfo
    security_headers: List[SecurityHeaderDetail] = Field(default_factory=list)
    missing_headers_count: int = 0
    cookie_analysis: List[CookieSecurityInfo] = Field(default_factory=list)
    mixed_content_count: int = 0
    mixed_content_urls: List[str] = Field(default_factory=list)
    exposed_files: List[ExposedFileFinding] = Field(default_factory=list)
    has_exposed_sensitive_files: bool = False
    form_security_risks: List[str] = Field(default_factory=list)
    testing_methodology: str = "Safe, Non-Destructive Passive Auditing"

# 5. Website Design, Responsiveness, and Performance
class CoreWebVitalsEstimate(BaseModel):
    fcp_seconds: float = 1.2 # First Contentful Paint
    lcp_seconds: float = 2.4 # Largest Contentful Paint
    cls_score: float = 0.05 # Cumulative Layout Shift
    inp_rating: str = "Good" # Interaction to Next Paint

class AssetWeightBreakdown(BaseModel):
    total_kb: float = 0.0
    html_kb: float = 0.0
    scripts_count: int = 0
    scripts_kb: float = 0.0
    styles_count: int = 0
    styles_kb: float = 0.0
    images_count: int = 0
    images_kb: float = 0.0
    fonts_count: int = 0

class ResponsiveAuditInfo(BaseModel):
    has_viewport_meta: bool = True
    viewport_content: Optional[str] = None
    has_media_queries: bool = True
    uses_responsive_images: bool = False
    desktop_ready: bool = True
    tablet_ready: bool = True
    mobile_ready: bool = True
    layout_issues: List[str] = Field(default_factory=list)

class PerformanceAuditReport(BaseModel):
    performance_score: int = 75
    responsiveness_score: int = 85
    load_time_seconds: float = 0.0
    ttfb_seconds: float = 0.0 # Time to First Byte
    assets: AssetWeightBreakdown
    estimated_cwv: CoreWebVitalsEstimate
    responsive_audit: ResponsiveAuditInfo
    performance_bottlenecks: List[str] = Field(default_factory=list)
    recommended_optimizations: List[str] = Field(default_factory=list)

# 6. Website Content and Data Accuracy
class ContentTrustReport(BaseModel):
    trust_score: int = 75
    total_word_count: int = 0
    estimated_reading_time_mins: float = 0.0
    has_privacy_policy: bool = True
    privacy_policy_url: Optional[str] = None
    has_terms_of_service: bool = True
    terms_of_service_url: Optional[str] = None
    has_refund_policy: bool = False
    refund_policy_url: Optional[str] = None
    has_about_page: bool = True
    has_contact_page: bool = True
    has_faq_section: bool = False
    has_social_proof: bool = False
    contact_data_consistency: Dict[str, Any] = Field(default_factory=dict)
    missing_trust_signals: List[str] = Field(default_factory=list)
    evidence_backed_findings: List[str] = Field(default_factory=list)

# 7. Technology Stack Item
class TechStackItem(BaseModel):
    name: str
    category: str # CMS, E-commerce, Frontend Framework, Analytics, Pixels, CDN, Live Chat, Payment
    confidence: str = "High" # High, Medium, Low
    version: Optional[str] = None
    detected_via: str = "Signature"

class TechStackReport(BaseModel):
    platform: str = "Custom Coded"
    hosting: Optional[str] = None
    is_ecommerce: bool = False
    technologies: List[TechStackItem] = Field(default_factory=list)
    analytics_pixels: List[str] = Field(default_factory=list)
    apps_detected: List[str] = Field(default_factory=list)
    details: Dict[str, Any] = Field(default_factory=dict)

# 8. Historical Records
class HistoricalTimelineEvent(BaseModel):
    year: str
    date: str
    event_type: str
    description: str
    source_url: Optional[str] = None

class HistoricalReport(BaseModel):
    first_seen_date: Optional[str] = None
    last_archived_date: Optional[str] = None
    total_archive_snapshots: int = 0
    archive_calendar_url: Optional[str] = None
    domain_age_years: Optional[float] = None
    timeline: List[HistoricalTimelineEvent] = Field(default_factory=list)
    disclaimer: str = "Historical records reconstructed from public Wayback Machine archives and Certificate Transparency logs."

# 9. Audit Comparison (Continuous Monitoring & Historical Rescans)
class AuditComparisonReport(BaseModel):
    has_previous_audit: bool = False
    previous_audit_id: Optional[str] = None
    previous_audit_date: Optional[str] = None
    previous_health_score: Optional[int] = None
    score_change: int = 0
    resolved_flaws: List[str] = Field(default_factory=list)
    new_flaws: List[str] = Field(default_factory=list)
    persistent_flaws: List[str] = Field(default_factory=list)

# Catalog & Dropshipping models
class CatalogProduct(BaseModel):
    title: str
    price: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None

class CatalogSummary(BaseModel):
    total_products_detected: int = 0
    currency: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    sample_products: List[CatalogProduct] = Field(default_factory=list)
    vendors: List[str] = Field(default_factory=list)

class DropshipAnalysis(BaseModel):
    is_dropshipping: bool = False
    confidence_score: int = 0
    signals_found: List[str] = Field(default_factory=list)
    business_model: str = "Brand / Private Label"
    reasoning: str = ""

# Legacy / Conversion model for backwards compatibility
class ClientConversionAudit(BaseModel):
    conversion_score: int = 65
    primary_call_to_action: Optional[str] = None
    has_above_the_fold_cta: bool = False
    has_lead_capture_form: bool = False
    has_social_proof: bool = False
    has_instant_chat: bool = False
    has_clear_pricing_or_offer: bool = False
    friction_points_count: int = 0
    why_not_getting_clients: List[str] = Field(default_factory=list)
    cro_checklist: Dict[str, bool] = Field(default_factory=dict)
    client_recovery_strategy: List[str] = Field(default_factory=list)

class MetaAdsInsight(BaseModel):
    active_ads_count: int = 0
    has_active_ads: bool = False
    oldest_ad_days: Optional[int] = None
    ad_spend_profile: str = "Inactive"
    sample_ads: List[Dict[str, Any]] = Field(default_factory=list)
    marketing_opportunity: str = ""

# Comprehensive Master Audit Report
class AuditReport(BaseModel):
    audit_id: str
    url: str
    domain: str
    brand_name: str
    
    # 5 Pillar Health Scores
    health_score: int = 70
    seo_score: int = 70
    security_score: int = 80
    performance_score: int = 75
    conversion_score: int = 65

    country_of_operation: str = "Global / Unknown"
    executive_summary: str = ""
    
    # 9 Comprehensive Dimensions
    contacts: ContactDetails
    social_discovery: SocialDiscoveryReport
    ad_intelligence: AdIntelligenceReport
    seo_audit: SeoAuditReport
    security_audit: SecurityAuditReport
    performance_audit: PerformanceAuditReport
    content_trust: ContentTrustReport
    tech_stack: TechStackReport
    historical_records: HistoricalReport
    
    # E-Commerce & Business
    catalog: CatalogSummary
    dropship_analysis: DropshipAnalysis
    conversion_audit: Optional[ClientConversionAudit] = None
    meta_ads: MetaAdsInsight # Kept for backward compatibility
    
    # Detailed Flaws & Pages
    flaws: List[FlawItem] = Field(default_factory=list)
    crawled_pages: List[CrawledPageInfo] = Field(default_factory=list)
    
    # Continuous Monitoring / Comparison
    comparison: Optional[AuditComparisonReport] = None
    
    # AI Synthesis
    pitch_email_subject: str = ""
    pitch_email_body: str = ""
    timestamp: Optional[str] = None

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    audit_id: Optional[str] = None
    report_context: Optional[Dict[str, Any]] = None
    message: str
    history: List[ChatMessage] = Field(default_factory=list)
    gemini_api_key: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
