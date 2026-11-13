"""
Workflow Orchestrator - BPMN 2.0 Engine for Hưng Phát Market Expansion.
Coordinates Swimlanes: Lane 1 (AI Agent), Lane 2 (PTKD Human Audit), Lane 3 (BD Manager Approval).
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import datetime

from src.agents.data_auditor import DataAuditorAgent
from src.agents.fit_feasibility import FitFeasibilityAgent
from src.agents.cost_analyzer import CostAnalyzerAgent
from src.agents.scoring_agent import ScoringAgent
from src.agents.proposal_architect import ProposalArchitectAgent
from src.human_lane.ptkd_audit import PTKDAuditModule
from src.human_lane.manager_review import ManagerReviewModule
from src.workflow.state_store import WorkflowStateStore
from src.models import HurdleStatus
from src.paths import CONFIG_DIR, DATA_DIR, get_artifacts_dir, get_reports_dir


class HungPhatWorkflowOrchestrator:
    def __init__(self, config_dir: Optional[Path] = None, data_dir: Optional[Path] = None):
        self.config_dir = Path(config_dir) if config_dir else CONFIG_DIR
        self.data_dir = Path(data_dir) if data_dir else DATA_DIR
        self.state_store = WorkflowStateStore()

        # Agents
        self.data_auditor = DataAuditorAgent()
        self.fit_feasibility_agent = FitFeasibilityAgent()
        self.cost_analyzer = CostAnalyzerAgent()
        self.scoring_agent = ScoringAgent()
        self.proposal_architect = ProposalArchitectAgent()

        # Human Lane Modules
        self.audit_module = PTKDAuditModule()
        self.manager_module = ManagerReviewModule()

        # Current state
        self.state: Dict[str, Any] = {}
        self.initialize_state()

    def initialize_state(self):
        """Loads baseline configs and initial raw datasets."""
        company_profile = self._read_json(self.config_dir / "company_profile.json")
        criteria_weights = self._read_json(self.config_dir / "criteria_weights.json")
        raw_market = self._read_json(self.data_dir / "raw_market_data.json")
        customer_fb = self._read_json(self.data_dir / "customer_feedback.json")
        deploy_cap = self._read_json(self.data_dir / "deployment_capacity.json")

        self.state = {
            "workflow_id": f"WF-HP-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            "current_step": "START",
            "current_swimlane": "LANE_1_AI_AGENT",
            "company_profile": company_profile,
            "criteria_weights": criteria_weights,
            "raw_market_data": raw_market,
            "customer_feedback": customer_fb,
            "deployment_capacity": deploy_cap,
            "parameter_overrides": {"score_overrides": {}, "weights": {}},
            "audit_logs": [],
            "history": []
        }
        self._record_history("INITIALIZE", "Khởi tạo hệ thống workflow BPMN 2.0 Công ty Hưng Phát.")

    def _read_json(self, path: Path) -> Any:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _record_history(self, node: str, message: str):
        entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "node": node,
            "message": message,
            "swimlane": self.state.get("current_swimlane", "SYSTEM")
        }
        self.state["history"].append(entry)

    # ------------------ BPMN NODE EXECUTION METHODS ------------------

    def run_task_1_1_clean_data(self) -> Dict[str, Any]:
        """Task 1.1: Chuẩn hóa & Khử trùng lặp nguồn (Lane 1: AI Data Auditor)"""
        self.state["current_step"] = "Task_CleanData"
        self.state["current_swimlane"] = "LANE_1_AI_AGENT"
        res = self.data_auditor.execute(self.state)
        self.state.update(res)
        self._record_history("Task_CleanData", "Hoàn tất chuẩn hóa số liệu và cấp Doc_ID.")
        self.state_store.save_state(self.state)
        return res

    def run_task_1_2_fit_analysis(self) -> Dict[str, Any]:
        """Task 1.2: Đối chiếu PMF & Năng lực triển khai (Lane 1: Fit & Feasibility Agent)"""
        self.state["current_step"] = "Task_FitAnalysis"
        self.state["current_swimlane"] = "LANE_1_AI_AGENT"
        res = self.fit_feasibility_agent.execute(self.state)
        self.state.update(res)
        self._record_history("Task_FitAnalysis", "Hoàn tất ma trận PMF và kiểm tra ngưỡng sàn SLA.")
        self.state_store.save_state(self.state)
        return res

    def evaluate_gateway_1_hurdle_rate(self) -> str:
        """
        Gateway 1: Đạt ngưỡng sàn triển khai?
        Returns 'ROUTE_TO_COST_ANALYZER' or 'PASS_TO_SCORING'.
        """
        self.state["current_step"] = "Gateway_HurdleRate"
        fit_records = self.state.get("fit_feasibility_records", [])
        has_failed_hurdle = any(r.hurdle_status == HurdleStatus.FAIL_CAPACITY for r in fit_records)

        if has_failed_hurdle:
            self._record_history(
                "Gateway_HurdleRate",
                "Phát hiện địa bàn vượt năng lực hỗ trợ tại chỗ -> Kích hoạt nhánh Task 1.3a Cost-to-Serve."
            )
            return "ROUTE_TO_COST_ANALYZER"
        else:
            self._record_history(
                "Gateway_HurdleRate",
                "Tất cả địa bàn đạt ngưỡng sàn -> Chuyển thẳng Task 1.4 Scoring."
            )
            return "PASS_TO_SCORING"

    def run_task_1_3a_cost_analyzer(self) -> Dict[str, Any]:
        """Task 1.3a: Tính Cost-to-Serve & Gắn Score Cap (Lane 1: Cost Analyzer Agent)"""
        self.state["current_step"] = "Task_CostToServe"
        self.state["current_swimlane"] = "LANE_1_AI_AGENT"
        res = self.cost_analyzer.execute(self.state)
        self.state.update(res)
        self._record_history("Task_CostToServe", "Hoàn tất tính chi phí thuê ngoài và áp Score Cap.")
        self.state_store.save_state(self.state)
        return res

    def run_task_1_4_scoring(self) -> Dict[str, Any]:
        """Task 1.4: Chấm điểm Đa tiêu chí & Trích dẫn Doc_ID (Lane 1: Scoring Agent)"""
        self.state["current_step"] = "Task_Scoring"
        self.state["current_swimlane"] = "LANE_1_AI_AGENT"
        res = self.scoring_agent.execute(self.state)
        self.state.update(res)
        self._record_history("Task_Scoring", "Hoàn tất xếp hạng 4 địa bàn kèm 100% trích dẫn Doc_ID.")
        self.state_store.save_state(self.state)
        return res

    def prepare_task_2_1_audit_sample(self) -> List[Any]:
        """Task 2.1 (Init): Rút mẫu kiểm tra chéo 20-30% cho Nhân viên PTKD (Lane 2)"""
        self.state["current_step"] = "Task_AuditSample"
        self.state["current_swimlane"] = "LANE_2_PTKD_STAFF"
        score_results = self.state.get("score_results", [])
        samples = self.audit_module.generate_audit_sample(score_results)
        self.state["audit_samples"] = samples
        self._record_history("Task_AuditSample", f"Sinh danh sách {len(samples)} mẫu trích dẫn cho nhân viên kiểm tra.")
        self.state_store.save_state(self.state)
        return samples

    def complete_task_2_1_and_evaluate_gateway_2(
        self,
        mismatches: Optional[List[Dict[str, Any]]] = None,
        auditor_name: str = "Trần Thị Mai - Chuyên viên PTKD"
    ) -> str:
        """
        Gateway 2: Dữ liệu & Ngữ cảnh khớp?
        If mismatches provided -> triggers Task 2.2 and loops back to Task 1.4.
        If empty / None -> passes to Lane 3 (Task 3.1 Review Shortlist).
        """
        self.state["current_step"] = "Gateway_DataValid"
        self.state["current_swimlane"] = "LANE_2_PTKD_STAFF"

        if mismatches:
            self._record_history("Gateway_DataValid", f"Phát hiện {len(mismatches)} sai lệch ngữ cảnh -> Chuyển Task 2.2 Hiệu chỉnh.")
            for m in mismatches:
                self.audit_module.record_manual_override(
                    actor=auditor_name,
                    target_province=m["province"],
                    criterion_id=m["criterion_id"],
                    previous_value=m["old_val"],
                    new_value=m["new_val"],
                    justification=m["reason"],
                    state=self.state
                )
            self._record_history("Task_ManualAdjust", "Đã ghi nhật ký Audit Log và cập nhật tham số.")
            # Loop back to Task 1.4
            self.run_task_1_4_scoring()
            return "MISMATCH_CORRECTED_AND_RESCORED"
        else:
            self._record_history("Gateway_DataValid", "100% mẫu kiểm tra khớp chính xác với tài liệu gốc -> Chuyển Lane 3.")
            return "VALID_PROCEED_TO_MANAGER"

    def run_task_3_1_manager_review(self) -> Dict[str, Any]:
        """Task 3.1: Rà soát Bảng xếp hạng & Duyệt ngoại lệ (Lane 3: Trưởng phòng PTKD)"""
        self.state["current_step"] = "Task_ReviewShortlist"
        self.state["current_swimlane"] = "LANE_3_BD_MANAGER"
        score_results = self.state.get("score_results", [])
        summary = self.manager_module.review_shortlist(score_results)
        self.state["manager_review_summary"] = summary
        self._record_history("Task_ReviewShortlist", "Trưởng phòng hoàn tất rà soát bảng xếp hạng.")
        self.state_store.save_state(self.state)
        return summary

    def evaluate_gateway_3_shortlist(
        self,
        approved: bool = True,
        approved_provinces: Optional[List[str]] = None,
        rejection_reason: Optional[str] = None,
        weight_adjustments: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Gateway 3: Chốt được 2 địa bàn ưu tiên?
        If approved -> advances to Task 1.5.
        If rejected -> sends back to Task 2.2 and re-scores.
        """
        self.state["current_step"] = "Gateway_ShortlistApproved"
        self.state["current_swimlane"] = "LANE_3_BD_MANAGER"

        score_results = self.state.get("score_results", [])
        if not approved_provinces:
            approved_provinces = [r.province for r in score_results[:2]]

        decision_res = self.manager_module.decide_shortlist(
            approved_provinces=approved_provinces,
            state=self.state,
            rejection_reason=rejection_reason if not approved else None,
            weight_adjustments=weight_adjustments if not approved else None
        )

        if decision_res["decision"] == "APPROVED":
            self._record_history("Gateway_ShortlistApproved", f"Trưởng phòng chốt 2 địa bàn: {approved_provinces} -> Kích hoạt Task 1.5.")
            self.run_task_1_5_generate_proposal()
            return "SHORTLIST_APPROVED"
        else:
            self._record_history("Gateway_ShortlistApproved", f"Trưởng phòng yêu cầu điều chỉnh: {rejection_reason} -> Quay lại chấm điểm.")
            self.run_task_1_4_scoring()
            return "SHORTLIST_REJECTED_RECALIBRATE"

    def run_task_1_5_generate_proposal(self) -> Dict[str, Any]:
        """Task 1.5: Sinh Bộ câu hỏi Khảo sát & Báo cáo BGĐ (Lane 1: Proposal Architect Agent)"""
        self.state["current_step"] = "Task_GenerateProposal"
        self.state["current_swimlane"] = "LANE_1_AI_AGENT"
        res = self.proposal_architect.execute(self.state)
        self.state.update(res)
        self._record_history("Task_GenerateProposal", "Đã tạo Hồ sơ đề xuất khảo sát (Markdown, JSON, DOCX).")
        self.state_store.save_state(self.state)
        return res

    def run_task_3_2_submit_to_bod(self) -> Dict[str, Any]:
        """Task 3.2: Ký duyệt & Trình Ban Giám Đốc (Lane 3: Trưởng phòng PTKD)"""
        self.state["current_step"] = "Task_SubmitBOD"
        self.state["current_swimlane"] = "LANE_3_BD_MANAGER"
        proposal = self.state.get("proposal_report")
        res = self.manager_module.sign_and_submit_to_bod(proposal, self.state)
        self.state["current_step"] = "EndEvent_1"
        self._record_history("EndEvent_1", "Quy trình hoàn tất: Hồ sơ đã được trình Ban Giám đốc.")
        self.state_store.save_state(self.state)
        return res

    def run_full_pipeline_automated(self) -> Dict[str, Any]:
        """Executes the full BPMN workflow end-to-end with automated human checks."""
        self.run_task_1_1_clean_data()
        self.run_task_1_2_fit_analysis()

        # Gateway 1
        g1 = self.evaluate_gateway_1_hurdle_rate()
        if g1 == "ROUTE_TO_COST_ANALYZER":
            self.run_task_1_3a_cost_analyzer()

        self.run_task_1_4_scoring()

        # Lane 2: Audit Sample
        self.prepare_task_2_1_audit_sample()
        # Simulate perfect audit match
        self.complete_task_2_1_and_evaluate_gateway_2(mismatches=None)

        # Lane 3: Manager Review
        self.run_task_3_1_manager_review()
        # Manager approves top 2
        self.evaluate_gateway_3_shortlist(approved=True)

        # Submit to BOD
        self.run_task_3_2_submit_to_bod()

        return self.state

    def step_forward(self) -> Dict[str, Any]:
        """Steps forward through the BPMN 2.0 sequence."""
        curr = self.state.get("current_step", "START")
        if curr == "START":
            self.run_task_1_1_clean_data()
            return {"next_step": "Task_CleanData", "message": "Hoàn tất Task 1.1: Chuẩn hóa kỳ thống kê & Khử trùng lặp nguồn (Data Auditor)."}
        elif curr == "Task_CleanData":
            self.run_task_1_2_fit_analysis()
            return {"next_step": "Task_FitAnalysis", "message": "Hoàn tất Task 1.2: Đối chiếu PMF & Năng lực đội ngũ triển khai (Fit & Feasibility)."}
        elif curr == "Task_FitAnalysis":
            g1 = self.evaluate_gateway_1_hurdle_rate()
            if g1 == "ROUTE_TO_COST_ANALYZER":
                self.run_task_1_3a_cost_analyzer()
                return {"next_step": "Task_CostToServe", "message": "Gateway 1: Đà Nẵng vượt năng lực -> Kích hoạt Task 1.3a tính Cost-to-Serve & áp Score Cap."}
            else:
                self.run_task_1_4_scoring()
                return {"next_step": "Task_Scoring", "message": "Gateway 1: Tất cả đạt ngưỡng sàn -> Chuyển sang Task 1.4 Chấm điểm."}
        elif curr == "Task_CostToServe" or curr == "Gateway_HurdleRate":
            self.run_task_1_4_scoring()
            return {"next_step": "Task_Scoring", "message": "Hoàn tất Task 1.4: Chấm điểm Đa tiêu chí & Trích dẫn bằng chứng 100% Doc_ID."}
        elif curr == "Task_Scoring":
            self.prepare_task_2_1_audit_sample()
            return {"next_step": "Task_AuditSample", "message": "Hoàn tất Task 2.1: Rút mẫu ngẫu nhiên 25% trích dẫn cho Nhân viên PTKD kiểm tra."}
        elif curr == "Task_AuditSample" or curr == "Task_ManualAdjust":
            self.complete_task_2_1_and_evaluate_gateway_2(mismatches=None)
            self.run_task_3_1_manager_review()
            return {"next_step": "Task_ReviewShortlist", "message": "Gateway 2: Dữ liệu khớp 100% -> Chuyển sang Task 3.1 Trưởng phòng PTKD rà soát."}
        elif curr == "Task_ReviewShortlist":
            self.evaluate_gateway_3_shortlist(approved=True)
            return {"next_step": "Task_GenerateProposal", "message": "Gateway 3: Trưởng phòng chốt Top 2 -> Kích hoạt Task 1.5 Sinh Hồ sơ BGĐ."}
        elif curr == "Task_GenerateProposal":
            self.run_task_3_2_submit_to_bod()
            return {"next_step": "EndEvent_1", "message": "Hoàn tất Task 3.2: Ký duyệt & Trình Ban Giám Đốc thành công!"}
        elif curr == "EndEvent_1":
            return {"next_step": "EndEvent_1", "message": "Quy trình đã hoàn tất!"}
        else:
            return {"next_step": curr, "message": f"Trạng thái hiện tại: {curr}"}


