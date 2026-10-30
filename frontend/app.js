// State Management
let currentReport = null;
let currentEventSource = null;
let chatHistory = [];
let currentFilterSeverity = 'ALL';
let currentFilterCategory = 'ALL';

// DOM Elements
const auditForm = document.getElementById('audit-form');
const targetUrlInput = document.getElementById('target-url');
const btnSubmitAudit = document.getElementById('btn-submit-audit');
const btnText = document.getElementById('btn-text');
const btnSpinner = document.getElementById('btn-spinner');

// Pipeline Stepper Elements
const pipelineSection = document.getElementById('pipeline-section');
const pipelineCurrentStep = document.getElementById('pipeline-current-step');
const pipelineDetails = document.getElementById('pipeline-details');
const pipelinePercent = document.getElementById('pipeline-percent');
const progressBarFill = document.getElementById('progress-bar-fill');

const stepNodes = {
  connect: document.getElementById('node-connect'),
  crawl: document.getElementById('node-crawl'),
  social: document.getElementById('node-social'),
  ads: document.getElementById('node-ads'),
  seo: document.getElementById('node-seo'),
  security: document.getElementById('node-security'),
  ai: document.getElementById('node-ai'),
};

// Dashboard Elements
const dashboardGrid = document.getElementById('dashboard-grid');
const reportBrandName = document.getElementById('report-brand-name');
const reportUrl = document.getElementById('report-url');
const reportHealthScore = document.getElementById('report-health-score');
const scoreCircle = document.getElementById('score-circle');
const badgePlatform = document.getElementById('badge-platform');
const badgeModel = document.getElementById('badge-model');
const badgePagesCrawled = document.getElementById('badge-pages-crawled');

// 5 Pillar Scores
const scoreValHealth = document.getElementById('score-val-health');
const scoreValSeo = document.getElementById('score-val-seo');
const scoreValSecurity = document.getElementById('score-val-security');
const scoreValPerf = document.getElementById('score-val-perf');
const scoreValCro = document.getElementById('score-val-cro');
const securityGradeBadge = document.getElementById('security-grade-badge');

// Comparison Banner
const comparisonBanner = document.getElementById('comparison-banner');
const compTitle = document.getElementById('comp-title');
const compText = document.getElementById('comp-text');
const compDelta = document.getElementById('comp-delta');

// Quick Stats
const reportCountry = document.getElementById('report-country');
const statSocialCount = document.getElementById('stat-social-count');
const statPixelsCount = document.getElementById('stat-pixels-count');
const statEmailsCount = document.getElementById('stat-emails-count');
const statIssuesCount = document.getElementById('stat-issues-count');
const reportExecutiveSummary = document.getElementById('report-executive-summary');

// Tab Badges
const tabSocialBadge = document.getElementById('tab-social-badge');
const tabAdsBadge = document.getElementById('tab-ads-badge');
const tabFlawsBadge = document.getElementById('tab-flaws-badge');

// Tab 1: Outreach Pitch
const pitchSubject = document.getElementById('pitch-subject');
const pitchBody = document.getElementById('pitch-body');
const btnCopyPitch = document.getElementById('btn-copy-pitch');

// Tab 2: Social & Contacts
const socialProfilesContainer = document.getElementById('social-profiles-container');
const socialSummaryText = document.getElementById('social-summary-text');
const missingPlatformsBox = document.getElementById('missing-platforms-box');
const missingPlatformsList = document.getElementById('missing-platforms-list');
const allContactEmails = document.getElementById('all-contact-emails');
const allContactPhones = document.getElementById('all-contact-phones');
const allContactWhatsapp = document.getElementById('all-contact-whatsapp');
const allContactAddresses = document.getElementById('all-contact-addresses');
const valLegalName = document.getElementById('val-legal-name');
const valGstin = document.getElementById('val-gstin');

// Tab 3: Advertising
const badgeAdSpend = document.getElementById('badge-ad-spend');
const badgePastAdvertiser = document.getElementById('badge-past-advertiser');
const adOpportunityText = document.getElementById('ad-opportunity-text');
const histStatusTitle = document.getElementById('hist-status-title');
const histStatusDesc = document.getElementById('hist-status-desc');
const histStatusBadge = document.getElementById('hist-status-badge');
const historicalEvidenceContainer = document.getElementById('historical-evidence-container');
const installedPixelsTbody = document.getElementById('installed-pixels-tbody');
const adPlatformsContainer = document.getElementById('ad-platforms-container');

// Tab 4: Technical SEO
const seoScoreBadge = document.getElementById('seo-score-badge');
const seoTitleVal = document.getElementById('seo-title-val');
const seoTitleStatus = document.getElementById('seo-title-status');
const seoDescVal = document.getElementById('seo-desc-val');
const seoDescStatus = document.getElementById('seo-desc-status');
const seoCanonicalVal = document.getElementById('seo-canonical-val');
const seoCanonicalStatus = document.getElementById('seo-canonical-status');
const seoCrawlVal = document.getElementById('seo-crawl-val');
const seoHeadingsContainer = document.getElementById('seo-headings-container');
const seoSchemasContainer = document.getElementById('seo-schemas-container');
const brokenLinksTbody = document.getElementById('broken-links-tbody');
const brokenLinksCounter = document.getElementById('broken-links-counter');

// Tab 5: Security Audit
const secAuditGrade = document.getElementById('sec-audit-grade');
const sslStatusBadge = document.getElementById('ssl-status-badge');
const sslProto = document.getElementById('ssl-proto');
const sslIssuer = document.getElementById('ssl-issuer');
const sslSubject = document.getElementById('ssl-subject');
const sslDays = document.getElementById('ssl-days');
const sslEnforced = document.getElementById('ssl-enforced');
const securityHeadersTbody = document.getElementById('security-headers-tbody');
const securityProbesContainer = document.getElementById('security-probes-container');

// Tab 6: Performance & Device Switcher
const perfScoreBadge = document.getElementById('perf-score-badge');
const cwvFcp = document.getElementById('cwv-fcp');
const cwvLcp = document.getElementById('cwv-lcp');
const cwvLoad = document.getElementById('cwv-load');
const cwvTtfb = document.getElementById('cwv-ttfb');
const assetsBreakdownRow = document.getElementById('assets-breakdown-row');
const deviceFrameContainer = document.getElementById('device-frame-container');
const devicePreviewIframe = document.getElementById('device-preview-iframe');

// Tab 7: Content & Trust
const contentTrustScoreBadge = document.getElementById('content-trust-score-badge');
const statusPrivacy = document.getElementById('status-privacy');
const statusTerms = document.getElementById('status-terms');
const statusRefund = document.getElementById('status-refund');
const statusContact = document.getElementById('status-contact');
const statusProof = document.getElementById('status-proof');
const contentWordCount = document.getElementById('content-word-count');
const contentReadTime = document.getElementById('content-read-time');

// Tab 8: Tech Stack
const techStackTbody = document.getElementById('tech-stack-tbody');

// Tab 9: History & Archives
const histFirstSeen = document.getElementById('hist-first-seen');
const histDomainAge = document.getElementById('hist-domain-age');
const histTotalSnapshots = document.getElementById('hist-total-snapshots');
const historyTimelineContainer = document.getElementById('history-timeline-container');
const btnViewWaybackCalendar = document.getElementById('btn-view-wayback-calendar');

// Tab 10: Flaws
const flawsContainer = document.getElementById('flaws-container');
const flawTotalTag = document.getElementById('flaw-total-tag');

// Action Buttons
const btnPrintPdf = document.getElementById('btn-print-pdf');
const btnExportExcel = document.getElementById('btn-export-excel');
const btnDownloadJson = document.getElementById('btn-download-json');

// Chat Elements
const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatBrandContext = document.getElementById('chat-brand-context');

// History & Settings Modals
const historyModal = document.getElementById('history-modal');
const btnOpenHistory = document.getElementById('btn-open-history');
const btnCloseHistory = document.getElementById('btn-close-history');
const historyItemsContainer = document.getElementById('history-items-container');
const historyCounter = document.getElementById('history-counter');

const settingsModal = document.getElementById('settings-modal');
const btnOpenSettings = document.getElementById('btn-open-settings');
const btnCloseSettings = document.getElementById('btn-close-settings');
const btnCancelSettings = document.getElementById('btn-cancel-settings');
const btnSaveSettings = document.getElementById('btn-save-settings');
const inputGeminiKey = document.getElementById('input-gemini-key');
const inputMetaToken = document.getElementById('input-meta-token');

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  setupTabs();
  setupSamplePills();
  setupChatHandlers();
  setupModals();
  setupDeviceSwitcher();
  setupFlawFilters();
  setupExportButtons();
  refreshHistoryCounter();
  loadStoredSettings();
});

// Tab Routing
function setupTabs() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      tabButtons.forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      
      btn.classList.add('active');
      const targetId = btn.getAttribute('data-tab');
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add('active');
    });
  });
}

// Device Switcher for Responsive Simulation
function setupDeviceSwitcher() {
  const deviceButtons = document.querySelectorAll('.device-btn');
  deviceButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      deviceButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      
      const device = btn.getAttribute('data-device');
      deviceFrameContainer.className = `device-frame-container ${device}`;
    });
  });
}

// Flaw Filters
function setupFlawFilters() {
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilterSeverity = btn.getAttribute('data-severity');
      renderFlaws();
    });
  });

  document.querySelectorAll('.cat-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilterCategory = btn.getAttribute('data-category');
      renderFlaws();
    });
  });
}

// Sample Targets
function setupSamplePills() {
  document.querySelectorAll('.pill-btn').forEach(pill => {
    pill.addEventListener('click', () => {
      targetUrlInput.value = pill.getAttribute('data-url');
      triggerAudit();
    });
  });
}

// Audit Form Submit
auditForm.addEventListener('submit', (e) => {
  e.preventDefault();
  triggerAudit();
});

function triggerAudit() {
  const rawUrl = targetUrlInput.value.trim();
  if (!rawUrl) return;

  btnText.textContent = "Auditing...";
  btnSpinner.classList.remove('hidden');
  btnSubmitAudit.disabled = true;

  resetPipeline();
  pipelineSection.classList.remove('hidden');
  dashboardGrid.classList.add('hidden');

  if (currentEventSource) {
    currentEventSource.close();
  }

  const storedKey = localStorage.getItem('gemini_api_key') || '';
  let streamUrl = `/api/audit/stream?url=${encodeURIComponent(rawUrl)}`;
  if (storedKey) {
    streamUrl += `&api_key=${encodeURIComponent(storedKey)}`;
  }

  currentEventSource = new EventSource(streamUrl);

  currentEventSource.addEventListener('step', (event) => {
    const data = JSON.parse(event.data);
    updatePipelineStep(data.step, data.progress, data.title, data.details);
  });

  currentEventSource.addEventListener('complete', (event) => {
    const data = JSON.parse(event.data);
    currentReport = data.report;
    currentEventSource.close();
    currentEventSource = null;

    finishPipelineSuccess();
    renderDashboard(currentReport);
    refreshHistoryCounter();
  });

  currentEventSource.addEventListener('error', (event) => {
    let msg = "Network error or audit timed out.";
    try {
      if (event.data) {
        const parsed = JSON.parse(event.data);
        msg = parsed.message || msg;
      }
    } catch (e) {}
    alert(`Audit Error: ${msg}`);
    resetPipeline();
    if (currentEventSource) {
      currentEventSource.close();
      currentEventSource = null;
    }
  });
}

function updatePipelineStep(stepKey, progress, title, details) {
  pipelineCurrentStep.textContent = title;
  pipelineDetails.textContent = details;
  pipelinePercent.textContent = `${progress}%`;
  progressBarFill.style.width = `${progress}%`;

  if (stepNodes[stepKey]) {
    Object.values(stepNodes).forEach(node => {
      if (node) node.classList.remove('active');
    });
    stepNodes[stepKey].classList.add('active');
  }
}

function resetPipeline() {
  btnText.textContent = "Audit Website";
  btnSpinner.classList.add('hidden');
  btnSubmitAudit.disabled = false;
  pipelinePercent.textContent = "0%";
  progressBarFill.style.width = "0%";
  Object.values(stepNodes).forEach(node => {
    if (node) node.classList.remove('active');
  });
}

function finishPipelineSuccess() {
  resetPipeline();
  pipelineSection.classList.add('hidden');
  dashboardGrid.classList.remove('hidden');
}

// Render Master Dashboard
function renderDashboard(report) {
  if (!report) return;

  // Header & Brand
  reportBrandName.textContent = report.brand_name || report.domain;
  reportUrl.textContent = `${report.url} ↗`;
  reportUrl.href = report.url;
  badgePlatform.textContent = report.tech_stack?.platform || "Custom Platform";
  badgeModel.textContent = report.dropship_analysis?.business_model || "Brand";
  badgePagesCrawled.textContent = `${(report.crawled_pages || []).length} Pages Crawled`;

  // Pillar Scores
  const health = report.health_score || 75;
  reportHealthScore.textContent = health;
  scoreValHealth.textContent = `${health}/100`;
  scoreValSeo.textContent = `${report.seo_score || 70}/100`;
  
  const secGrade = report.security_audit?.security_grade || "B";
  scoreValSecurity.textContent = `${report.security_score || 80}/100 (${secGrade})`;
  if (securityGradeBadge) securityGradeBadge.textContent = secGrade;
  if (secAuditGrade) secAuditGrade.textContent = `Grade ${secGrade}`;

  scoreValPerf.textContent = `${report.performance_score || 75}/100`;
  scoreValCro.textContent = `${report.conversion_score || 65}/100`;

  // Comparison Banner
  if (report.comparison && report.comparison.has_previous_audit) {
    comparisonBanner.classList.remove('hidden');
    const diff = report.comparison.score_change;
    const sign = diff >= 0 ? `+${diff}` : `${diff}`;
    compDelta.textContent = `${sign} pts`;
    compDelta.style.color = diff >= 0 ? "var(--emerald)" : "var(--rose)";
    compTitle.textContent = `Compared with Previous Scan (${report.comparison.previous_audit_date || 'Earlier'})`;
    compText.textContent = `${report.comparison.resolved_flaws.length} issues resolved, ${report.comparison.new_flaws.length} new issues flagged.`;
  } else {
    comparisonBanner.classList.add('hidden');
  }

  // Quick Stats
  reportCountry.textContent = report.country_of_operation || "Global";
  const socialCount = report.social_discovery?.profiles?.length || 0;
  statSocialCount.textContent = `${socialCount} Discovered`;
  tabSocialBadge.textContent = socialCount;

  const pixelCount = report.ad_intelligence?.installed_pixels?.length || 0;
  statPixelsCount.textContent = `${pixelCount} Active`;
  tabAdsBadge.textContent = pixelCount;

  statEmailsCount.textContent = `${(report.contacts?.emails || []).length} Found`;
  statIssuesCount.textContent = `${(report.flaws || []).length} Issues`;
  tabFlawsBadge.textContent = (report.flaws || []).length;
  flawTotalTag.textContent = `${(report.flaws || []).length} Issues Found`;

  // Tab 1: Executive Summary & Outreach Pitch
  reportExecutiveSummary.textContent = report.executive_summary || "Audit complete.";
  pitchSubject.value = report.pitch_email_subject || `Website observation regarding ${report.brand_name}`;
  pitchBody.value = report.pitch_email_body || "Hi team,\n\nI reviewed your site...";

  // Tab 2: Social Media & Contacts
  renderSocialAndContacts(report);

  // Tab 3: Advertising Intelligence
  renderAdIntelligence(report);

  // Tab 4: Technical SEO
  renderTechnicalSeo(report);

  // Tab 5: Website Security Audit
  renderSecurityAudit(report);

  // Tab 6: Performance & Device Switcher
  renderPerformance(report);

  // Tab 7: Content & Trust
  renderContentTrust(report);

  // Tab 8: Tech Stack
  renderTechStack(report);

  // Tab 9: History & Archives
  renderHistory(report);

  // Tab 10: All Flaws
  renderFlaws();

  // Update Chat Context
  chatBrandContext.textContent = report.brand_name;
  chatHistory = [];
  chatMessages.innerHTML = `
    <div class="chat-msg msg-ai">
      <div class="msg-bubble">
        I've loaded the full 360° audit for <strong>${report.brand_name}</strong> (${report.domain}). You can ask me to draft tailored cold emails, explain technical fixes, or summarize security and SEO bottlenecks!
      </div>
    </div>
  `;
}

// -------------------------------------------------------------
// RENDER HELPERS
// -------------------------------------------------------------

function renderSocialAndContacts(report) {
  const soc = report.social_discovery || {};
  socialSummaryText.textContent = soc.summary || "Identified social links across website navigation and metadata.";

  // Social Cards
  socialProfilesContainer.innerHTML = '';
  if (soc.profiles && soc.profiles.length > 0) {
    soc.profiles.forEach(p => {
      const card = document.createElement('div');
      card.className = 'social-card';
      card.innerHTML = `
        <div class="social-card-left">
          <div class="social-icon-box">🔗</div>
          <div class="social-card-details">
            <h5>${escapeHtml(p.platform)}</h5>
            <span>${escapeHtml(p.handle || p.platform)} • ${p.found_in.join(', ')}</span>
          </div>
        </div>
        <a href="${escapeHtml(p.url)}" target="_blank" class="btn btn-secondary btn-sm">Visit ↗</a>
      `;
      socialProfilesContainer.appendChild(card);
    });
  } else {
    socialProfilesContainer.innerHTML = '<p class="tab-hint">No official social media profiles detected.</p>';
  }

  // Missing essential platforms
  if (soc.missing_platforms && soc.missing_platforms.length > 0) {
    missingPlatformsBox.classList.remove('hidden');
    missingPlatformsList.textContent = soc.missing_platforms.join(', ');
  } else {
    missingPlatformsBox.classList.add('hidden');
  }

  // Contacts
  const c = report.contacts || {};
  renderChips(allContactEmails, c.emails, 'mailto:');
  renderChips(allContactPhones, c.phone_numbers, 'tel:');
  renderChips(allContactWhatsapp, c.whatsapp_numbers, 'https://wa.me/');

  allContactAddresses.innerHTML = '';
  if (c.addresses && c.addresses.length > 0) {
    c.addresses.forEach(a => {
      const p = document.createElement('p');
      p.className = 'address-item';
      p.textContent = a;
      allContactAddresses.appendChild(p);
    });
  } else {
    allContactAddresses.innerHTML = '<span class="text-dim">No physical address detected</span>';
  }

  valLegalName.textContent = c.registered_business_name || 'N/A';
  valGstin.textContent = c.gstin_or_cin || 'N/A';
}

function renderAdIntelligence(report) {
  const ad = report.ad_intelligence || {};
  badgeAdSpend.textContent = ad.overall_spend_profile || "Active Advertiser";
  adOpportunityText.textContent = ad.marketing_opportunity || "Auditing active advertising footprints.";

  // Past / Historical Advertiser Badge
  if (badgePastAdvertiser) {
    if (ad.past_advertiser_detected) {
      badgePastAdvertiser.textContent = "📜 Past / Configured Advertiser Detected";
      badgePastAdvertiser.className = "badge badge-past-ad detected";
    } else {
      badgePastAdvertiser.textContent = "⚪ No Historical Ad Pixels";
      badgePastAdvertiser.className = "badge badge-past-ad none";
    }
  }

  // Historical Advertising Card Details
  if (histStatusBadge) {
    if (ad.past_advertiser_detected) {
      histStatusBadge.textContent = "Conversion Tracking Detected";
      histStatusBadge.className = "hist-status-badge detected";
      if (histStatusDesc) {
        histStatusDesc.textContent = "Active or historical advertising tags detected in website code. Direct transparency library queries available below.";
      }
    } else {
      histStatusBadge.textContent = "No Conversion Pixels Detected";
      histStatusBadge.className = "hist-status-badge none";
      if (histStatusDesc) {
        histStatusDesc.textContent = "No Meta Pixel, Google Ads tags, or marketing pixels found. Brand does not currently have active conversion tracking funnels.";
      }
    }
  }

  // Historical Evidence List
  if (historicalEvidenceContainer) {
    historicalEvidenceContainer.innerHTML = '';
    const evidenceItems = ad.past_campaign_evidence && ad.past_campaign_evidence.length > 0
      ? ad.past_campaign_evidence
      : ["No conversion tags or campaign parameters observed on page source."];
    
    evidenceItems.forEach(ev => {
      const item = document.createElement('div');
      item.className = 'hist-evidence-item';
      const icon = ad.past_advertiser_detected ? '✅' : 'ℹ️';
      item.innerHTML = `<span class="ev-icon">${icon}</span><span>${escapeHtml(ev)}</span>`;
      historicalEvidenceContainer.appendChild(item);
    });
  }

  // Pixels table
  installedPixelsTbody.innerHTML = '';
  if (ad.installed_pixels && ad.installed_pixels.length > 0) {
    ad.installed_pixels.forEach(px => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong>${escapeHtml(px.platform)}</strong></td>
        <td><code>${escapeHtml(px.pixel_id || 'Active')}</code></td>
        <td><span class="seo-status-pill success">${escapeHtml(px.detected_via)}</span></td>
      `;
      installedPixelsTbody.appendChild(tr);
    });
  } else {
    installedPixelsTbody.innerHTML = '<tr><td colspan="3" class="text-dim">No advertising pixels detected on page source.</td></tr>';
  }

  // Ad Platforms Grid
  adPlatformsContainer.innerHTML = '';
  if (ad.platform_insights && ad.platform_insights.length > 0) {
    ad.platform_insights.forEach(pi => {
      const card = document.createElement('div');
      card.className = 'ad-platform-card';
      const statusBadge = pi.has_active_pixel
        ? '<span class="seo-status-pill success">Pixel Installed</span>'
        : '<span class="seo-status-pill warning">No Pixel</span>';
      
      // Build distinct action buttons
      let buttonsHtml = '';
      if (pi.active_ads_search_url) {
        buttonsHtml += `<a href="${escapeHtml(pi.active_ads_search_url)}" target="_blank" class="ad-btn ad-btn-active">🟢 Active Ads (Live) ↗</a>`;
      }
      if (pi.past_ads_search_url && pi.past_ads_search_url !== pi.active_ads_search_url) {
        buttonsHtml += `<a href="${escapeHtml(pi.past_ads_search_url)}" target="_blank" class="ad-btn ad-btn-past">📜 Past Ads (Ended) ↗</a>`;
      }
      if (pi.all_ads_search_url && pi.all_ads_search_url !== pi.active_ads_search_url && pi.all_ads_search_url !== pi.past_ads_search_url) {
        buttonsHtml += `<a href="${escapeHtml(pi.all_ads_search_url)}" target="_blank" class="ad-btn ad-btn-all">🌐 All Archived Ads ↗</a>`;
      } else if (!buttonsHtml && pi.transparency_search_url) {
        buttonsHtml += `<a href="${escapeHtml(pi.transparency_search_url)}" target="_blank" class="ad-btn ad-btn-all">Search Library ↗</a>`;
      }
      if (pi.handle_search_url && pi.target_handle) {
        buttonsHtml += `<a href="${escapeHtml(pi.handle_search_url)}" target="_blank" class="ad-btn ad-btn-handle">🏷️ Search @${escapeHtml(pi.target_handle)} ↗</a>`;
      }

      card.innerHTML = `
        <div>
          <div class="ad-platform-header">
            <h5>${escapeHtml(pi.platform_name)}</h5>
            ${statusBadge}
          </div>
          <p>${escapeHtml(pi.key_findings)}</p>
        </div>
        <div class="ad-actions-row">
          ${buttonsHtml}
        </div>
      `;
      adPlatformsContainer.appendChild(card);
    });
  }
}

function renderTechnicalSeo(report) {
  const seo = report.seo_audit || {};
  if (seoScoreBadge) seoScoreBadge.textContent = `Score: ${seo.seo_score || 70}/100`;

  seoTitleVal.textContent = seo.title_tag || "Missing <title> Tag";
  seoTitleStatus.textContent = seo.title_status || "Optimal";
  seoTitleStatus.className = `seo-status-pill ${getStatusClass(seo.title_status)}`;

  seoDescVal.textContent = seo.meta_description || "Missing Meta Description";
  seoDescStatus.textContent = seo.meta_desc_status || "Optimal";
  seoDescStatus.className = `seo-status-pill ${getStatusClass(seo.meta_desc_status)}`;

  seoCanonicalVal.textContent = seo.canonical_url || "Missing Canonical";
  seoCanonicalStatus.textContent = seo.canonical_status || "Valid";
  seoCanonicalStatus.className = `seo-status-pill ${getStatusClass(seo.canonical_status)}`;

  seoCrawlVal.textContent = `robots.txt: ${seo.robots_txt_status || 'OK'} | sitemap.xml: ${seo.sitemap_status || 'OK'}`;

  // Headings
  seoHeadingsContainer.innerHTML = '';
  if (seo.h1_tags && seo.h1_tags.length > 0) {
    seo.h1_tags.forEach(h => {
      const item = document.createElement('div');
      item.className = 'heading-item';
      item.innerHTML = `<span class="heading-tag-pill">H1</span> <span>${escapeHtml(h)}</span>`;
      seoHeadingsContainer.appendChild(item);
    });
  } else {
    seoHeadingsContainer.innerHTML = '<span class="text-dim">Zero &lt;h1&gt; tags detected.</span>';
  }

  // Schemas
  seoSchemasContainer.innerHTML = '';
  if (seo.schema_types_detected && seo.schema_types_detected.length > 0) {
    seo.schema_types_detected.forEach(st => {
      const span = document.createElement('span');
      span.className = 'schema-tag';
      span.textContent = st;
      seoSchemasContainer.appendChild(span);
    });
  } else {
    seoSchemasContainer.innerHTML = '<span class="text-dim">No Schema.org structured data detected.</span>';
  }

  // Broken Links
  brokenLinksTbody.innerHTML = '';
  brokenLinksCounter.textContent = seo.broken_links_count || 0;
  if (seo.broken_links && seo.broken_links.length > 0) {
    seo.broken_links.forEach(bl => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><a href="${escapeHtml(bl.url)}" target="_blank" class="brand-link">${escapeHtml(bl.url)}</a></td>
        <td><span class="seo-status-pill danger">${bl.status_code}</span></td>
        <td>${escapeHtml(bl.source_page || 'Homepage')}</td>
        <td>${bl.is_external ? 'External' : 'Internal'}</td>
      `;
      brokenLinksTbody.appendChild(tr);
    });
  } else {
    brokenLinksTbody.innerHTML = '<tr><td colspan="4" class="text-dim">No broken 404/500 links detected in sampled navigation.</td></tr>';
  }
}

function renderSecurityAudit(report) {
  const sec = report.security_audit || {};
  const ssl = sec.ssl_info || {};

  sslStatusBadge.textContent = ssl.is_valid ? '🔒 SSL Certificate Valid' : '⚠️ Insecure / Expired SSL';
  sslStatusBadge.className = `ssl-badge ${ssl.is_valid ? 'valid' : 'invalid'}`;
  sslProto.textContent = ssl.protocol_version || 'TLSv1.3';
  sslIssuer.textContent = ssl.issuer || 'Unknown CA';
  sslSubject.textContent = ssl.subject || report.domain;
  sslDays.textContent = `${ssl.days_remaining || 0} days remaining`;
  sslEnforced.textContent = ssl.is_https_enforced ? 'Yes (HTTPS Enforced)' : 'No (Insecure HTTP permitted)';

  // Headers table
  securityHeadersTbody.innerHTML = '';
  if (sec.security_headers && sec.security_headers.length > 0) {
    sec.security_headers.forEach(sh => {
      const tr = document.createElement('tr');
      const isPresent = sh.status === 'Present';
      tr.innerHTML = `
        <td><strong>${escapeHtml(sh.header)}</strong></td>
        <td><span class="seo-status-pill ${isPresent ? 'success' : 'danger'}">${sh.status}</span></td>
        <td><small class="text-dim">${escapeHtml(sh.value || sh.recommended_value)}</small></td>
      `;
      securityHeadersTbody.appendChild(tr);
    });
  }

  // Exposed Probes
  securityProbesContainer.innerHTML = '';
  if (sec.exposed_files && sec.exposed_files.length > 0) {
    sec.exposed_files.forEach(p => {
      const div = document.createElement('div');
      div.className = 'ad-platform-card';
      const isRisk = p.is_exposed && p.path !== '/robots.txt';
      div.innerHTML = `
        <div class="ad-platform-header">
          <h5><code>${escapeHtml(p.path)}</code></h5>
          <span class="seo-status-pill ${isRisk ? 'danger' : 'success'}">${isRisk ? 'EXPOSED' : 'Protected (404)'}</span>
        </div>
        <p>${escapeHtml(p.description)}</p>
      `;
      securityProbesContainer.appendChild(div);
    });
  }
}

function renderPerformance(report) {
  const perf = report.performance_audit || {};
  if (perfScoreBadge) perfScoreBadge.textContent = `Performance: ${perf.performance_score || 75}/100`;

  cwvFcp.textContent = `${perf.estimated_cwv?.fcp_seconds || 1.2}s`;
  cwvLcp.textContent = `${perf.estimated_cwv?.lcp_seconds || 2.4}s`;
  cwvLoad.textContent = `${perf.load_time_seconds || 1.8}s`;
  cwvTtfb.textContent = `${perf.ttfb_seconds || 0.25}s`;

  // Asset breakdown
  const ast = perf.assets || {};
  assetsBreakdownRow.innerHTML = `
    <div class="meta-stat"><span class="stat-label">Total Size</span><span class="stat-val">${ast.total_kb || 0} KB</span></div>
    <div class="meta-stat"><span class="stat-label">HTML</span><span class="stat-val">${ast.html_kb || 0} KB</span></div>
    <div class="meta-stat"><span class="stat-label">Scripts (${ast.scripts_count || 0})</span><span class="stat-val">${ast.scripts_kb || 0} KB</span></div>
    <div class="meta-stat"><span class="stat-label">Styles (${ast.styles_count || 0})</span><span class="stat-val">${ast.styles_kb || 0} KB</span></div>
    <div class="meta-stat"><span class="stat-label">Images (${ast.images_count || 0})</span><span class="stat-val">${ast.images_kb || 0} KB</span></div>
  `;

  // Update simulator iframe url
  if (devicePreviewIframe && report.url) {
    devicePreviewIframe.src = report.url;
  }
}

function renderContentTrust(report) {
  const ct = report.content_trust || {};
  if (contentTrustScoreBadge) contentTrustScoreBadge.textContent = `Trust Score: ${ct.trust_score || 85}/100`;

  updateTrustStatus(statusPrivacy, ct.has_privacy_policy);
  updateTrustStatus(statusTerms, ct.has_terms_of_service);
  updateTrustStatus(statusRefund, ct.has_refund_policy);
  updateTrustStatus(statusContact, ct.has_contact_page);
  updateTrustStatus(statusProof, ct.has_social_proof);

  contentWordCount.textContent = ct.total_word_count || 0;
  contentReadTime.textContent = `${ct.estimated_reading_time_mins || 0} min`;
}

function updateTrustStatus(element, condition) {
  if (!element) return;
  element.textContent = condition ? 'Verified' : 'Missing';
  element.className = `trust-status ${condition ? 'verified' : 'missing'}`;
}

function renderTechStack(report) {
  const tech = report.tech_stack || {};
  techStackTbody.innerHTML = '';

  if (tech.technologies && tech.technologies.length > 0) {
    tech.technologies.forEach(t => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong>${escapeHtml(t.name)}</strong></td>
        <td>${escapeHtml(t.category)}</td>
        <td><span class="seo-status-pill success">${t.confidence}</span></td>
        <td><code>${escapeHtml(t.version || t.detected_via)}</code></td>
      `;
      techStackTbody.appendChild(tr);
    });
  } else {
    techStackTbody.innerHTML = '<tr><td colspan="4" class="text-dim">No third-party libraries identified.</td></tr>';
  }
}

function renderHistory(report) {
  const hist = report.historical_records || {};
  histFirstSeen.textContent = hist.first_seen_date || "Archived";
  histDomainAge.textContent = hist.domain_age_years ? `~${hist.domain_age_years} Years` : "Established";
  histTotalSnapshots.textContent = `${hist.total_archive_snapshots || 12}+ Snapshots`;

  if (btnViewWaybackCalendar && hist.archive_calendar_url) {
    btnViewWaybackCalendar.href = hist.archive_calendar_url;
  }

  historyTimelineContainer.innerHTML = '';
  if (hist.timeline && hist.timeline.length > 0) {
    hist.timeline.forEach(item => {
      const div = document.createElement('div');
      div.className = 'timeline-item';
      div.innerHTML = `
        <span class="timeline-date">${escapeHtml(item.date)}</span>
        <div class="timeline-title">${escapeHtml(item.event_type)}</div>
        <p class="timeline-desc">${escapeHtml(item.description)}</p>
      `;
      historyTimelineContainer.appendChild(div);
    });
  }
}

function renderFlaws() {
  if (!currentReport) return;
  const allFlaws = currentReport.flaws || [];
  
  const filtered = allFlaws.filter(f => {
    const matchSev = currentFilterSeverity === 'ALL' || f.severity === currentFilterSeverity;
    const matchCat = currentFilterCategory === 'ALL' || f.category.toLowerCase() === currentFilterCategory.toLowerCase();
    return matchSev && matchCat;
  });

  flawsContainer.innerHTML = '';
  if (filtered.length === 0) {
    flawsContainer.innerHTML = '<p class="tab-hint" style="padding: 1.5rem 0;">No issues found matching the selected filter criteria.</p>';
    return;
  }

  filtered.forEach(f => {
    const card = document.createElement('div');
    card.className = `flaw-card ${f.severity.toLowerCase()}`;
    card.innerHTML = `
      <div class="flaw-header">
        <span class="flaw-severity ${f.severity.toLowerCase()}">${f.severity}</span>
        <span class="flaw-category">${escapeHtml(f.category)}</span>
        <span class="flaw-confidence">🟢 ${escapeHtml(f.confidence || 'Verified')}</span>
      </div>
      <h4 class="flaw-title">${escapeHtml(f.title)}</h4>
      <p class="flaw-description">${escapeHtml(f.description)}</p>
      <div class="flaw-impact-box">
        <strong>Impact:</strong> ${escapeHtml(f.client_impact || 'Degrades user experience.')}
      </div>
      <div class="flaw-fix-box">
        <strong>Recommended Fix:</strong> ${escapeHtml(f.recommended_fix || 'Remediate according to web standards.')}
      </div>
    `;
    flawsContainer.appendChild(card);
  });
}

function renderChips(container, items, linkPrefix) {
  if (!container) return;
  container.innerHTML = '';
  if (items && items.length > 0) {
    items.forEach(it => {
      const a = document.createElement('a');
      a.className = 'contact-chip';
      a.href = `${linkPrefix}${it}`;
      a.textContent = it;
      if (linkPrefix.startsWith('http')) a.target = '_blank';
      container.appendChild(a);
    });
  } else {
    container.innerHTML = '<span class="text-dim">None detected</span>';
  }
}

function getStatusClass(status) {
  if (!status) return 'success';
  const s = status.toUpperCase();
  if (s === 'OPTIMAL' || s === 'VALID' || s === 'ACCESSIBLE') return 'success';
  if (s === 'TOO_SHORT' || s === 'TOO_LONG' || s === 'RELATIVE') return 'warning';
  return 'danger';
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// -------------------------------------------------------------
// EXPORTS & CHAT & MODALS
// -------------------------------------------------------------

function setupExportButtons() {
  if (btnPrintPdf) {
    btnPrintPdf.addEventListener('click', () => {
      window.print();
    });
  }

  if (btnExportExcel) {
    btnExportExcel.addEventListener('click', () => {
      if (!currentReport || !currentReport.audit_id) return;
      window.location.href = `/api/audit/${currentReport.audit_id}/export/excel`;
    });
  }

  if (btnDownloadJson) {
    btnDownloadJson.addEventListener('click', () => {
      if (!currentReport) return;
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(currentReport, null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute("href", dataStr);
      downloadAnchor.setAttribute("download", `${currentReport.domain}_digital_audit.json`);
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
    });
  }

  if (btnCopyPitch) {
    btnCopyPitch.addEventListener('click', () => {
      const fullText = `Subject: ${pitchSubject.value}\n\n${pitchBody.value}`;
      navigator.clipboard.writeText(fullText).then(() => {
        btnCopyPitch.textContent = "Copied! ✓";
        setTimeout(() => btnCopyPitch.textContent = "📋 Copy Email", 2000);
      });
    });
  }
}

function setupChatHandlers() {
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query || !currentReport) return;

    chatInput.value = '';
    appendChatMessage('user', query);

    const typingMsg = appendChatMessage('ai', 'Thinking...');
    
    try {
      const storedKey = localStorage.getItem('gemini_api_key') || '';
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          audit_id: currentReport.audit_id,
          report_context: currentReport,
          message: query,
          history: chatHistory,
          gemini_api_key: storedKey
        })
      });
      const data = await res.json();
      typingMsg.querySelector('.msg-bubble').innerHTML = formatMarkdown(data.reply);
      chatHistory.push({ role: 'user', content: query });
      chatHistory.push({ role: 'model', content: data.reply });
    } catch (err) {
      typingMsg.querySelector('.msg-bubble').textContent = "Failed to communicate with AI Copilot.";
    }
  });

  document.querySelectorAll('.chip').forEach(ch => {
    ch.addEventListener('click', () => {
      chatInput.value = ch.getAttribute('data-prompt');
      chatForm.dispatchEvent(new Event('submit'));
    });
  });
}

function appendChatMessage(role, text) {
  const msg = document.createElement('div');
  msg.className = `chat-msg msg-${role}`;
  msg.innerHTML = `<div class="msg-bubble">${escapeHtml(text)}</div>`;
  chatMessages.appendChild(msg);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return msg;
}

function formatMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/^### (.*$)/gim, '<h5 style="color:#ffffff; margin: 0.5rem 0 0.2rem;">$1</h5>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code style="background:rgba(255,255,255,0.1); padding:0.1rem 0.3rem; border-radius:3px;">$1</code>')
    .replace(/\n/g, '<br>');
}

function setupModals() {
  btnOpenHistory.addEventListener('click', openHistoryModal);
  btnCloseHistory.addEventListener('click', () => historyModal.classList.add('hidden'));

  btnOpenSettings.addEventListener('click', () => settingsModal.classList.remove('hidden'));
  btnCloseSettings.addEventListener('click', () => settingsModal.classList.add('hidden'));
  btnCancelSettings.addEventListener('click', () => settingsModal.classList.add('hidden'));

  btnSaveSettings.addEventListener('click', async () => {
    const key = inputGeminiKey.value.trim();
    if (key) {
      localStorage.setItem('gemini_api_key', key);
      await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ gemini_api_key: key })
      });
    }
    settingsModal.classList.add('hidden');
    alert("Credentials saved.");
  });
}

async function openHistoryModal() {
  historyModal.classList.remove('hidden');
  historyItemsContainer.innerHTML = '<p class="tab-hint">Loading history...</p>';
  try {
    const res = await fetch('/api/history');
    const items = await res.json();
    historyItemsContainer.innerHTML = '';
    if (items.length === 0) {
      historyItemsContainer.innerHTML = '<p class="tab-hint">No past audits in database yet.</p>';
      return;
    }
    items.forEach(it => {
      const div = document.createElement('div');
      div.className = 'history-item';
      div.innerHTML = `
        <div class="history-item-info">
          <h4>${escapeHtml(it.brand_name || it.domain)}</h4>
          <p>${escapeHtml(it.url)} • ${it.created_at ? it.created_at.split('T')[0] : ''}</p>
        </div>
        <div class="history-item-actions">
          <span class="seo-status-pill success">${it.health_score}/100</span>
          <button class="btn btn-secondary btn-sm btn-load-hist" data-id="${it.id}">Load Report</button>
        </div>
      `;
      div.querySelector('.btn-load-hist').addEventListener('click', async (e) => {
        e.stopPropagation();
        const repRes = await fetch(`/api/history/${it.id}`);
        const fullRep = await repRes.json();
        currentReport = fullRep;
        historyModal.classList.add('hidden');
        dashboardGrid.classList.remove('hidden');
        renderDashboard(fullRep);
      });
      historyItemsContainer.appendChild(div);
    });
  } catch (e) {
    historyItemsContainer.innerHTML = '<p class="tab-hint">Failed to load history.</p>';
  }
}

async function refreshHistoryCounter() {
  try {
    const res = await fetch('/api/history?limit=100');
    const items = await res.json();
    if (historyCounter) historyCounter.textContent = items.length;
  } catch (e) {}
}

function loadStoredSettings() {
  const k = localStorage.getItem('gemini_api_key');
  if (k && inputGeminiKey) inputGeminiKey.value = k;
}
