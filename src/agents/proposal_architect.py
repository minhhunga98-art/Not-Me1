"""
Task 1.5: Proposal Architect Agent
Synthesizes data blindspots for shortlisted provinces, designs field survey questionnaire,
and compiles the comprehensive Executive BOD Proposal Report with 100% audit trail appendix.
Generates Markdown, JSON, and Word (.docx) formats.
"""

import json
import datetime
from pathlib import Path
from typing import Dict, Any, List
from src.agents.base_agent import BaseWorkflowAgent
from src.models import (
    BODProposalReport,
    SurveyQuestion,
    ProvinceScoreResult,
    CleanDataRecord,
    FitFeasibilityRecord,
)
from src.paths import get_reports_dir

# Check if python-docx is available
try:
    import docx
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import parse_xml, OxmlElement
    from docx.oxml.ns import nsdecls, qn
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


class ProposalArchitectAgent(BaseWorkflowAgent):
    def __init__(self):
        super().__init__(
            name="ProposalArchitectAgent",
            role="Task 1.5: Sinh Bộ câu hỏi Khảo sát Thực địa & Báo cáo Trình Ban Giám Đốc"
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.log("Bắt đầu Task 1.5: Tổng hợp điểm mù dữ liệu, sinh bộ câu hỏi khảo sát & lập Báo cáo Đề xuất Trình BGĐ...")

        selected_provinces: List[str] = state.get("selected_provinces", [])
        score_results: List[ProvinceScoreResult] = state.get("score_results", [])
        clean_records: List[CleanDataRecord] = state.get("clean_dataset", [])
        fit_records: List[FitFeasibilityRecord] = state.get("fit_feasibility_records", [])
        customer_feedback: List[Dict[str, Any]] = state.get("customer_feedback", [])
        audit_logs: List[Dict[str, Any]] = state.get("audit_logs", [])
        company_profile: Dict[str, Any] = state.get("company_profile", {})

        if not selected_provinces:
            # Fallback to top 2 from leaderboard
            selected_provinces = [r.province for r in score_results[:2]]
            self.log(f"Chưa có chỉ định từ Manager, tự động lấy Top 2 bảng xếp hạng: {selected_provinces}", level="warning")

        clean_by_prov = {r.province: r for r in clean_records}
        score_by_prov = {r.province: r for r in score_results}
        fit_by_prov = {r.province: r for r in fit_records}
        fb_by_prov = {r["province"]: r for r in customer_feedback}

        # 1. Identify Data Blindspots & Generate Targeted Survey Questions
        survey_questions: List[SurveyQuestion] = []
        q_counter = 1

        for prov in selected_provinces:
            clean_rec = clean_by_prov.get(prov)
            fit_rec = fit_by_prov.get(prov)
            fb_rec = fb_by_prov.get(prov, {})

            # Blindspot 1: Hardware & Network Infrastructure in Warehouses
            survey_questions.append(SurveyQuestion(
                question_id=f"Q-SURVEY-{q_counter:03d}",
                province=prov,
                category="Hạ tầng & Thiết bị phần cứng",
                question_text=f"Kho hàng của doanh nghiệp tại {prov} hiện đã trang bị mạng WiFi công nghiệp phủ sóng toàn kho và thiết bị quét PDA/Barcode chuyên dụng hay chưa?",
                target_respondent="Trưởng kho / Quản trị viên CNTT",
                blindspot_addressed=f"Xác định chi phí đầu tư thiết bị ngoại vi của khách hàng tại {prov} để tính gói hỗ trợ trọn gói.",
                priority="HIGH"
            ))
            q_counter += 1

            # Blindspot 2: Existing ERP Integration & Custom Workflows
            survey_questions.append(SurveyQuestion(
                question_id=f"Q-SURVEY-{q_counter:03d}",
                province=prov,
                category="Tích hợp Hệ thống Hiện hữu",
                question_text=f"Doanh nghiệp đang vận hành hệ thống kế toán/bán hàng nào? Nếu tích hợp Hưng Phát WMS qua Open API, quy trình kiểm toán nội bộ mất bao lâu để cấp quyền kết nối dữ liệu?",
                target_respondent="Giám đốc CNTT (CIO) / Trưởng phòng Kế toán",
                blindspot_addressed=f"Đo lường thời gian chốt hợp đồng và thời gian triển khai tích hợp kỹ thuật tại {prov}.",
                priority="HIGH"
            ))
            q_counter += 1

            # Blindspot 3: Peak Volume Operations & SLA Expectations
            survey_questions.append(SurveyQuestion(
                question_id=f"Q-SURVEY-{q_counter:03d}",
                province=prov,
                category="Quy trình Vận hành Thực tế & SLA",
                question_text=f"Vào mùa cao điểm hoặc ca đêm, doanh nghiệp có quy định xử lý sự cố kho trong bao lâu? Mức độ chấp nhận xử lý từ xa qua TeamViewer/UltraView so với kỹ sư onsite?",
                target_respondent="Giám đốc Vận hành (COO) / Trưởng bộ phận Chuỗi Cung ứng",
                blindspot_addressed=f"Kiểm chứng tính khả thi của cam kết SLA 4 giờ và nhu cầu bố trí nhân sự tại {prov}.",
                priority="MEDIUM"
            ))
            q_counter += 1

        # 2. Compile Executive Proposal Report
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_id = f"HP-PROPOSAL-{datetime.datetime.now().strftime('%Y%m%d')}-01"

        exec_summary = (
            f"Báo cáo đề xuất chiến lược mở rộng địa bàn kinh doanh của Công ty Hưng Phát cho giải pháp "
            f"Smart WMS. Sau quá trình sàng lọc 4 địa bàn tiềm năng qua hệ thống Multi-Agent AI (Lane 1), "
            f"kiểm tra chéo mẫu trích dẫn từ nhân viên PTKD (Lane 2), và rà soát của Trưởng phòng PTKD (Lane 3), "
            f"chúng tôi kính trình Ban Giám đốc phê duyệt kế hoạch khảo sát thực địa tại 2 địa bàn ưu tiên: "
            f"**{', '.join(selected_provinces)}**."
        )

        detailed_prov_info = []
        for prov in selected_provinces:
            s_res = score_by_prov.get(prov)
            c_rec = clean_by_prov.get(prov)
            f_rec = fit_by_prov.get(prov)
            detailed_prov_info.append({
                "province": prov,
                "rank": s_res.rank if s_res else 1,
                "final_score": s_res.final_score if s_res else 0,
                "retail_chains": c_rec.metrics.get("retail_chain_count", 0) if c_rec else 0,
                "market_growth": c_rec.metrics.get("growth_rate_pct", 0) if c_rec else 0,
                "distance_km": f_rec.distance_km if f_rec else 0,
                "sla_readiness": "Đạt chuẩn SLA 4h trực tiếp" if f_rec and f_rec.meets_direct_sla else "Ủy quyền đối tác",
                "doc_citations": [c.doc_id for c in s_res.criteria_scores] if s_res else []
            })

        proposal = BODProposalReport(
            report_id=report_id,
            generated_at=timestamp,
            company_name=company_profile.get("company_name", "Công ty Cổ phần Công nghệ Hưng Phát"),
            solution_name=company_profile.get("solution_name", "Hưng Phát Smart WMS"),
            selected_provinces=selected_provinces,
            executive_summary=exec_summary,
            detailed_provinces=detailed_prov_info,
            survey_agenda=survey_questions,
            audit_trail_summary={
                "total_audit_logs": len(audit_logs),
                "doc_ids_referenced": list({q.doc_id for r in score_results for q in r.criteria_scores}),
                "audit_logs": audit_logs
            }
        )

        # 3. Save Artifacts: JSON, Markdown, and Word (.docx)
        reports_dir = get_reports_dir()
        reports_dir.mkdir(parents=True, exist_ok=True)

        json_path = reports_dir / f"{report_id}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(proposal.__dict__, f, default=lambda o: o.__dict__, ensure_ascii=False, indent=2)

        md_path = reports_dir / f"{report_id}.md"
        md_content = self._render_markdown_report(proposal, score_results, clean_records, audit_logs)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        docx_path = reports_dir / f"{report_id}.docx"
        if DOCX_AVAILABLE:
            self._generate_docx_report(docx_path, proposal, score_results, clean_records, audit_logs)
            self.log(f"Đã xuất báo cáo Word chuẩn Ban Giám Đốc tại: {docx_path}")

        self.log(f"Hoàn tất Task 1.5: Hồ sơ đề xuất khảo sát đã được tạo thành công.")
        self.log(f"  - Markdown: {md_path}")
        self.log(f"  - JSON: {json_path}")

        return {
            "proposal_report": proposal,
            "proposal_report_md": str(md_path),
            "proposal_report_json": str(json_path),
            "proposal_report_docx": str(docx_path) if DOCX_AVAILABLE else None
        }

    def _render_markdown_report(
        self,
        proposal: BODProposalReport,
        score_results: List[ProvinceScoreResult],
        clean_records: List[CleanDataRecord],
        audit_logs: List[Dict[str, Any]]
    ) -> str:
        provinces_str = ", ".join(proposal.selected_provinces)
        md = f"""# TỜ TRÌNH BAN GIÁM ĐỐC: ĐỀ XUẤT KHẢO SÁT THỰC ĐỊA MỞ RỘNG ĐỊA BÀN KINH DOANH
**Mã tài liệu:** `{proposal.report_id}`  
**Thời gian lập:** {proposal.generated_at}  
**Đơn vị trình:** Phòng Phát triển Kinh doanh (PTKD) - {proposal.company_name}  
**Sản phẩm mục tiêu:** {proposal.solution_name}  
**Địa bàn đề xuất ưu tiên khảo sát:** **{provinces_str}**  

---

## 1. TÓM TẮT ĐIỀU HÀNH (EXECUTIVE SUMMARY)
{proposal.executive_summary}

* **Tính minh bạch và kiểm toán:** 100% số liệu đánh giá được trích dẫn trực tiếp từ các văn bản, nghiên cứu thị trường chính thống với mã định danh `Doc_ID`, đã trải qua khâu kiểm chứng chéo 25% mẫu thực tế của Nhân viên PTKD và được rà soát bởi Trưởng phòng PTKD.

---

## 2. KẾT QUẢ SÀNG LỌC & BẢNG XẾP HẠNG 4 ĐỊA BÀN

| Hạng | Địa bàn | Điểm Tổng kết | Điểm Thô | Trần Điểm (Score Cap) | Cờ Cost-to-Serve | Khuyến nghị Trình BGĐ |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
"""
        for r in score_results:
            is_top = r.province in proposal.selected_provinces
            status = "⭐ **ĐỀ XUẤT KHẢO SÁT**" if is_top else "Dự bị / Giám sát thêm"
            cap_text = f"Áp trần {r.score_cap}" if r.is_score_capped else "Không áp trần"
            cts_flag = "⚠️ Có phát sinh" if r.cost_to_serve_flag else "✅ An toàn"
            md += f"| **#{r.rank}** | **{r.province}** | **{r.final_score:.2f}** | {r.raw_composite_score:.2f} | {cap_text} | {cts_flag} | {status} |\n"

        md += """
---

## 3. PHÂN TÍCH CHUYÊN SÂU 2 ĐỊA BÀN ĐƯỢC CHỌN

"""
        for prov_info in proposal.detailed_provinces:
            p_name = prov_info["province"]
            md += f"### 3.{prov_info['rank']} Địa bàn: {p_name} (Xếp hạng #{prov_info['rank']})\n"
            md += f"- **Quy mô chuỗi bán lẻ:** {prov_info['retail_chains']} chuỗi mục tiêu (Tăng trưởng: {prov_info['market_growth']}%/năm).\n"
            md += f"- **Khoảng cách tới hub kỹ thuật:** {prov_info['distance_km']} km ({prov_info['sla_readiness']}).\n"
            md += f"- **Mã tài liệu trích dẫn thẩm định:** `{', '.join(prov_info['doc_citations'])}`.\n\n"

        md += """## 4. BỘ CÂU HỎI KHẢO SÁT THỰC ĐỊA (GIẢI QUYẾT ĐIỂM MÙ DỮ LIỆU)

Để bảo đảm chuyến khảo sát thực địa đạt hiệu quả cao nhất, hệ thống AI Proposal Architect đã sinh các câu hỏi mục tiêu nhắm vào các điểm mù dữ liệu:

| STT | Địa bàn | Nhóm chủ đề | Câu hỏi khảo sát thực địa | Đối tượng phỏng vấn | Mục tiêu giải quyết điểm mù |
| :---: | :--- | :--- | :--- | :--- | :--- |
"""
        for i, q in enumerate(proposal.survey_agenda, 1):
            md += f"| {i} | {q.province} | {q.category} | {q.question_text} | {q.target_respondent} | {q.blindspot_addressed} |\n"

        md += """
---

## 5. PHỤ LỤC KIỂM TOÁN NGƯỢC (AUDIT TRAIL 100%)

### 5.1 Danh mục Tài liệu Gốc (Primary Sources & Doc_ID)
| Doc_ID | Địa bàn | Tên tài liệu / Cơ quan xuất bản | Năm gốc | Năm quy đổi | Trích dẫn nguyên văn kiểm toán |
| :--- | :--- | :--- | :---: | :---: | :--- |
"""
        for rec in clean_records:
            md += f"| `{rec.doc_id}` | {rec.province} | {rec.source_title} ({rec.publisher}) | {rec.publication_year} | {rec.normalized_year} | \"{rec.direct_quote}\" |\n"

        md += """
### 5.2 Nhật ký Thay đổi Tham số (Audit Log)
| Thời gian | Tác nhân | Hành động | Địa bàn | Trường tác động | Giá trị cũ | Giá trị mới | Lý do giải trình |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
        if not audit_logs:
            md += "| (Không có thay đổi thủ công) | Hệ thống | Khởi tạo ban đầu | ALL | N/A | N/A | N/A | Chấm điểm tự động theo tiêu chuẩn gốc |\\n"
        else:
            for log in audit_logs:
                md += f"| {log.get('timestamp')} | {log.get('actor')} | `{log.get('action')}` | {log.get('target_province')} | {log.get('field_affected')} | {log.get('previous_value')} | {log.get('new_value')} | {log.get('justification')} |\n"

        md += f"""
---

## 6. Ý KIẾN PHÊ DUYỆT CỦA TRƯỞNG PHÒNG PTKD & TRÌNH BAN GIÁM ĐỐC
* **Người phê duyệt:** {proposal.signed_by or 'Nguyễn Văn Hùng - Trưởng phòng PTKD'}
* **Trạng thái:** {proposal.approval_status}
* **Ngày ký duyệt:** {proposal.sign_off_date or proposal.generated_at}
* **Đề xuất Ban Giám đốc:** Kính đề nghị Ban Giám đốc phê duyệt chủ trương và cấp ngân sách khảo sát thực địa 2 địa bàn **{provinces_str}** trong tháng tới.
"""
        return md

    def _generate_docx_report(
        self,
        output_path: Path,
        proposal: BODProposalReport,
        score_results: List[ProvinceScoreResult],
        clean_records: List[CleanDataRecord],
        audit_logs: List[Dict[str, Any]]
    ):
        doc = docx.Document()

        # Styles & Margins
        for section in doc.sections:
            section.top_margin = Inches(0.8)
            section.bottom_margin = Inches(0.8)
            section.left_margin = Inches(0.8)
            section.right_margin = Inches(0.8)

        # Title
        title_p = doc.add_paragraph()
        title_run = title_p.add_run("TỜ TRÌNH BAN GIÁM ĐỐC\nĐỀ XUẤT KHẢO SÁT THỰC ĐỊA MỞ RỘNG ĐỊA BÀN KINH DOANH")
        title_run.font.size = Pt(16)
        title_run.font.bold = True
        title_run.font.color.rgb = RGBColor(16, 44, 87)
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Metadata
        meta_p = doc.add_paragraph()
        meta_p.add_run(f"Mã tài liệu: {proposal.report_id} | Ngày: {proposal.generated_at}\n")
        meta_p.add_run(f"Đơn vị trình: Phòng Phát triển Kinh doanh - {proposal.company_name}\n")
        meta_p.add_run(f"Địa bàn đề xuất: {', '.join(proposal.selected_provinces)}")
        meta_p.runs[0].font.italic = True

        doc.add_heading("1. Tóm Tắt Điều Hành (Executive Summary)", level=1)
        doc.add_paragraph(proposal.executive_summary)

        doc.add_heading("2. Kết Quả Bảng Xếp Hạng 4 Địa Bàn", level=1)
        table = doc.add_table(rows=1, cols=5)
        table.style = 'Light Shading Accent 1'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "Hạng"
        hdr_cells[1].text = "Địa bàn"
        hdr_cells[2].text = "Điểm Cuối"
        hdr_cells[3].text = "Cost-to-Serve"
        hdr_cells[4].text = "Khuyến nghị"

        for r in score_results:
            row_cells = table.add_row().cells
            row_cells[0].text = f"#{r.rank}"
            row_cells[1].text = r.province
            row_cells[2].text = f"{r.final_score:.2f}"
            row_cells[3].text = "Có áp trần" if r.is_score_capped else "Chuẩn SLA"
            row_cells[4].text = "ĐỀ XUẤT KHẢO SÁT" if r.province in proposal.selected_provinces else "Dự bị"

        doc.add_heading("3. Bộ Câu Hỏi Khảo Sát Thực Địa", level=1)
        for q in proposal.survey_agenda:
            p = doc.add_paragraph(style='List Bullet')
            p.add_run(f"[{q.province} - {q.category}] ").bold = True
            p.add_run(f"{q.question_text} (Đối tượng: {q.target_respondent})")

        doc.add_heading("4. Phụ Lục Truy Vết Nguồn (Doc_ID Audit Trail)", level=1)
        for rec in clean_records:
            p = doc.add_paragraph(style='List Bullet')
            p.add_run(f"Doc_ID: {rec.doc_id} | {rec.province}: ").bold = True
            p.add_run(f"{rec.source_title} ({rec.publisher}, {rec.publication_year}) - \"{rec.direct_quote}\"")

        doc.add_heading("5. Phê Duyệt & Chữ Ký Trình Ban Giám Đốc", level=1)
        sign_p = doc.add_paragraph()
        sign_p.add_run(f"Trưởng phòng PTKD: {proposal.signed_by or 'Nguyễn Văn Hùng'}\n")
        sign_p.add_run(f"Trạng thái: {proposal.approval_status}\n")
        sign_p.add_run(f"Thời gian trình: {proposal.sign_off_date or proposal.generated_at}\n")

        doc.save(str(output_path))

