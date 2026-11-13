"""
Task 1.3a: Cost Analyzer Agent
Calculates Outsourced Cost-to-Serve and applies Score Cap for locations
exceeding immediate direct deployment capacity.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from src.agents.base_agent import BaseWorkflowAgent
from src.models import CostToServeRecord, FitFeasibilityRecord, HurdleStatus
from src.paths import get_artifacts_dir


class CostAnalyzerAgent(BaseWorkflowAgent):
    def __init__(self, default_score_cap: float = 80.0):
        super().__init__(
            name="CostAnalyzerAgent",
            role="Task 1.3a: Tính Cost-to-Serve & Gắn Trần Điểm Số (Score Cap)"
        )
        self.default_score_cap = default_score_cap

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.log("Bắt đầu Task 1.3a: Xử lý các địa bàn vượt ngưỡng sàn triển khai trực tiếp...")
        fit_records: List[FitFeasibilityRecord] = state.get("fit_feasibility_records", [])
        capacity_config: Dict[str, Any] = state.get("deployment_capacity", {})
        cand_feasibility: Dict[str, Any] = capacity_config.get("candidate_provinces_feasibility", {})

        cost_records: Dict[str, CostToServeRecord] = {}

        for rec in fit_records:
            province = rec.province
            if rec.hurdle_status == HurdleStatus.FAIL_CAPACITY:
                self.log(f"Phân tích chuyên sâu Cost-to-Serve cho địa bàn ngoại lệ: {province}...")
                feas_data = cand_feasibility.get(province, {})
                cts_model = feas_data.get("cost_to_serve_model", {})

                score_cap = cts_model.get("score_cap", self.default_score_cap)
                monthly_partner = cts_model.get("outsourced_partner_retainer_monthly_vnd", 18000000)
                quarterly_trip = cts_model.get("quarterly_onsite_audit_trip_vnd", 6000000)
                annual_extra = cts_model.get("estimated_annual_extra_cost_vnd", (monthly_partner * 12) + (quarterly_trip * 4))
                margin_impact = cts_model.get("margin_impact_pct", -12.5)
                strategy = cts_model.get(
                    "recommendation",
                    "Cần hợp tác với đối tác SI/IT địa phương ủy quyền kèm gói đào tạo cấp tốc để bảo đảm SLA 4h."
                )

                cost_record = CostToServeRecord(
                    province=province,
                    is_capped=True,
                    score_cap=score_cap,
                    outsourced_partner_monthly_vnd=monthly_partner,
                    quarterly_trip_vnd=quarterly_trip,
                    annual_extra_cost_vnd=annual_extra,
                    margin_impact_pct=margin_impact,
                    mitigation_strategy=strategy
                )
                cost_records[province] = cost_record
                self.log(
                    f"[{province}] -> Gắn Score Cap: {score_cap}/100. Chi phí phục vụ phát sinh: "
                    f"{annual_extra:,.0f} VNĐ/năm (Ảnh hưởng biên lợi nhuận: {margin_impact}%)."
                )

        # Save artifact cost_to_serve_analysis.json
        artifacts_dir = get_artifacts_dir()
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = artifacts_dir / "cost_to_serve_analysis.json"

        artifact_data = {
            "title": "Phân Tích Chi Phí Thuê Ngoài (Cost-to-Serve) & Ràng Buộc Score Cap",
            "capped_provinces_count": len(cost_records),
            "records": {
                prov: {
                    "province": r.province,
                    "is_capped": r.is_capped,
                    "score_cap": r.score_cap,
                    "outsourced_partner_monthly_vnd": r.outsourced_partner_monthly_vnd,
                    "quarterly_trip_vnd": r.quarterly_trip_vnd,
                    "annual_extra_cost_vnd": r.annual_extra_cost_vnd,
                    "margin_impact_pct": r.margin_impact_pct,
                    "mitigation_strategy": r.mitigation_strategy
                }
                for prov, r in cost_records.items()
            }
        }

        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(artifact_data, f, ensure_ascii=False, indent=2)

        self.log(f"Hoàn tất Task 1.3a: Đã xử lý {len(cost_records)} địa bàn có rủi ro chi phí phục vụ. Lưu tại {artifact_path}")

        return {
            "cost_to_serve_records": cost_records,
            "cost_to_serve_artifact": str(artifact_path)
        }

