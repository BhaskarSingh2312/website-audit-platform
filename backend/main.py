import os
import sys
from pathlib import Path

# Add project root to sys.path so running backend directly, via uvicorn, or from subdirectories works seamlessly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse, Response

from backend.app.config import settings
from backend.app.orchestrator import AuditOrchestrator
from backend.app.ai.gemini_agent import GeminiAgent
from backend.app.models.schemas import AuditRequest, ChatRequest, ChatResponse
from backend.app.db.database import db
from backend.app.reports.report_exporter import exporter
from backend.app.analyzers.audit_differ import AuditDiffer

app = FastAPI(
    title="Advanced Website Intelligence & Digital Audit Platform",
    version="2.0.0",
    description="Full-spectrum website analysis, SEO audit, security testing, social media discovery, and advertising intelligence platform."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = AuditOrchestrator()
differ = AuditDiffer()
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "database_active": True,
        "version": "2.0.0"
    }

@app.get("/api/config")
async def get_config():
    return {
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "meta_token_configured": bool(settings.META_ACCESS_TOKEN)
    }

@app.post("/api/config")
async def update_config(data: dict):
    new_key = data.get("gemini_api_key", "").strip()
    if new_key:
        settings.GEMINI_API_KEY = new_key
        return {"status": "success", "message": "Gemini API Key updated."}
    return {"status": "ignored"}

@app.get("/api/audit/stream")
async def stream_audit(
    url: str = Query(..., description="Target website URL to audit"),
    api_key: str = Query(None, description="Optional custom Gemini API Key")
):
    key_to_use = api_key or settings.GEMINI_API_KEY
    return StreamingResponse(
        orchestrator.run_audit_stream(url, custom_api_key=key_to_use),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/api/history")
async def get_audit_history(limit: int = 50):
    """Returns past audits stored in SQLite database."""
    return db.list_audits(limit=limit)

@app.get("/api/history/{audit_id}")
async def get_history_detail(audit_id: str):
    """Loads a full audit report from SQLite database."""
    report = db.get_audit(audit_id)
    if not report:
        raise HTTPException(status_code=404, detail="Audit not found in database.")
    return report

@app.delete("/api/history/{audit_id}")
async def delete_history_item(audit_id: str):
    """Removes an audit from SQLite database."""
    success = db.delete_audit(audit_id)
    if not success:
        raise HTTPException(status_code=404, detail="Audit not found.")
    return {"status": "deleted", "audit_id": audit_id}

@app.get("/api/audit/{audit_id}")
async def get_audit_report(audit_id: str):
    report = db.get_audit(audit_id)
    if not report:
        raise HTTPException(status_code=404, detail="Audit report not found.")
    return report

@app.get("/api/audit/{audit_id}/export/excel")
async def export_audit_excel(audit_id: str):
    """Generates and downloads a multi-sheet .xlsx Excel report."""
    report = db.get_audit(audit_id)
    if not report:
        raise HTTPException(status_code=404, detail="Audit report not found.")
    
    excel_stream = exporter.generate_excel_report(report)
    domain = report.get("domain", "website").replace(".", "_")
    filename = f"{domain}_digital_intelligence_audit.xlsx"
    
    return Response(
        content=excel_stream.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

@app.get("/api/audit/{audit_id}/compare/{previous_id}")
async def compare_audits(audit_id: str, previous_id: str):
    """Returns comparison diff between two audits of a website."""
    curr = db.get_audit(audit_id)
    prev = db.get_audit(previous_id)
    if not curr or not prev:
        raise HTTPException(status_code=404, detail="One or both audits not found.")
    return differ.compare(curr, prev)

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_audit(request: ChatRequest):
    context = request.report_context
    if not context and request.audit_id:
        context = db.get_audit(request.audit_id)
    if not context:
        context = {}

    key_to_use = request.gemini_api_key or settings.GEMINI_API_KEY
    gemini_agent = GeminiAgent(api_key=key_to_use)
    reply_text = await gemini_agent.chat(
        user_message=request.message,
        report_context=context,
        history=request.history
    )
    return ChatResponse(reply=reply_text)

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    @app.get("/index.html")
    async def serve_index():
        return FileResponse(FRONTEND_DIR / "index.html")

    @app.get("/favicon.ico")
    async def favicon():
        return Response(status_code=204)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG, app_dir=str(PROJECT_ROOT))
