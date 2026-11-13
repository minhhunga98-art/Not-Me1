"""
Web Dashboard & Interactive BPMN Control Center for Hưng Phát Multi-Agent Workflow.
Built using standard Python http.server - zero external dependencies required.
Serves high-fidelity visionOS Spatial Glassmorphism UI.
"""

import http.server
import socketserver
import json
import urllib.parse
from pathlib import Path
from typing import Dict, Any

from src.workflow.orchestrator import HungPhatWorkflowOrchestrator

orchestrator_instance = HungPhatWorkflowOrchestrator()
TEMPLATE_DIR = Path("c:/Agent/src/web/templates")
STATIC_DIR = Path("c:/Agent/src/web/static")


class HungPhatWebHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            root_index = Path("c:/Agent/index.html")
            if root_index.exists():
                with open(root_index, "rb") as f:
                    self.wfile.write(f.read())
            else:
                index_path = TEMPLATE_DIR / "index.html"
                with open(index_path, "rb") as f:
                    self.wfile.write(f.read())
            return

        elif path == "/static/glass-tokens.css":
            css_path = STATIC_DIR / "glass-tokens.css"
            if css_path.exists():
                self.send_response(200)
                self.send_header("Content-Type", "text/css; charset=utf-8")
                self.end_headers()
                with open(css_path, "rb") as f:
                    self.wfile.write(f.read())
                return

        elif path == "/api/state":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            summary = self.get_serializable_state()
            self.wfile.write(json.dumps(summary, default=str, ensure_ascii=False).encode("utf-8"))
            return

        elif path.startswith("/reports/") or path.startswith("/artifacts/"):
            # Serve local file safely
            file_rel = path.lstrip("/")
            file_path = Path("c:/Agent") / file_rel
            if file_path.exists() and file_path.is_file():
                self.send_response(200)
                if file_path.suffix == ".md":
                    self.send_header("Content-Type", "text/markdown; charset=utf-8")
                elif file_path.suffix == ".json":
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                elif file_path.suffix == ".docx":
                    self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    self.send_header("Content-Disposition", f"attachment; filename=\"{file_path.name}\"")
                else:
                    self.send_header("Content-Type", "application/octet-stream")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
                return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        data = json.loads(body) if body else {}

        global orchestrator_instance

        if path == "/api/reset":
            orchestrator_instance = HungPhatWorkflowOrchestrator()
            self.respond_json({"status": "RESET_OK", "message": "Đã thiết lập lại workflow về trạng thái ban đầu."})
            return

        elif path == "/api/run_auto":
            state = orchestrator_instance.run_full_pipeline_automated()
            self.respond_json({"status": "COMPLETED", "state": self.get_serializable_state()})
            return

        elif path == "/api/run_step_forward":
            step_res = orchestrator_instance.step_forward()
            self.respond_json({
                "status": "STEP_OK",
                "next_step": step_res.get("next_step"),
                "message": step_res.get("message")
            })
            return

        elif path == "/api/run_step":
            step = data.get("step")
            if step == "Task_CleanData":
                orchestrator_instance.run_task_1_1_clean_data()
            elif step == "Task_FitAnalysis":
                orchestrator_instance.run_task_1_2_fit_analysis()
            elif step == "Gateway_HurdleRate":
                g1 = orchestrator_instance.evaluate_gateway_1_hurdle_rate()
                if g1 == "ROUTE_TO_COST_ANALYZER":
                    orchestrator_instance.run_task_1_3a_cost_analyzer()
            elif step == "Task_Scoring":
                orchestrator_instance.run_task_1_4_scoring()
            elif step == "Task_AuditSample":
                orchestrator_instance.prepare_task_2_1_audit_sample()
            elif step == "Task_ReviewShortlist":
                orchestrator_instance.run_task_3_1_manager_review()
            elif step == "Task_GenerateProposal":
                orchestrator_instance.run_task_1_5_generate_proposal()
            elif step == "Task_SubmitBOD":
                orchestrator_instance.run_task_3_2_submit_to_bod()

            self.respond_json({"status": "STEP_OK", "current_step": orchestrator_instance.state.get("current_step")})
            return

        elif path == "/api/ptkd_override":
            prov = data.get("province")
            crit = data.get("criterion_id")
            new_val = float(data.get("new_value", 85.0))
            reason = data.get("justification", "Hiệu chỉnh từ nhân viên PTKD")
            old_val = float(data.get("old_value", 75.0))

            mismatches = [{
                "province": prov,
                "criterion_id": crit,
                "old_val": old_val,
                "new_val": new_val,
                "reason": reason
            }]
            orchestrator_instance.complete_task_2_1_and_evaluate_gateway_2(mismatches=mismatches)
            self.respond_json({"status": "OVERRIDE_RECORDED_AND_RESCORED"})
            return

        elif path == "/api/ptkd_approve":
            orchestrator_instance.complete_task_2_1_and_evaluate_gateway_2(mismatches=None)
            orchestrator_instance.run_task_3_1_manager_review()
            self.respond_json({"status": "AUDIT_VERIFIED_TRANSITIONED_TO_MANAGER"})
            return

        elif path == "/api/manager_decide":
            approved = data.get("approved", True)
            selected = data.get("selected_provinces", [])
            reason = data.get("reason")
            weights = data.get("weights")
            orchestrator_instance.evaluate_gateway_3_shortlist(
                approved=approved,
                approved_provinces=selected if approved else None,
                rejection_reason=reason if not approved else None,
                weight_adjustments=weights if not approved else None
            )
            self.respond_json({"status": "MANAGER_DECISION_PROCESSED"})
            return

        self.send_response(404)
        self.end_headers()

    def respond_json(self, data: Dict[str, Any]):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str, ensure_ascii=False).encode("utf-8"))

    def get_serializable_state(self) -> Dict[str, Any]:
        global orchestrator_instance
        s = orchestrator_instance.state
        clean_recs = s.get("clean_dataset", [])
        score_recs = s.get("score_results", [])
        fit_recs = s.get("fit_feasibility_records", [])
        cost_recs = s.get("cost_to_serve_records", {})
        audit_samples = s.get("audit_samples", [])
        audit_logs = s.get("audit_logs", [])

        return {
            "current_step": s.get("current_step", "START"),
            "current_swimlane": s.get("current_swimlane", "LANE_1_AI_AGENT"),
            "selected_provinces": s.get("selected_provinces", []),
            "clean_dataset": [r.__dict__ for r in clean_recs] if clean_recs and hasattr(clean_recs[0], "__dict__") else clean_recs,
            "fit_records": [
                {
                    "province": r.province,
                    "feature_match_pct": r.feature_match_pct,
                    "readiness_score": r.readiness_score,
                    "distance_km": r.distance_km,
                    "meets_direct_sla": r.meets_direct_sla,
                    "hurdle_status": r.hurdle_status.value if hasattr(r.hurdle_status, "value") else str(r.hurdle_status),
                    "rationale": r.rationale
                } for r in fit_recs
            ] if fit_recs and hasattr(fit_recs[0], "province") else [],
            "cost_records": {
                k: (v.__dict__ if hasattr(v, "__dict__") else v)
                for k, v in cost_recs.items()
            },
            "score_results": [
                {
                    "rank": r.rank,
                    "province": r.province,
                    "final_score": r.final_score,
                    "raw_composite_score": r.raw_composite_score,
                    "is_score_capped": r.is_score_capped,
                    "score_cap": r.score_cap,
                    "cost_to_serve_flag": r.cost_to_serve_flag,
                    "notes": r.notes,
                    "criteria_scores": [c.__dict__ if hasattr(c, "__dict__") else c for c in r.criteria_scores]
                }
                for r in score_recs
            ] if score_recs and hasattr(score_recs[0], "province") else [],
            "audit_samples": [s.__dict__ if hasattr(s, "__dict__") else s for s in audit_samples],
            "audit_logs": audit_logs,
            "proposal_md_url": "/reports/" + Path(s.get("proposal_report_md", "")).name if s.get("proposal_report_md") else None,
            "proposal_docx_url": "/reports/" + Path(s.get("proposal_report_docx", "")).name if s.get("proposal_report_docx") else None,
            "history": s.get("history", [])
        }


def start_server(port: int = 8088):
    server_address = ("127.0.0.1", port)
    httpd = socketserver.TCPServer(server_address, HungPhatWebHandler)
    print(f"[*] Hưng Phát Multi-Agent BPMN Dashboard running at: http://127.0.0.1:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server stopped.")
        httpd.server_close()
