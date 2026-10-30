# 01. Project Overview: AI-Powered Website Scraper & Lead Audit Agent

## 1. Executive Summary

The **AI-Powered Website Scraper & Lead Audit Agent** is an automated intelligence and sales enablement tool designed for digital agencies, web development studios, SEO specialists, and marketing consultants.

The system accepts any target website URL, systematically inspects its frontend, infrastructure, business model, and advertising footprint, detects critical flaws, and synthesizes the findings into a **client-ready Website Audit & Pitch Report**. Furthermore, an integrated **conversational AI agent** allows users to query site findings, brainstorm strategies, and generate customized cold outreach emails and proposals.

---

## 2. Core Business Problem & Purpose

Agencies spend hours manually auditing prospective client websites before sending cold pitches or jumping on discovery calls:
- Manually inspecting source code to identify Shopify, WordPress, or custom tech stacks.
- Searching for contact details across footer links, privacy policies, and social media pages.
- Guessing whether a store is a low-effort dropshipping site or a private-label brand.
- Checking Meta Ad Library manually to see if the brand is actively investing in paid traffic.
- Identifying technical flaws (slow images, broken SEO tags, missing OpenGraph, bad mobile layouts).

**The Solution:** This agent automates this entire manual audit process in **under 30 seconds**, producing high-converting sales angles to sell website redesigns, conversion rate optimization (CRO), speed optimization, SEO, and paid media management.

---

## 3. Comprehensive Feature Specifications

### 3.1 Step 1: Website Scraping & Data Extraction
* **Deep Crawl & DOM Parsing:**
  * Extracts `<head>` metadata, OpenGraph tags, Twitter Cards, favicons, canonical URLs, and schema markup (JSON-LD).
  * Traverses internal links to extract critical trust pages: `/about`, `/contact`, `/policies`, `/terms-of-service`, `/privacy-policy`, `/shipping-policy`.
* **Instant Product & Catalog Intelligence:**
  * For Shopify websites: Automatically queries `/products.json` and `/collections.json` to extract total product counts, price ranges, top-selling tags, vendor names, and variant setups without heavy crawling.
  * For non-Shopify sites: Parses XML sitemaps (`/sitemap.xml`, `/sitemap_products.xml`) and schema.org `Product` / `Service` markup.
* **Geographical & Operational Detection:**
  * Detects primary operating country using TLD extensions (`.in`, `.co.uk`, `.com.au`, `.us`), currency symbols (`₹`, `$`, `£`, `€`), footer physical addresses, and shipping policy clauses.

---

### 3.2 Step 2: Business & Contact Footprint Discovery
* **Domain & Brand Identity:**
  * Domain name, registrar info, SSL certificate issuer, and DNS configuration.
  * Brand name, registered entity name, and branding consistency.
* **Omnichannel Contact Extraction:**
  * **Email Extraction:** Regex and DOM scrapers targeting `mailto:` links, footer text, contact page forms, and privacy policy sections.
  * **Phone Numbers:** Detection of international and local phone formats across headers, banners, and footers.
  * **Social Media Footprint:** Automated extraction and verification of links for:
    * Instagram
    * Facebook (Pages and Groups)
    * LinkedIn (Company profile)
    * Twitter / X
    * YouTube
    * TikTok & Pinterest

---

### 3.3 Step 3: Dropshipping vs. Private Label Brand Identification
A proprietary hybrid heuristic + Gemini LLM classification model determines whether an e-commerce website is a dropshipping store or an established brand:
* **Dropshipping Signals Checked:**
  * **Shipping Policy Clauses:** Mentions of 7–15+ business days delivery times, ePacket, international warehouses, or AliExpress shipping terminology.
  * **Review Apps & Patterns:** Usage of unverified photo review apps (Loox, Judge.me, AliReviews) populated with stock/AliExpress customer pictures.
  * **Catalog Diversity:** Presence of unrelated viral trending gadgets (e.g., posture corrector + dog collar + LED lamp).
  * **Image Provenance:** High usage of generic factory/supplier mockup photos without branded lifestyle imagery.
  * **App Footprint:** Presence of dropshipping fulfillment integrations (DSers, Oberlo, Spocket, CJ Dropshipping, Zendrop).
* **Brand Signals Checked:**
  * Custom branded packaging photos, authentic company founding stories, trademark notices, local warehouse addresses, and proprietary warranty claims.

---

### 3.4 Step 4: Technical, SEO & CRO Flaw Detection
The engine conducts an automated audit across 4 primary technical vectors to surface high-value agency pitch angles:
1. **SEO & Discoverability Flaws:**
   * Missing, duplicated, or truncated `<title>` and `<meta description>` tags.
   * Broken heading hierarchy (missing `<h1>`, multiple `<h1>` tags, skipped levels).
   * Missing `alt` attributes on key product and hero images.
   * Missing or misconfigured OpenGraph preview tags (poor link preview on WhatsApp/iMessage).
2. **Speed & Performance Leaks:**
   * Oversized uncompressed images causing slow First Contentful Paint (FCP).
   * Render-blocking third-party scripts and bloated tracking apps.
3. **Conversion Rate Optimization (CRO) & UX Flaws:**
   * Missing sticky navigation or missing sticky "Add to Cart" on mobile viewports.
   * Lack of clear value proposition and social proof above the fold.
   * Missing return policy or guarantee badges near checkout triggers.
4. **Trust & Compliance Flaws:**
   * Broken SSL / mixed content warnings.
   * Missing standard legal compliance pages (Privacy Policy, Terms of Service, Refund Policy).

---

### 3.5 Step 5: Meta Ad Library Intelligence
* **Active Ad Volume Detection:**
  * Queries the Meta Ad Library using brand name, domain, and Facebook Page ID.
  * Measures whether the brand is running **0 ads, 1–5 ads (testing), or 20+ ads (scaling)**.
* **Ad Longevity & Creative Analysis:**
  * Calculates ad duration (how long specific ads have been active). Ads running for 30–90+ days are flagged as **winning creatives**.
  * Identifies creative types: Static image ads, UGC (User-Generated Content) videos, carousels, or catalog ads.
* **Agency Sales Pitch Formulation:**
  * **Case A (0 Active Ads):** Pitch paid social customer acquisition services; highlight lost market share to competitors.
  * **Case B (Heavy Ad Spend + Flawed Website):** Pitch website redesign & CRO services; demonstrate that poor site speed and friction are burning their paid ad budget.

---

### 3.6 Step 6: Automated 10-Section Client Audit Report
The system compiles all raw findings into an executive-grade structured report:
1. **Website Overview & Executive Health Score** (Calculated 0–100 score).
2. **Hosting Platform & Complete Tech Stack Breakdown.**
3. **Business & Brand Classification** (Dropshipping vs. Private Brand confidence score).
4. **Products, Services & Catalog Architecture.**
5. **Verified Contact Details & Social Media Links.**
6. **Technical & SEO Flaws Audit** (Severity-ranked: Critical, Warning, Minor).
7. **Performance & Mobile UX Bottlenecks.**
8. **Meta Ad Library Footprint & Longevity Analysis.**
9. **Strategic Recommended Action Plan** (Prioritized quick-wins vs. long-term fixes).
10. **Ready-to-Send Client Outreach Email & Custom Proposal Pitch.**

---

### 3.7 Step 7: Interactive AI Chatbot Agent
* Embedded in the dashboard to act as your **AI Research Assistant**.
* Has full in-memory context of the analyzed target website.
* Capability to execute dynamic user prompts:
  * *"Draft a 3-paragraph cold LinkedIn DM to the founder mentioning their missing Meta pixel and slow mobile checkout."*
  * *"What are the top 3 weaknesses in their product page structure?"*
  * *"Write a proposal for a $2,500 Shopify redesign project based on these audit findings."*
