"""
Comprehensive Test Suite for Hưng Phát BPMN 2.0 Multi-Agent Workflow.
Tests all swimlanes, tasks, gateways, and loops.
"""

import unittest
from pathlib import Path
from src.workflow.orchestrator import HungPhatWorkflowOrchestrator
from src.models import HurdleStatus


class TestHungPhatWorkflow(unittest.TestCase):
    def setUp(self):
        self.orchestrator = HungPhatWorkflowOrchestrator()

    def test_task_1_1_deduplication_and_normalization(self):
        """Test that secondary duplicate records are removed and Doc_IDs are assigned."""
        res = self.orchestrator.run_task_1_1_clean_data()
        clean = self.orchestrator.state["clean_dataset"]
        discarded = self.orchestrator.state["discarded_data"]

        self.assertEqual(len(clean), 4)
        self.assertGreater(len(discarded), 0)

        provinces = {r.province for r in clean}
        self.assertEqual(provinces, {"Bắc Ninh", "Hải Phòng", "Đà Nẵng", "Cần Thơ"})

        for r in clean:
            self.assertTrue(r.doc_id.startswith("DOC-HP-"))
            self.assertEqual(r.normalized_year, 2026)
            self.assertTrue(len(r.verification_hash) > 0)

    def test_gateway_1_and_cost_to_serve_trigger(self):
        """Test Gateway 1 identifies Đà Nẵng exceeding direct SLA and triggers Task 1.3a."""
        self.orchestrator.run_task_1_1_clean_data()
        self.orchestrator.run_task_1_2_fit_analysis()

        g1_result = self.orchestrator.evaluate_gateway_1_hurdle_rate()
        self.assertEqual(g1_result, "ROUTE_TO_COST_ANALYZER")

        # Run Task 1.3a
        self.orchestrator.run_task_1_3a_cost_analyzer()
        cost_records = self.orchestrator.state["cost_to_serve_records"]

        self.assertIn("Đà Nẵng", cost_records)
        da_nang_cost = cost_records["Đà Nẵng"]
        self.assertTrue(da_nang_cost.is_capped)
        self.assertEqual(da_nang_cost.score_cap, 80.0)
        self.assertEqual(da_nang_cost.margin_impact_pct, -12.5)

    def test_gateway_2_human_override_and_loop_back(self):
        """Test human PTKD staff detecting a mismatch, overriding score, and re-scoring."""
        self.orchestrator.run_task_1_1_clean_data()
        self.orchestrator.run_task_1_2_fit_analysis()
        self.orchestrator.evaluate_gateway_1_hurdle_rate()
        self.orchestrator.run_task_1_3a_cost_analyzer()
        self.orchestrator.run_task_1_4_scoring()

        initial_scores = {r.province: r.final_score for r in self.orchestrator.state["score_results"]}

        # Simulate PTKD staff finding a mismatch in Cần Thơ readiness and overriding from 92 to 98
        mismatches = [{
            "province": "Cần Thơ",
            "criterion_id": "switching_cost",
            "old_val": 92.0,
            "new_val": 98.0,
            "reason": "Phỏng vấn thực tế xác nhận 100% chủ vựa phân phối đã ký cam kết chuyển đổi sang WMS."
        }]

        g2_res = self.orchestrator.complete_task_2_1_and_evaluate_gateway_2(mismatches=mismatches)
        self.assertEqual(g2_res, "MISMATCH_CORRECTED_AND_RESCORED")

        # Verify Audit Log was recorded
        audit_logs = self.orchestrator.state["audit_logs"]
        self.assertTrue(len(audit_logs) >= 1)
        last_log = audit_logs[-1]
        self.assertEqual(last_log["target_province"], "Cần Thơ")
        self.assertEqual(last_log["action"], "SCORE_OVERRIDE")
        self.assertEqual(last_log["new_value"], 98.0)

        # Verify re-scoring changed Cần Thơ final score
        new_scores = {r.province: r.final_score for r in self.orchestrator.state["score_results"]}
        self.assertGreater(new_scores["Cần Thơ"], initial_scores["Cần Thơ"])

    def test_gateway_3_manager_recalibration_loop(self):
        """Test BD Manager requesting weight recalibration and re-scoring."""
        self.orchestrator.run_task_1_1_clean_data()
        self.orchestrator.run_task_1_2_fit_analysis()
        self.orchestrator.run_task_1_3a_cost_analyzer()
        self.orchestrator.run_task_1_4_scoring()

        initial_top = self.orchestrator.state["score_results"][0].province

        # Manager requests to increase Cost-to-Serve weight heavily to 45% and decrease Market Size to 10%
        custom_weights = {
            "pmf_fit": 0.25,
            "market_size": 0.10,
            "switching_cost": 0.20,
            "cost_to_serve": 0.45
        }

        g3_res = self.orchestrator.evaluate_gateway_3_shortlist(
            approved=False,
            rejection_reason="Cần ưu tiên tối đa tối ưu chi phí phục vụ gần hub kỹ thuật để bảo toàn dòng tiền.",
            weight_adjustments=custom_weights
        )
        self.assertEqual(g3_res, "SHORTLIST_REJECTED_RECALIBRATE")

        # Now approve with recalibrated scores
        g3_app = self.orchestrator.evaluate_gateway_3_shortlist(approved=True)
        self.assertEqual(g3_app, "SHORTLIST_APPROVED")

    def test_full_pipeline_audit_trail_and_reports(self):
        """Test full end-to-end execution generates valid reports and 100% Doc_ID traceability."""
        final_state = self.orchestrator.run_full_pipeline_automated()

        self.assertEqual(final_state["current_step"], "EndEvent_1")
        self.assertTrue(Path(final_state["proposal_report_md"]).exists())
        self.assertTrue(Path(final_state["proposal_report_json"]).exists())

        # Check docx exists if generated
        if final_state.get("proposal_report_docx"):
            self.assertTrue(Path(final_state["proposal_report_docx"]).exists())

        # Verify 100% Doc_ID references
        clean_doc_ids = {r.doc_id for r in final_state["clean_dataset"]}
        score_results = final_state["score_results"]
        for r in score_results:
            for c in r.criteria_scores:
                self.assertTrue(c.doc_id.startswith("DOC-HP-"))
                self.assertIsNotNone(c.citation_quote)
                self.assertGreater(len(c.citation_quote), 5)


if __name__ == "__main__":
    unittest.main()

