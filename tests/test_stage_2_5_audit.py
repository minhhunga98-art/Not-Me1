"""
Unit Tests cho Giai đoạn 2.5 (Audit Gate: Kiểm duyệt & Bổ khuyết thông tin)
và tính tương thích với Bước 3 (Analysis) & Bước 4 (Reporting).
"""

import os
import unittest
import json
from workflow.stage_2_5_audit import DataReadinessAuditStage
from workflow.stage_3_analysis import AnalysisStage

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestStage2_5Audit(unittest.TestCase):

    def test_audit_dataset_missing_cogs_and_channels(self):
        """Kiểm tra khi bộ dữ liệu thiếu cột COGS và Kênh bán hàng."""
        sample_records = [
            {"order_id": "ORD-1", "order_date": "2024-01-15", "revenue": "1000000", "product_name": "Sản phẩm A"},
            {"order_id": "ORD-2", "order_date": "2024-02-20", "revenue": "2000000", "product_name": "Sản phẩm B"}
        ]
        stage = DataReadinessAuditStage()
        audit_res = stage.audit_dataset_readiness(
            cleaned_records=sample_records,
            file_name="test_missing.csv",
            company_type="Bán lẻ"
        )
        self.assertEqual(audit_res["status"], "SUCCESS")
        self.assertTrue(audit_res["has_gaps"])
        missing_ids = [m["id"] for m in audit_res["missing_items"]]
        self.assertIn("cogs", missing_ids)
        self.assertIn("channels", missing_ids)
        self.assertIn("customer_rfm", missing_ids)
        self.assertTrue(len(audit_res["ai_gap_summary"]) > 0)
        self.assertTrue(len(audit_res["ai_elicitation_questions"]) > 0)

    def test_save_user_decisions_and_skip(self):
        """Kiểm tra người dùng chọn bỏ qua khai báo -> Bước 3 lược bỏ phép tính và Verify Gate vẫn PASS."""
        stage_audit = DataReadinessAuditStage()
        stage_audit.save_user_decisions(
            declarations={},
            omitted_metrics=["cogs", "channels", "customer_rfm"]
        )

        sample_records = [
            {"order_id": "ORD-1", "order_date": "2024-01-15", "revenue": "1000000", "product_name": "Sản phẩm A"},
            {"order_id": "ORD-2", "order_date": "2024-02-20", "revenue": "2000000", "product_name": "Sản phẩm B"}
        ]
        stage_analysis = AnalysisStage()
        res = stage_analysis.run_analysis(
            cleaned_records=sample_records,
            business_context={"questions": ["Doanh thu theo kênh bán hàng nào cao nhất?", "Sản phẩm nào mang lại lợi nhuận cao nhất?"]}
        )

        kpis = res["kpis"]
        self.assertTrue(kpis.get("cogs_omitted"))
        self.assertIsNone(kpis.get("GrossProfit"))
        self.assertIsNone(kpis.get("GrossMarginPct"))
        self.assertEqual(kpis["Formatted"]["GrossProfit"], "Đã lược bỏ")
        self.assertEqual(kpis["Formatted"]["GrossMarginPct"], "Đã lược bỏ")

        # Verify gate vẫn PASS dù cogs đã lược bỏ
        self.assertTrue(res["verify_passed"])

        # Câu hỏi liên quan đến kênh bán được ghi nhận OMITTED_BY_USER
        q_ans = res["answered_questions"]
        q_channel = next((q for q in q_ans if "kênh" in q["question"].lower()), None)
        self.assertIsNotNone(q_channel)
        self.assertEqual(q_channel["status"], "OMITTED_BY_USER")

    def test_save_user_decisions_with_declared_cogs(self):
        """Kiểm tra người dùng khai báo ước tính COGS 60% -> Bước 3 tính toán đúng tỷ lệ khai báo."""
        stage_audit = DataReadinessAuditStage()
        stage_audit.save_user_decisions(
            declarations={"cogs": "60%", "channels": "Cửa hàng trực tiếp"},
            omitted_metrics=["customer_rfm"]
        )

        sample_records = [
            {"order_id": "ORD-1", "order_date": "2024-01-15", "revenue": "1000000", "product_name": "Sản phẩm A"},
            {"order_id": "ORD-2", "order_date": "2024-02-20", "revenue": "2000000", "product_name": "Sản phẩm B"}
        ]
        stage_analysis = AnalysisStage()
        res = stage_analysis.run_analysis(
            cleaned_records=sample_records,
            business_context={"questions": ["Sản phẩm nào mang lại lợi nhuận cao nhất?"]}
        )

        kpis = res["kpis"]
        # Doanh thu thuần = 3,000,000. COGS ước tính 60% = 1,800,000. Lợi nhuận gộp = 1,200,000. Biên LN = 40%
        self.assertEqual(kpis["NetRevenue"], 3000000.0)
        self.assertEqual(kpis["TotalCOGS"], 1800000.0)
        self.assertEqual(kpis["GrossProfit"], 1200000.0)
        self.assertEqual(kpis["GrossMarginPct"], 40.0)
        self.assertTrue(res["verify_passed"])

if __name__ == "__main__":
    unittest.main()
