"""
Task 1.2 & Gateway 1: Fit & Feasibility Agent
Analyzes Product-Market Fit (PMF), Switching Costs, and evaluates Deployment Team Capacity.
Routes candidates through Gateway 1 (Hurdle Rate Gate).
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from src.agents.base_agent import BaseWorkflowAgent
from src.models import FitFeasibilityRecord, HurdleStatus, CleanDataRecord
from src.paths import get_artifacts_dir


class FitFeasibilityAgent(BaseWorkflowAgent):
    def __init__(self):
        super().__init__(
            name="FitFeasibilityAgent",
            role="Task 1.2: Đối chiếu PMF & Năng lực Đội ngũ Triển khai"
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.log("Bắt đầu Task 1.2: Phân tích độ khớp PMF, Rào cản chuyển đổi & Năng lực hỗ trợ tại chỗ...")
        clean_records: List[CleanDataRecord] = state.get("clean_dataset", [])
        customer_feedback: List[Dict[str, Any]] = state.get("customer_feedback", [])
        capacity_config: Dict[str, Any] = state.get("deployment_capacity", {})
        cand_feasibility: Dict[str, Any] = capacity_config.get("candidate_provinces_feasibility", {})

        feedback_by_province = {fb["province"]: fb for fb in customer_feedback}
        fit_records: List[FitFeasibilityRecord] = []
        gateway_1_routing: Dict[str, str] = {}

        for rec in clean_records:
            province = rec.province
            fb = feedback_by_province.get(province, {})
            feasibility = cand_feasibility.get(province, {})

            feature_match = fb.get("feature_match_pct", 70.0)
            switching_barrier = fb.get("switching_barrier_level", "MEDIUM")
            readiness_score = fb.get("readiness_score", 70.0)
            doc_id_feedback = fb.get("doc_id", "DOC-HP-FB-UNKNOWN")

            distance_km = feasibility.get("distance_km", 200.0)
            travel_time = feasibility.get("travel_time_hours", 3.0)
            meets_direct_sla = feasibility.get("meets_direct_sla", False)
            hurdle_status_str = feasibility.get("hurdle_status", "PASS")
            assigned_hub = feasibility.get("assigned_hub")

            hurdle_status = HurdleStatus.PASS if meets_direct_sla else HurdleStatus.FAIL_CAPACITY

            rationale = (
                f"Độ khớp PMF đạt {feature_match}%. Rào cản chuyển đổi: {switching_barrier} (Điểm sẵn sàng: {readiness_score}/100). "
                f"Khoảng cách tới hub kỹ thuật: {distance_km}km ({travel_time}h di chuyển). "
                f"Trạng thái SLA trực tiếp 4h: {'Đạt' if meets_direct_sla else 'Vượt năng lực hỗ trợ tại chỗ'}."
            )

            fit_record = FitFeasibilityRecord(
                province=province,
                doc_id_market=rec.doc_id,
                doc_id_feedback=doc_id_feedback,
                feature_match_pct=feature_match,
                switching_barrier=switching_barrier,
                readiness_score=readiness_score,
                distance_km=distance_km,
                travel_time_hours=travel_time,
                meets_direct_sla=meets_direct_sla,
                hurdle_status=hurdle_status,
                rationale=rationale,
                assigned_hub=assigned_hub
            )
            fit_records.append(fit_record)

            # Gateway 1 Logic:
            if hurdle_status == HurdleStatus.PASS:
                gateway_1_routing[province] = "DIRECT_TO_SCORING (Task 1.4)"
                self.log(f"[{province}] -> ĐẠT NGƯỠNG SÀN (Hurdle Rate: PASS). Tuyến thẳng tới Task 1.4.")
            else:
                gateway_1_routing[province] = "ROUTE_TO_COST_ANALYZER (Task 1.3a)"
                self.log(f"[{province}] -> VƯỢT NĂNG LỰC TẠI CHỖ (Hurdle Rate: FAIL_CAPACITY). Chuyển sang Task 1.3a tính Cost-to-Serve & áp Score Cap.", level="warning")

        # Save artifact fit_feasibility_matrix.json
        artifacts_dir = get_artifacts_dir()
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = artifacts_dir / "fit_feasibility_matrix.json"

        artifact_data = {
            "evaluation_title": "Ma Trận Đối Chiếu PMF & Năng Lực Triển Khai",
            "evaluated_provinces": len(fit_records),
            "gateway_1_summary": gateway_1_routing,
            "records": [
                {
                    "province": r.province,
                    "doc_id_market": r.doc_id_market,
                    "doc_id_feedback": r.doc_id_feedback,
                    "feature_match_pct": r.feature_match_pct,
                    "switching_barrier": r.switching_barrier,
                    "readiness_score": r.readiness_score,
                    "distance_km": r.distance_km,
                    "travel_time_hours": r.travel_time_hours,
                    "meets_direct_sla": r.meets_direct_sla,
                    "hurdle_status": r.hurdle_status.value,
                    "rationale": r.rationale,
                    "assigned_hub": r.assigned_hub
                }
                for r in fit_records
            ]
        }

        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(artifact_data, f, ensure_ascii=False, indent=2)

        self.log(f"Hoàn tất Task 1.2: Lưu ma trận PMF & Feasibility tại {artifact_path}")

        return {
            "fit_feasibility_records": fit_records,
            "gateway_1_routing": gateway_1_routing,
            "fit_feasibility_artifact": str(artifact_path)
        }

