import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

DB_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
DB_PATH = DB_DIR / "scrapper.db"

def init_db():
    """Initializes the SQLite database and creates the audits table if not exists."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audits (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                domain TEXT NOT NULL,
                brand_name TEXT NOT NULL,
                health_score INTEGER NOT NULL,
                seo_score INTEGER DEFAULT 70,
                security_score INTEGER DEFAULT 80,
                performance_score INTEGER DEFAULT 75,
                platform TEXT,
                is_dropshipping BOOLEAN,
                total_pages_crawled INTEGER DEFAULT 1,
                total_products INTEGER DEFAULT 0,
                total_emails INTEGER DEFAULT 0,
                total_phones INTEGER DEFAULT 0,
                active_ads_count INTEGER DEFAULT 0,
                report_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_domain ON audits(domain)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON audits(created_at DESC)")
        
        # Add new score columns if table existed previously without them
        try:
            cursor.execute("ALTER TABLE audits ADD COLUMN seo_score INTEGER DEFAULT 70")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE audits ADD COLUMN security_score INTEGER DEFAULT 80")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("ALTER TABLE audits ADD COLUMN performance_score INTEGER DEFAULT 75")
        except sqlite3.OperationalError:
            pass

        conn.commit()

class AuditDatabase:
    def __init__(self):
        init_db()

    def save_audit(self, report: Dict[str, Any]) -> str:
        """Saves or updates an audit report in the SQLite database."""
        audit_id = report.get("audit_id") or report.get("id")
        url = report.get("url", "")
        domain = report.get("domain", "")
        brand_name = report.get("brand_name", "")
        health_score = int(report.get("health_score", 70))
        seo_score = int(report.get("seo_score", 70))
        security_score = int(report.get("security_score", 80))
        performance_score = int(report.get("performance_score", 75))
        platform = report.get("tech_stack", {}).get("platform", "Unknown")
        is_dropshipping = bool(report.get("dropship_analysis", {}).get("is_dropshipping", False))
        
        pages_crawled = len(report.get("crawled_pages", []))
        total_products = int(report.get("catalog", {}).get("total_products_detected", 0))
        total_emails = len(report.get("contacts", {}).get("emails", []))
        total_phones = len(report.get("contacts", {}).get("phone_numbers", []))
        active_ads = int(report.get("ad_intelligence", {}).get("total_active_ads_detected", 0))

        report_json = json.dumps(report)
        now_iso = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO audits (
                    id, url, domain, brand_name, health_score, seo_score, security_score, performance_score,
                    platform, is_dropshipping, total_pages_crawled, total_products,
                    total_emails, total_phones, active_ads_count, report_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                audit_id, url, domain, brand_name, health_score, seo_score, security_score, performance_score,
                platform, is_dropshipping, pages_crawled, total_products,
                total_emails, total_phones, active_ads, report_json, now_iso
            ))
            conn.commit()
        return audit_id

    def get_latest_audit_by_domain(self, domain: str, exclude_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieves the most recent audit report for a given domain, excluding exclude_id if given."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            if exclude_id:
                cursor.execute("""
                    SELECT report_json FROM audits
                    WHERE domain = ? AND id != ?
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (domain, exclude_id))
            else:
                cursor.execute("""
                    SELECT report_json FROM audits
                    WHERE domain = ?
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (domain,))
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row[0])
                except Exception:
                    pass
        return None

    def get_audit(self, audit_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single full audit report by ID."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT report_json FROM audits WHERE id = ?", (audit_id,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
        return None

    def list_audits(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns summarized history of past audits ordered by newest first."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, url, domain, brand_name, health_score, seo_score, security_score, performance_score,
                       platform, is_dropshipping, total_pages_crawled, total_products,
                       total_emails, total_phones, active_ads_count, created_at
                FROM audits
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            
            history = []
            for r in rows:
                history.append({
                    "id": r[0],
                    "url": r[1],
                    "domain": r[2],
                    "brand_name": r[3],
                    "health_score": r[4],
                    "seo_score": r[5] if len(r) > 5 and r[5] is not None else 70,
                    "security_score": r[6] if len(r) > 6 and r[6] is not None else 80,
                    "performance_score": r[7] if len(r) > 7 and r[7] is not None else 75,
                    "platform": r[8] if len(r) > 8 else "Unknown",
                    "is_dropshipping": bool(r[9]) if len(r) > 9 else False,
                    "total_pages_crawled": r[10] if len(r) > 10 else 1,
                    "total_products": r[11] if len(r) > 11 else 0,
                    "total_emails": r[12] if len(r) > 12 else 0,
                    "total_phones": r[13] if len(r) > 13 else 0,
                    "active_ads_count": r[14] if len(r) > 14 else 0,
                    "created_at": r[15] if len(r) > 15 else ""
                })
            return history

    def delete_audit(self, audit_id: str) -> bool:
        """Deletes an audit from the database."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM audits WHERE id = ?", (audit_id,))
            conn.commit()
            return cursor.rowcount > 0

db = AuditDatabase()
