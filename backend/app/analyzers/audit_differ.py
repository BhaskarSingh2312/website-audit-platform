from typing import Dict, Any, Optional, List
from backend.app.models.schemas import AuditComparisonReport

class AuditDiffer:
    def compare(
        self,
        current_report: Dict[str, Any],
        previous_report: Optional[Dict[str, Any]]
    ) -> AuditComparisonReport:
        if not previous_report:
            return AuditComparisonReport(
                has_previous_audit=False,
                score_change=0,
                resolved_flaws=[],
                new_flaws=[],
                persistent_flaws=[]
            )

        prev_id = previous_report.get("audit_id") or previous_report.get("id")
        prev_date = previous_report.get("timestamp") or previous_report.get("created_at")
        prev_score = int(previous_report.get("health_score", 70))
        curr_score = int(current_report.get("health_score", 70))
        score_diff = curr_score - prev_score

        # Extract flaw titles
        prev_flaws = {f.get("title") for f in previous_report.get("flaws", []) if f.get("title")}
        curr_flaws = {f.get("title") for f in current_report.get("flaws", []) if f.get("title")}

        resolved = list(prev_flaws - curr_flaws)
        new_flaws = list(curr_flaws - prev_flaws)
        persistent = list(curr_flaws & prev_flaws)

        return AuditComparisonReport(
            has_previous_audit=True,
            previous_audit_id=prev_id,
            previous_audit_date=prev_date,
            previous_health_score=prev_score,
            score_change=score_diff,
            resolved_flaws=resolved,
            new_flaws=new_flaws,
            persistent_flaws=persistent
        )

