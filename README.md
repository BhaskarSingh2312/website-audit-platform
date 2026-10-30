# 🌐 Advanced Website Analysis & Digital Intelligence Platform

An enterprise-grade, automated website intelligence, SEO audit, security analysis, social media discovery, and advertising intelligence platform. Enter any website URL to systematically crawl, analyze, and present deep insights across **11 core digital pillars**.

---

## 🌟 Core Intelligence Dimensions

### 1. Social Media Discovery & Analysis
* **Omnichannel Profile Identification**: Discovers links to Instagram, Facebook, LinkedIn, X (Twitter), YouTube, Pinterest, TikTok, GitHub, Reddit, Threads, Medium, Discord, and Telegram.
* **Contextual Discovery Mapping**: Identifies discovery locations: Header Navigation, Footer Section, Meta Tags (`twitter:site`, `twitter:creator`, `og:see_also`), and JSON-LD schema (`sameAs`).
* **Health & Integration Alerts**: Identifies missing essential platforms, unlinked channels, and flags broken/placeholder links (e.g. `facebook.com/#`).

### 2. Multi-Platform Advertising Intelligence
* **Tracking Pixel Detection**: Inspects DOM for Meta Pixel, Google Ads Tag (`AW-XXXXX`), Google Tag Manager (`GTM-XXXXX`), LinkedIn Insight Tag, TikTok Pixel, Pinterest Tag, Twitter Pixel, and Snapchat Pixel.
* **Public Ad Library Lookups**: Direct links to Meta Ad Library, Google Ads Transparency Center, and LinkedIn Ad Library.
* **Transparent Data Provenance**: Explicitly differentiates between Verified Public Data (installed pixels, library entries), Estimated Data (activity profile), and Private Data (ad spend, ROAS).

### 3. Technical SEO & Search Engine Audit
* **On-Page & Hierarchy**: Title tags, meta descriptions, canonical status, H1–H3 heading hierarchy.
* **Crawlability & Directives**: Validates `robots.txt`, `sitemap.xml`, and meta robots directives (`noindex`, `nofollow`).
* **Rich Schema Validation**: JSON-LD and microdata parser validating Organization, WebSite, LocalBusiness, Product, Article, and BreadcrumbList schemas.
* **Image & Link Optimization**: Audits missing `alt` attributes, image formats, and flags broken links (HTTP 404/500).

### 4. Passive Website Security Audit
* **SSL/TLS Certificate Inspection**: Real socket inspection extracting certificate issuer, validity period, days until expiration, and TLS protocol version.
* **Security Headers Compliance**: Scores and grades (A+ to F) HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, and Permissions-Policy.
* **Cookie & Form Security**: Checks `Secure`, `HttpOnly`, and `SameSite` cookie attributes, mixed content warnings, and detects password fields over HTTP.
* **Safe Non-Destructive Probes**: Checks for publicly exposed `.env`, `.git/HEAD`, or unminified source maps.

### 5. Website Design, Responsiveness & Performance
* **Core Web Vitals Estimates**: Measures TTFB, page load latency, FCP, and LCP.
* **Interactive Responsive Screen Simulator**: Embedded frame simulator to preview desktop (1440px), tablet (768px), and mobile (375px) viewports.
* **Asset Payload Breakdown**: Analyzes HTML, scripts, stylesheets, and image counts and sizes.

### 6. Website Content Completeness & Trust Signals
* **Legal Compliance Checklist**: Verifies presence of Privacy Policy, Terms of Service, Refund Policy, About Us, and Contact Us pages.
* **Business Information Consistency**: Cross-references contact info, phone numbers, and addresses across pages; flags free email providers.
* **Content Metrics**: Analyzes total word count, reading time, and social proof/testimonials.

### 7. Technology Stack Directory
* **Categorized Detection**: Identifies CMS, E-Commerce, Frontend Frameworks (React, Next.js, Vue, Tailwind), Web Servers, CDNs, Live Chat widgets, and Payment Gateways.
* **Confidence Indicators**: Displays confidence levels (High / Medium / Low) and version numbers where exposed.

### 8. Historical Records & Web Archives
* **Wayback Machine Integration**: Queries Internet Archive APIs to retrieve earliest recorded snapshot, total archive count, and domain age.
* **Milestone Timeline**: Reconstructs a historical timeline with direct links to the archive calendar.

### 9. Comprehensive Dashboard & Export Engine
* **Five Pillar Health Scores**: Overall Health (0-100), SEO Score, Security Score + Grade, Performance Score, Conversion Score.
* **Multi-Sheet Excel Export (.xlsx)**: Generates structured workbooks with Executive Overview, SEO Flaws, Security Findings, Discovered Contacts, Advertising Intel, and Tech Stack via `openpyxl`.
* **Print-Optimized Branded PDF Export**: Clean, multi-page print layout.
* **Severity & Category Filters**: Filter flaws by severity (`Critical`, `Warning`, `Opportunity`) or category.

### 10. Automated Scanning & Continuous Monitoring
* **Historical Rescans & Comparison Engine**: Compares current audit against previous scans of the same domain in SQLite to track resolved and new issues over time.
* **Real-time SSE Stream**: Real-time progress updates across all audit stages.

---

## 🚀 Quick Start Guide

### 1. Requirements
* Python 3.10+
* Pip

### 2. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 3. Configure Environment
Copy `.env.example` to `.env`:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
PORT=8000
HOST=127.0.0.1
DEBUG=True
```

### 4. Run Application
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser at:
```
http://127.0.0.1:8000
```

---

## 📁 Project Architecture

```
Scrapper/
├── backend/
│   ├── app/
│   │   ├── config.py              # Configuration & env loader
│   │   ├── core/
│   │   │   └── security.py        # SSRF prevention & prompt sanitization
│   │   ├── models/
│   │   │   └── schemas.py         # Complete Pydantic schemas across 11 pillars
│   │   ├── scrapers/
│   │   │   ├── fast_crawler.py    # Async multi-page crawler, asset & probe auditor
│   │   │   └── contact_extractor.py # Email, phone & social DOM extractor
│   │   ├── analyzers/
│   │   │   ├── social_analyzer.py # Social media discovery & consistency analyzer
│   │   │   ├── ad_intelligence.py # Ad pixels & multi-channel ad transparency
│   │   │   ├── seo_analyzer.py    # Technical SEO, canonicals, schema & broken links
│   │   │   ├── security_analyzer.py # SSL socket inspector & security headers grader
│   │   │   ├── performance_analyzer.py # CWV estimator, TTFB & asset breakdown
│   │   │   ├── content_analyzer.py # Content trust, legal pages & consistency
│   │   │   ├── history_analyzer.py # Wayback Machine archive timeline
│   │   │   ├── tech_detector.py   # Stack & framework recognition with confidence
│   │   │   ├── flaw_detector.py   # Multi-category flaw prioritization
│   │   │   └── audit_differ.py    # Rescan comparison & issue resolution tracker
│   │   ├── reports/
│   │   │   └── report_exporter.py # Multi-sheet Excel (.xlsx) generator (openpyxl)
│   │   ├── ai/
│   │   │   └── gemini_agent.py    # Google Gemini synthesis & conversational copilot
│   │   ├── db/
│   │   │   └── database.py        # SQLite database for audit persistence & rescans
│   │   └── orchestrator.py        # 11-stage pipeline orchestrator with SSE streaming
│   └── main.py                    # FastAPI entry point & API endpoints
├── frontend/
│   ├── index.html                 # 10-tab digital intelligence dashboard & device simulator
│   ├── style.css                  # Glassmorphism styling, scorecards & print styles
│   └── app.js                     # Reactive SSE client, device switcher, filters & exporter
├── requirements.txt
└── README.md
```
