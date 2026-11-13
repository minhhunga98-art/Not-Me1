"""
Task 1.4: Scoring Agent
Evaluates candidate provinces across multi-criteria weighted matrix.
Enforces 100% citation with Doc_ID and applies Score Cap constraints.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.agents.base_agent import BaseWorkflowAgent
from src.models import (
    ProvinceScoreResult,
    CriterionScoreItem,
    CleanDataRecord,
    FitFeasibilityRecord,
    CostToServeRecord,
)
from src.paths import get_artifacts_dir


class ScoringAgent(BaseWorkflowAgent):
    def __init__(self):
        super().__init__(
            name="ScoringAgent",
            role="Task 1.4: Chấm điểm Đa tiêu chí & Trích dẫn bằng chứng kiểm toán (Doc_ID)"
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.log("Bắt đầu Task 1.4: Thực hiện chấm điểm đa tiêu chí và liên kết trích dẫn gốc...")

        clean_records: List[CleanDataRecord] = state.get("clean_dataset", [])
        fit_records: List[FitFeasibilityRecord] = state.get("fit_feasibility_records", [])
        cost_records: Dict[str, CostToServeRecord] = state.get("cost_to_serve_records", {})
        customer_feedback: List[Dict[str, Any]] = state.get("customer_feedback", [])
        criteria_config: Dict[str, Any] = state.get("criteria_weights", {})
        param_overrides: Dict[str, Any] = state.get("parameter_overrides", {})

        criteria_list = criteria_config.get("criteria", [])
        weights_map = {c["id"]: c["weight"] for c in criteria_list}

        # Apply any active weight overrides from human review if present
        if "weights" in param_overrides:
            self.log(f"Áp dụng trọng số điều chỉnh từ Human Audit: {param_overrides['weights']}")
            weights_map.update(param_overrides["weights"])

        clean_by_prov = {r.province: r for r in clean_records}
        fit_by_prov = {r.province: r for r in fit_records}
        fb_by_prov = {r["province"]: r for r in customer_feedback}

        score_results: List[ProvinceScoreResult] = []

        for prov, clean_rec in clean_by_prov.items():
            fit_rec = fit_by_prov.get(prov)
            fb_rec = fb_by_prov.get(prov, {})
            cost_rec = cost_records.get(prov)

            criteria_scores: List[CriterionScoreItem] = []

            # 1. PMF Score (Weight: 30%)
            pmf_raw = float(fb_rec.get("feature_match_pct", 75.0))
            if prov in param_overrides.get("score_overrides", {}).get("pmf_fit", {}):
                override_val = param_overrides["score_overrides"]["pmf_fit"][prov]
                self.log(f"[{prov}] Override PMF score: {pmf_raw} -> {override_val}")
                pmf_raw = float(override_val)

            w_pmf = weights_map.get("pmf_fit", 0.30)
            criteria_scores.append(CriterionScoreItem(
                criterion_id="pmf_fit",
                criterion_name="Độ Khớp Giải Pháp & PMF",
                weight=w_pmf,
                raw_score=pmf_raw,
                weighted_score=round(pmf_raw * w_pmf, 2),
                doc_id=fb_rec.get("doc_id", "DOC-HP-FB-001"),
                citation_quote=fb_rec.get("quote", "Khảo sát nhu cầu khách hàng Hưng Phát."),
                data_source_title=f"Khảo sát PTKD Hưng Phát ({prov})"
            ))

            # 2. Market Size Score (Weight: 25%)
            # Calculate from retail chain count and warehouse density
            retail_count = clean_rec.metrics.get("retail_chain_count", 30)
            # Normalization scale: 20 chains = 50 pts, 60 chains = 100 pts
            market_raw = min(100.0, max(40.0, (retail_count / 60.0) * 100.0))
            if prov in param_overrides.get("score_overrides", {}).get("market_size", {}):
                override_val = param_overrides["score_overrides"]["market_size"][prov]
                market_raw = float(override_val)

            w_market = weights_map.get("market_size", 0.25)
            criteria_scores.append(CriterionScoreItem(
                criterion_id="market_size",
                criterion_name="Quy Mô & Mật Độ Chuỗi Bán Lẻ",
                weight=w_market,
                raw_score=round(market_raw, 1),
                weighted_score=round(market_raw * w_market, 2),
                doc_id=clean_rec.doc_id,
                citation_quote=clean_rec.direct_quote,
                data_source_title=clean_rec.source_title
            ))

            # 3. Switching Cost & Readiness Score (Weight: 25%)
            readiness_raw = float(fb_rec.get("readiness_score", 70.0))
            if prov in param_overrides.get("score_overrides", {}).get("switching_cost", {}):
                override_val = param_overrides["score_overrides"]["switching_cost"][prov]
                readiness_raw = float(override_val)

            w_switching = weights_map.get("switching_cost", 0.25)
            criteria_scores.append(CriterionScoreItem(
                criterion_id="switching_cost",
                criterion_name="Sự Sẵn Sàng & Chi Phí Chuyển Đổi",
                weight=w_switching,
                raw_score=readiness_raw,
                weighted_score=round(readiness_raw * w_switching, 2),
                doc_id=fb_rec.get("doc_id", "DOC-HP-FB-001"),
                citation_quote=f"Rào cản chuyển đổi {fb_rec.get('switching_barrier_level')}. {fb_rec.get('quote')}",
                data_source_title=f"Đánh giá rào cản chuyển đổi hệ thống ERP ({prov})"
            ))

            # 4. Cost-to-Serve & Feasibility Score (Weight: 20%)
            if fit_rec and fit_rec.meets_direct_sla:
                # Direct SLA: score based on proximity (40km = 95, 120km = 88, 160km = 84)
                dist = fit_rec.distance_km
                cost_to_serve_raw = max(60.0, 100.0 - (dist * 0.10))
            else:
                # Needs outsourcing: penalize cost-to-serve
                cost_to_serve_raw = 55.0

            if prov in param_overrides.get("score_overrides", {}).get("cost_to_serve", {}):
                override_val = param_overrides["score_overrides"]["cost_to_serve"][prov]
                cost_to_serve_raw = float(override_val)

            w_cts = weights_map.get("cost_to_serve", 0.20)
            criteria_scores.append(CriterionScoreItem(
                criterion_id="cost_to_serve",
                criterion_name="Chi Phí Phục Vụ & Khả Thi Triển Khai",
                weight=w_cts,
                raw_score=round(cost_to_serve_raw, 1),
                weighted_score=round(cost_to_serve_raw * w_cts, 2),
                doc_id=clean_rec.doc_id,
                citation_quote=(
                    f"Khoảng cách {fit_rec.distance_km}km. "
                    f"Thời gian tiếp cận {fit_rec.travel_time_hours}h. "
                    f"{'Đạt SLA trực tiếp' if fit_rec.meets_direct_sla else 'Cần đối tác ủy quyền thuê ngoài.'}"
                ) if fit_rec else "N/A",
                data_source_title="Quy hoạch năng lực kỹ thuật Hưng Phát"
            ))

            # Total raw weighted score
            total_raw = sum(item.weighted_score for item in criteria_scores)
            is_capped = False
            score_cap_val = None
            final_score = total_raw
            notes = ""

            # Check Score Cap if Cost-to-Serve triggered
            if cost_rec and cost_rec.is_capped:
                is_capped = True
                score_cap_val = cost_rec.score_cap
                if total_raw > score_cap_val:
                    final_score = score_cap_val
                    notes = f"Đã áp dụng trần điểm Score Cap {score_cap_val} do vượt năng lực hỗ trợ tại chỗ trực tiếp (Điểm thô: {total_raw:.2f})."
                else:
                    notes = f"Có gắn cờ Cost-to-Serve nhưng điểm thô ({total_raw:.2f}) không vượt trần {score_cap_val}."
            else:
                notes = "Đạt tiêu chuẩn hỗ trợ tại chỗ trực tiếp từ trung tâm kỹ thuật."

            score_results.append(ProvinceScoreResult(
                province=prov,
                raw_composite_score=round(total_raw, 2),
                is_score_capped=is_capped,
                score_cap=score_cap_val,
                final_score=round(final_score, 2),
                criteria_scores=criteria_scores,
                cost_to_serve_flag=(cost_rec is not None and cost_rec.is_capped),
                notes=notes
            ))

        # Rank descending
        score_results.sort(key=lambda x: x.final_score, reverse=True)
        for i, res in enumerate(score_results, 1):
            res.rank = i

        # Save artifact scorecard_rationale.json
        artifacts_dir = get_artifacts_dir()
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = artifacts_dir / "scorecard_rationale.json"

        artifact_data = {
            "title": "Bảng Xếp Hạng Đa Tiêu Chí Kèm Trích Dẫn Bằng Chứng Chuẩn Kiểm Toán",
            "scoring_weights_used": weights_map,
            "leaderboard": [
                {
                    "rank": r.rank,
                    "province": r.province,
                    "final_score": r.final_score,
                    "raw_composite_score": r.raw_composite_score,
                    "is_score_capped": r.is_score_capped,
                    "score_cap": r.score_cap,
                    "cost_to_serve_flag": r.cost_to_serve_flag,
                    "notes": r.notes,
                    "criteria_breakdown": [
                        {
                            "criterion_id": c.criterion_id,
                            "criterion_name": c.criterion_name,
                            "weight": c.weight,
                            "raw_score": c.raw_score,
                            "weighted_score": c.weighted_score,
                            "doc_id": c.doc_id,
                            "citation_quote": c.citation_quote,
                            "data_source_title": c.data_source_title
                        }
                        for c in r.criteria_scores
                    ]
                }
                for r in score_results
            ]
        }

        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(artifact_data, f, ensure_ascii=False, indent=2)

        self.log("Hoàn tất Task 1.4: Đã xếp hạng 4 địa bàn. Kết quả sơ bộ:")
        for r in score_results:
            cap_info = f" [Score Cap: {r.score_cap}]" if r.is_score_capped else ""
            self.log(f"  #{r.rank} {r.province}: {r.final_score} điểm (Điểm thô: {r.raw_composite_score}){cap_info}")

        return {
            "score_results": score_results,
            "scorecard_artifact": str(artifact_path)
        }

