"""
Unit Test Suite - CCN-DA AI-Powered Business Intelligence Platform
Kiểm thử tự động 100% toàn diện:
1. Bộ điều phối 12 Skills (core/orchestrator.py)
2. Quy trình vận hành 7 Giai đoạn (workflow/engine.py)
3. Cổng kiểm chứng bắt buộc Verify Gate (Math Invariants)
4. Vòng lặp Loopback "Điều chỉnh & Tái phân tích" (Feedback to Process)
"""

import os
import sys
import unittest

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from core.orchestrator import BIAgentOrchestrator
from workflow.engine import BIWorkflowEngine
from workflow.state import StageStatus


class TestCCNDAPlatform(unittest.TestCase):
    def setUp(self):
        self.workspace_root = WORKSPACE_ROOT

    def test_01_all_12_skills_orchestration(self):
        """Kiểm thử thực thi thành công toàn bộ 12 BI Skills."""
        orchestrator = BIAgentOrchestrator(self.workspace_root)
        payload = orchestrator.run_full_pipeline()
        
        self.assertIsNotNone(payload, "Payload không được rỗng")
        self.assertIn("kpis", payload, "Payload phải chứa bảng KPI cốt lõi")
        self.assertIn("olap", payload, "Payload phải chứa khối OLAP đa chiều")
        self.assertIn("insights", payload, "Payload phải trích xuất Insight chuẩn Minto")
        self.assertIn("verify_checks", payload, "Payload phải chứa bộ kiểm chứng Verify Gate")
        
        # Kiểm tra tính toàn vẹn KPI
        kpis = payload["kpis"].get("kpis", payload["kpis"])
        net_rev = kpis["NetRevenue"]["value"] if "value" in kpis["NetRevenue"] else kpis["NetRevenue"].get("raw", 0)
        gross_profit = kpis["GrossProfit"]["value"] if "value" in kpis["GrossProfit"] else kpis["GrossProfit"].get("raw", 0)
        gross_margin = kpis["GrossMarginPct"]["value"] if "value" in kpis["GrossMarginPct"] else kpis["GrossMarginPct"].get("raw", 0)
        self.assertGreater(net_rev, 0, "Doanh thu thuần phải > 0")
        self.assertGreater(gross_profit, 0, "Lợi nhuận gộp phải > 0")
        self.assertGreater(gross_margin, 0, "Biên lợi nhuận gộp phải > 0")

    def test_02_seven_stage_workflow_engine(self):
        """Kiểm thử vòng đời 7 Giai đoạn chuẩn mực của BIWorkflowEngine."""
        engine = BIWorkflowEngine(self.workspace_root)
        state = engine.run_workflow(user_feedback_decision="APPROVE")

        # Xác thực trạng thái hoàn thành
        self.assertTrue(state.verification_passed, "Verify Gate bắt buộc phải PASS 100%")
        self.assertEqual(len(state.verification_errors), 0, "Không được tồn tại lỗi kiểm chứng")
        self.assertEqual(state.stage_statuses.get("SHEET"), StageStatus.SUCCESS)
        self.assertEqual(state.stage_statuses.get("CLEANING"), StageStatus.SUCCESS)
        self.assertEqual(state.stage_statuses.get("PROCESS"), StageStatus.SUCCESS)
        self.assertEqual(state.stage_statuses.get("VERIFY"), StageStatus.VERIFIED)
        self.assertEqual(state.stage_statuses.get("FEEDBACK"), StageStatus.SUCCESS)
        self.assertEqual(state.stage_statuses.get("EXPORT"), StageStatus.SUCCESS)
        self.assertEqual(state.stage_statuses.get("REPORT"), StageStatus.SUCCESS)

        # Kiểm tra xuất file
        self.assertGreaterEqual(len(state.exported_files), 4, "Phải xuất ít nhất 4 tệp dữ liệu đã kiểm chứng")

    def test_03_loopback_feedback_reanalysis(self):
        """Kiểm thử vòng lặp Feedback Loopback: Điều chỉnh tham số -> Tái phân tích."""
        engine = BIWorkflowEngine(self.workspace_root)
        state = engine.run_workflow(
            user_feedback_decision="REVISE",
            feedback_adjustments={"quarter_filter": "Q4", "channel_filter": "Online Web"}
        )

        self.assertTrue(state.verification_passed, "Verify Gate phải PASS sau khi tái phân tích")
        self.assertEqual(state.stage_statuses.get("FEEDBACK"), StageStatus.SUCCESS)
        self.assertIn("monthly_rollup", state.olap_cubes)

    def test_04_math_invariants_verify_gate(self):
        """Kiểm chứng bất biến toán học: Doanh thu thuần = Doanh thu gộp - Chiết khấu."""
        engine = BIWorkflowEngine(self.workspace_root)
        state = engine.run_workflow(user_feedback_decision="APPROVE")
        kpis = state.kpis

        gross = kpis.get("TotalGrossSales", 0)
        disc = kpis.get("TotalDiscounts", 0)
        net = kpis.get("NetRevenue", 0)

        # Invariant 1: Net = Gross - Disc
        self.assertAlmostEqual(net, gross - disc, places=2, msg="Bất biến toán học Net = Gross - Disc vi phạm!")

        # Invariant 2: Gross Profit = Net - Total COGS
        cogs = kpis.get("TotalCOGS", 0)
        profit = kpis.get("GrossProfit", 0)
        self.assertAlmostEqual(profit, net - cogs, places=2, msg="Bất biến toán học Profit = Net - COGS vi phạm!")

    def test_05_gemini_ai_assistant(self):
        """Kiểm thử tính năng Trợ lý AI BI Assistant phản hồi thông minh."""
        from server import ask_gemini_bi_assistant
        res = ask_gemini_bi_assistant("Doanh thu thuần năm 2025 là bao nhiêu và kênh nào cao nhất?")
        self.assertIn("reply", res, "Phản hồi AI phải có trường 'reply'")
        self.assertTrue(len(res["reply"]) > 20, "Nội dung trả lời của AI phải chi tiết, không rỗng")
        self.assertIn(res.get("source"), ["gemini", "rule-based", "system"], "Nguồn phản hồi hợp lệ")


if __name__ == "__main__":
    unittest.main()
