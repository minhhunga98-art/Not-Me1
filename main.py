"""
CLI Entry Point for Hưng Phát Market Expansion Multi-Agent System.
Supports automated demonstration mode and interactive step-by-step BPMN walkthrough.
"""

import sys
import argparse
from pathlib import Path
from src.workflow.orchestrator import HungPhatWorkflowOrchestrator


def print_banner():
    banner = r"""
================================================================================
   HƯNG PHÁT SMART WMS - HỆ THỐNG MULTI-AGENT SÀNG LỌC ĐỊA BÀN KINH DOANH
         (Tuân thủ 100% Chuẩn Quy trình BPMN 2.0 & Truy vết Kiểm toán Doc_ID)
================================================================================
    """
    print(banner)


def run_automated_demo():
    print_banner()
    print("[*] Đang khởi động Workflow Orchestrator (Chế độ tự động chuẩn BPMN 2.0)...")
    orchestrator = HungPhatWorkflowOrchestrator()

    print("\n----------------------------------------------------------------------")
    print(">>> GIAI ĐOẠN 1: HỆ THỐNG AI AGENT (LANE 1)")
    print("----------------------------------------------------------------------")

    print("\n[+] TASK 1.1: Chuẩn hóa kỳ thống kê & Khử trùng lặp nguồn (Data Auditor Agent)")
    res_1_1 = orchestrator.run_task_1_1_clean_data()
    clean_records = orchestrator.state["clean_dataset"]
    print(f"    -> Đã quét {len(clean_records)} địa bàn chuẩn hóa, loại bỏ các nguồn tin thứ cấp.")
    for r in clean_records:
        print(f"       * [{r.doc_id}] {r.province:12s} | Năm CSDL: {r.normalized_year} | Nguồn: {r.publisher}")

    print("\n[+] TASK 1.2: Đối chiếu PMF & Năng lực triển khai (Fit & Feasibility Agent)")
    res_1_2 = orchestrator.run_task_1_2_fit_analysis()
    fit_records = orchestrator.state["fit_feasibility_records"]
    for r in fit_records:
        sla_txt = "ĐẠT SLA TRỰC TIẾP 4H" if r.meets_direct_sla else "VƯỢT BÁN KÍNH TRỰC TIẾP"
        print(f"       * {r.province:12s} | PMF: {r.feature_match_pct}% | Sẵn sàng: {r.readiness_score}/100 | Khoảng cách: {r.distance_km}km ({sla_txt})")

    print("\n[+] GATEWAY 1: Đạt ngưỡng sàn triển khai (Hurdle Rate)?")
    g1 = orchestrator.evaluate_gateway_1_hurdle_rate()
    if g1 == "ROUTE_TO_COST_ANALYZER":
        print("    -> PHÁT HIỆN ĐỊA BÀN VƯỢT NĂNG LỰC TẠI CHỖ (Đà Nẵng: 760km).")
        print("    -> RẼ NHÁNH: Kích hoạt Task 1.3a Cost Analyzer Agent.")
        orchestrator.run_task_1_3a_cost_analyzer()
        cost_records = orchestrator.state["cost_to_serve_records"]
        for prov, cr in cost_records.items():
            print(f"       * [{prov}] Áp Score Cap: {cr.score_cap}/100 | Phụ phí đối tác: {cr.annual_extra_cost_vnd:,.0f} đ/năm | Tác động biên: {cr.margin_impact_pct}%")
    else:
        print("    -> Tất cả địa bàn đạt chuẩn sàn.")

    print("\n[+] TASK 1.4: Chấm điểm Đa tiêu chí & Trích dẫn bằng chứng kiểm toán (Scoring Agent)")
    orchestrator.run_task_1_4_scoring()
    score_results = orchestrator.state["score_results"]
    print("\n    >>> BẢNG XẾP HẠNG 4 ĐỊA BÀN (SƠ BỘ):")
    print("    " + "-" * 72)
    print(f"    | {'Hạng':4s} | {'Địa bàn':12s} | {'Điểm Thô':10s} | {'Score Cap':10s} | {'Điểm Cuối':10s} | {'Trạng thái':12s} |")
    print("    " + "-" * 72)
    for r in score_results:
        cap_str = f"{r.score_cap}" if r.is_score_capped else "N/A"
        flag_str = "Cờ Phí Vùng" if r.cost_to_serve_flag else "Đạt SLA"
        print(f"    | #{r.rank:<3d} | {r.province:12s} | {r.raw_composite_score:<10.2f} | {cap_str:<10s} | {r.final_score:<10.2f} | {flag_str:12s} |")
    print("    " + "-" * 72)

    print("\n----------------------------------------------------------------------")
    print(">>> GIAI ĐOẠN 2: NHÂN VIÊN PTKD (LANE 2 - HUMAN-IN-THE-LOOP AUDIT)")
    print("----------------------------------------------------------------------")
    print("\n[+] TASK 2.1: Rút mẫu ngẫu nhiên 25% trích dẫn kiểm tra chéo (Audit Sample)")
    samples = orchestrator.prepare_task_2_1_audit_sample()
    print(f"    -> Đã rút {len(samples)} mẫu ngẫu nhiên để chuyên viên PTKD đối chiếu:")
    for s in samples:
        print(f"       * [{s.sample_id}] {s.province:12s} | Tiêu chí: {s.criterion_name} | Doc_ID: {s.doc_id}")
        print(f"         Trích dẫn gốc: \"{s.citation_quote[:85]}...\"")

    print("\n[+] GATEWAY 2: Dữ liệu & Ngữ cảnh khớp 100%?")
    print("    -> Chuyên viên PTKD xác nhận: 100% trích dẫn khớp số liệu thực tế, không có ảo giác.")
    orchestrator.complete_task_2_1_and_evaluate_gateway_2(mismatches=None)

    print("\n----------------------------------------------------------------------")
    print(">>> GIAI ĐOẠN 3: TRƯỞNG PHÒNG PTKD & ĐÓNG GÓI ĐỀ XUẤT (LANE 3 & LANE 1)")
    print("----------------------------------------------------------------------")
    print("\n[+] TASK 3.1: Rà soát Bảng xếp hạng & Ngoại lệ (Trưởng phòng PTKD)")
    summary = orchestrator.run_task_3_1_manager_review()
    top_cand_names = [c["province"] for c in summary["top_candidates"]]
    print(f"    -> Top 2 đề xuất của hệ thống: {top_cand_names}")

    print("\n[+] GATEWAY 3: Chốt được 2 địa bàn ưu tiên?")
    print(f"    -> Trưởng phòng PTKD ký duyệt chốt danh sách rút gọn: {top_cand_names}")
    orchestrator.evaluate_gateway_3_shortlist(approved=True, approved_provinces=top_cand_names)

    print("\n[+] TASK 1.5: Sinh Bộ câu hỏi Khảo sát & Báo cáo BGĐ (Proposal Architect Agent)")
    res_1_5 = orchestrator.state
    print(f"    -> Đã sinh bộ câu hỏi khảo sát thực địa giải quyết điểm mù dữ liệu.")
    print(f"    -> Xuất báo cáo Markdown: {res_1_5.get('proposal_report_md')}")
    print(f"    -> Xuất báo cáo Word: {res_1_5.get('proposal_report_docx')}")

    print("\n[+] TASK 3.2: Ký duyệt & Trình Ban Giám Đốc")
    sign_res = orchestrator.run_task_3_2_submit_to_bod()
    print(f"    -> Người ký duyệt: {sign_res['signed_by']}")
    print(f"    -> Trạng thái: {sign_res['status']} lúc {sign_res['submitted_at']}")

    print("\n======================================================================")
    print("   [HOÀN TẤT QUY TRÌNH] BÁO CÁO ĐÃ SẴN SÀNG TRÌNH BAN GIÁM ĐỐC!")
    print("======================================================================")
    print(f"Tài liệu báo cáo chi tiết đã lưu tại thư mục: c:/Agent/reports/")
    print(f"Nhật ký kiểm toán lưu tại: c:/Agent/artifacts/audit_log.json\n")


def run_interactive_mode():
    print_banner()
    print("[*] CHẾ ĐỘ TƯƠNG TÁC TỪNG BƯỚC (INTERACTIVE STEP-BY-STEP)...")
    orchestrator = HungPhatWorkflowOrchestrator()

    input("\nNhấn [Enter] để chạy Task 1.1 (Data Auditor Agent: Chuẩn hóa & Khử trùng lặp)...")
    orchestrator.run_task_1_1_clean_data()
    print("[v] Task 1.1 hoàn tất. Xem artifact tại: c:/Agent/artifacts/clean_dataset.json")

    input("\nNhấn [Enter] để chạy Task 1.2 (Fit & Feasibility Agent: Đối chiếu PMF)...")
    orchestrator.run_task_1_2_fit_analysis()
    print("[v] Task 1.2 hoàn tất.")

    input("\nNhấn [Enter] để kiểm tra Gateway 1 (Ngưỡng sàn triển khai Hurdle Rate)...")
    g1 = orchestrator.evaluate_gateway_1_hurdle_rate()
    if g1 == "ROUTE_TO_COST_ANALYZER":
        print("[!] Phát hiện địa bàn vượt năng lực. Rẽ nhánh Task 1.3a Cost Analyzer...")
        orchestrator.run_task_1_3a_cost_analyzer()

    input("\nNhấn [Enter] để chạy Task 1.4 (Scoring Agent: Chấm điểm đa tiêu chí)...")
    orchestrator.run_task_1_4_scoring()
    print("[v] Task 1.4 hoàn tất.")

    print("\n--- LANE 2: NHÂN VIÊN PTKD (HUMAN AUDIT) ---")
    samples = orchestrator.prepare_task_2_1_audit_sample()
    print(f"Đã rút {len(samples)} mẫu trích dẫn. Bạn có muốn can thiệp sửa đổi điểm số (Task 2.2) không? (y/N): ", end="")
    choice = input().strip().lower()

    if choice == 'y':
        print("\nNhập tên địa bàn muốn điều chỉnh (ví dụ: Hải Phòng): ", end="")
        prov = input().strip() or "Hải Phòng"
        print("Nhập mã tiêu chí (pmf_fit, market_size, switching_cost, cost_to_serve): ", end="")
        crit = input().strip() or "pmf_fit"
        print("Nhập điểm mới (0 - 100): ", end="")
        new_val = float(input().strip() or "95.0")
        print("Nhập lý do điều chỉnh để ghi vào Audit Log: ", end="")
        reason = input().strip() or "Khảo sát thực tế bổ sung phát hiện thêm nhu cầu đặc thù."

        mismatches = [{
            "province": prov,
            "criterion_id": crit,
            "old_val": 80.0,
            "new_val": new_val,
            "reason": reason
        }]
        print("[*] Đang ghi Audit Log và chạy lại Task 1.4...")
        orchestrator.complete_task_2_1_and_evaluate_gateway_2(mismatches=mismatches)
    else:
        print("[v] Xác nhận 100% mẫu chính xác. Chuyển tiếp Trưởng phòng PTKD.")
        orchestrator.complete_task_2_1_and_evaluate_gateway_2(mismatches=None)

    print("\n--- LANE 3: TRƯỞNG PHÒNG PTKD ---")
    summary = orchestrator.run_task_3_1_manager_review()
    top_cand = [c["province"] for c in summary["top_candidates"]]
    print(f"Top 2 ứng viên khuyến nghị: {top_cand}")
    print(f"Bạn có đồng ý phê duyệt Top 2 này không? (Y/n): ", end="")
    app_choice = input().strip().lower()

    if app_choice == 'n':
        print("Nhập 2 địa bàn bạn muốn chọn (cách nhau bởi dấu phẩy): ", end="")
        custom_prov = [p.strip() for p in input().strip().split(",") if p.strip()]
        orchestrator.evaluate_gateway_3_shortlist(approved=True, approved_provinces=custom_prov)
    else:
        orchestrator.evaluate_gateway_3_shortlist(approved=True)

    print("\n[*] Đang ký duyệt và hoàn tất báo cáo...")
    orchestrator.run_task_3_2_submit_to_bod()
    print("\n[SUCCESS] Toàn bộ quy trình hoàn tất! Báo cáo lưu tại: c:/Agent/reports/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hưng Phát Market Expansion BPMN Multi-Agent System")
    parser.add_argument("--interactive", action="store_true", help="Chạy ở chế độ tương tác từng bước")
    args = parser.parse_args()

    if args.interactive:
        run_interactive_mode()
    else:
        run_automated_demo()

