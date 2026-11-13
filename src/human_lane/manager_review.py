"""
Lane 3: Trưởng phòng PTKD (Decision Making & Governance)
- Task 3.1: Rà soát Bảng xếp hạng 4 địa bàn & Duyệt ngoại lệ
- Gateway 3: Chốt được 2 địa bàn ưu tiên?
- Task 3.2: Phê duyệt Hồ sơ & Trình Ban Giám đốc
"""

import json
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.models import ProvinceScoreResult, AuditLogEntry
from src.paths import get_artifacts_dir


class ManagerReviewModule:
    def __init__(self, manager_name: str = "Nguyễn Văn Hùng - Trưởng phòng PTKD"):
        self.manager_name = manager_name

    def review_shortlist(
        self,
        score_results: List[ProvinceScoreResult]
    ) -> Dict[str, Any]:
        """
        Task 3.1: Generates summary review dashboard for the BD Manager.
        Highlights exceptions, cost-to-serve flags, and recommended top 2.
        """
        top_2 = score_results[:2]
        others = score_results[2:]

        summary = {
            "top_candidates": [
                {
                    "rank": r.rank,
                    "province": r.province,
                    "score": r.final_score,
                    "cost_to_serve_flag": r.cost_to_serve_flag,
                    "notes": r.notes
                }
                for r in top_2
            ],
            "runners_up": [
                {
                    "rank": r.rank,
                    "province": r.province,
                    "score": r.final_score,
                    "cost_to_serve_flag": r.cost_to_serve_flag,
                    "notes": r.notes
                }
                for r in others
            ],
            "has_cost_to_serve_exception": any(r.cost_to_serve_flag for r in top_2)
        }
        return summary

    def decide_shortlist(
        self,
        approved_provinces: List[str],
        state: Dict[str, Any],
        rejection_reason: Optional[str] = None,
        weight_adjustments: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Gateway 3 decision logic.
        If approved: confirms top 2 and advances to Task 1.5.
        If rejected / requires adjustment: routes back to Task 2.2 with audit entry.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if rejection_reason or weight_adjustments:
            # Manager requests adjustment
            log_entry = AuditLogEntry(
                log_id=f"LOG-{int(datetime.datetime.now().timestamp())}",
                timestamp=timestamp,
                actor=self.manager_name,
                action="MANAGER_REQUEST_RECALIBRATION",
                target_province="ALL",
                field_affected="criteria_weights",
                previous_value=state.get("criteria_weights", {}),
                new_value=weight_adjustments or {},
                justification=rejection_reason or "Trưởng phòng yêu cầu tái cân bằng trọng số đánh giá."
            )
            if "audit_logs" not in state:
                state["audit_logs"] = []
            state["audit_logs"].append(log_entry.__dict__)

            if weight_adjustments:
                if "parameter_overrides" not in state:
                    state["parameter_overrides"] = {"score_overrides": {}, "weights": {}}
                state["parameter_overrides"]["weights"] = weight_adjustments

            return {
                "decision": "REJECTED_NEEDS_ADJUSTMENT",
                "reason": rejection_reason,
                "route_to": "Task_ManualAdjust (2.2)"
            }

        # Shortlist confirmed
        log_entry = AuditLogEntry(
            log_id=f"LOG-{int(datetime.datetime.now().timestamp())}",
            timestamp=timestamp,
            actor=self.manager_name,
            action="MANAGER_CONFIRM_SHORTLIST",
            target_province=",".join(approved_provinces),
            field_affected="shortlist_provinces",
            previous_value=None,
            new_value=approved_provinces,
            justification=f"Trưởng phòng phê duyệt chính thức 2 địa bàn ưu tiên khảo sát thực địa: {', '.join(approved_provinces)}."
        )
        if "audit_logs" not in state:
            state["audit_logs"] = []
        state["audit_logs"].append(log_entry.__dict__)

        state["selected_provinces"] = approved_provinces

        return {
            "decision": "APPROVED",
            "selected_provinces": approved_provinces,
            "route_to": "Task_GenerateProposal (1.5)"
        }

    def sign_and_submit_to_bod(self, proposal_report: Any, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task 3.2: Formal sign-off and submission to BOD.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        proposal_report.approval_status = "APPROVED_BY_BD_MANAGER_SUBMITTED_TO_BOD"
        proposal_report.signed_by = self.manager_name
        proposal_report.sign_off_date = timestamp

        log_entry = AuditLogEntry(
            log_id=f"LOG-{int(datetime.datetime.now().timestamp())}",
            timestamp=timestamp,
            actor=self.manager_name,
            action="FINAL_BOD_SUBMISSION",
            target_province=",".join(proposal_report.selected_provinces),
            field_affected="proposal_approval_status",
            previous_value="DRAFT",
            new_value=proposal_report.approval_status,
            justification="Hồ sơ đã được kiểm tra chéo 100% trích dẫn Doc_ID và ký duyệt để Ban Giám đốc phê duyệt ngân sách khảo sát."
        )
        state["audit_logs"].append(log_entry.__dict__)

        # Update persisted audit_log.json
        artifacts_dir = get_artifacts_dir()
        log_path = artifacts_dir / "audit_log.json"
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(state["audit_logs"], f, ensure_ascii=False, indent=2)

        return {
            "status": "COMPLETED",
            "signed_by": self.manager_name,
            "submitted_at": timestamp,
            "report_id": proposal_report.report_id
        }

