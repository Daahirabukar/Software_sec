"""Report Service: formats only the notes sent by API after Notes authorization."""

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from secure_notes_helper import format_report
from services.common import InvalidAuthority, report_scope, required_secret, verify_authority


class ReportInput(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    notes: list[dict[str, str]] = Field(max_length=50)


def create_app(service_secret: bytes | None = None) -> FastAPI:
    secret = service_secret or required_secret("API_REPORTS_SECRET")
    app = FastAPI(title="Secure Notes Mini Report Service")

    @app.post("/reports")
    def create_report(data: ReportInput, authorization: str | None = Header(default=None)):
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Service authorization required")
        try:
            grant = verify_authority(authorization[7:], secret, audience="reports",
                                    action="report:create", resource=report_scope(data.notes))
        except InvalidAuthority:
            raise HTTPException(status_code=403, detail="Service authorization denied") from None
        if data.username != grant["username"]:
            raise HTTPException(status_code=403, detail="Service authorization denied")
        return {"report": format_report(data.username, data.notes), "subject": grant["sub"]}

    return app
