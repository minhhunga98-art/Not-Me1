# HỆ THỐNG MULTI-AGENT SÀNG LỌC ĐỊA BÀN KINH DOANH - CÔNG TY HÙNG PHÁT / HƯNG PHÁT
> **Quy trình chuẩn BPMN 2.0 tích hợp AI Multi-Agent & Human-in-the-Loop**  
> **Sản phẩm:** Giải pháp Quản lý Kho thông minh cho Chuỗi bán lẻ (Smart WMS)  
> **Mục tiêu:** Sàng lọc 4 địa bàn $\rightarrow$ Chọn 2 địa bàn ưu tiên $\rightarrow$ Sinh bộ câu hỏi & Báo cáo trình Ban Giám đốc (Đảm bảo truy vết kiểm toán 100% Doc_ID).

---

## 1. Kiến Trúc 3 Swimlanes (BPMN 2.0 Mapping)

```
+-----------------------------------------------------------------------------------------------------------------------------------+
| POOL: QUY TRÌNH SÀNG LỌC & ĐỀ XUẤT KHẢO SÁT ĐỊA BÀN MỚI                                                                           |
+-------------------+---------------------------------------------------------------------------------------------------------------+
| LANE 1:           |  (Start) -> [Task 1.1: Data Auditor] (Clean Dataset + Doc_ID)                                                 |
| HỆ THỐNG          |             -> [Task 1.2: Fit & Feasibility] (PMF & Hurdle Rate)                                              |
| AI AGENT          |             -> <Gateway 1: Đạt ngưỡng sàn?>                                                                   |
| (Tự động hóa &    |                  ├── [Vượt năng lực] -> [Task 1.3a: Cost Analyzer] (Score Cap & Thuê ngoài)                   |
|  Truy vết nguồn)  |                  └── [Đạt ngưỡng] ────┐                                                                       |
|                   |                                       ├──> [Task 1.4: Scoring Agent] (100% Trích dẫn Doc_ID)                   |
|                   |                                       └──> [Task 1.5: Proposal Architect] (Sau khi chốt 2 địa bàn)            |
+-------------------+---------------------------------------------------------------------------------------------------------------+
| LANE 2:           |  [Task 2.1: Human Audit 25% Mẫu Trích Dẫn]                                                                    |
| NHÂN VIÊN PTKD    |       -> <Gateway 2: Dữ liệu khớp?>                                                                           |
| (Kiểm chứng chéo) |            ├── [Sai lệch] -> [Task 2.2: Hiệu chỉnh & Ghi Audit Log] -> (Quay lại Task 1.4)                   |
|                   |            └── [Chính xác] -> (Chuyển sang Lane 3)                                                            |
+-------------------+---------------------------------------------------------------------------------------------------------------+
| LANE 3:           |  [Task 3.1: Trưởng phòng Rà soát Bảng xếp hạng & Ngoại lệ]                                                    |
| TRƯỞNG PHÒNG PTKD |       -> <Gateway 3: Chốt được 2 địa bàn ưu tiên?>                                                            |
| (Ra quyết định)   |            ├── [Cần điều chỉnh] -> Task 2.2 (Hiệu chỉnh trọng số) -> Task 1.4                                |
|                   |            └── [Chốt 2 địa bàn] -> Kích hoạt Task 1.5 -> [Task 3.2: Ký duyệt & Trình BGĐ] -> (End)           |
+-------------------+---------------------------------------------------------------------------------------------------------------+
```

---

## 2. Cấu Trúc Thư Mục Hệ Thống (`c:\Agent`)

```
c:\Agent\
├── config/
│   ├── company_profile.json       # Hồ sơ Hưng Phát WMS, SLA 4h, bán kính phục vụ 100km
│   └── criteria_weights.json      # Bộ trọng số đa tiêu chí & ngưỡng sàn
├── data/
│   ├── raw_market_data.json       # Số liệu 4 tỉnh, bao gồm dữ liệu sơ cấp & thứ cấp trùng lặp
│   ├── customer_feedback.json     # Phản hồi khách hàng, rào cản chuyển đổi (Switching Cost)
│   └── deployment_capacity.json   # Khoảng cách, thời gian tiếp cận và mô hình chi phí phục vụ
├── src/
│   ├── models.py                  # Định nghĩa schemas, Dataclasses & Data Contracts
│   ├── agents/
│   │   ├── base_agent.py          # Lớp cơ sở tích hợp logging và tracking
│   │   ├── data_auditor.py        # Task 1.1: Chuẩn hóa kỳ cơ sở 2026, khử trùng lặp, cấp Doc_ID
│   │   ├── fit_feasibility.py     # Task 1.2 & Gateway 1: Đánh giá PMF, SLA và Hurdle Rate
│   │   ├── cost_analyzer.py       # Task 1.3a: Tính chi phí thuê ngoài (Cost-to-Serve) & Score Cap
│   │   ├── scoring_agent.py       # Task 1.4: Chấm điểm đa biến với 100% bằng chứng trích dẫn
│   │   └── proposal_architect.py  # Task 1.5: Giải quyết điểm mù, sinh câu hỏi & báo cáo BGĐ
│   ├── human_lane/
│   │   ├── ptkd_audit.py          # Task 2.1 & 2.2: Rút mẫu 25% audit & ghi Audit Log bất biến
│   │   └── manager_review.py      # Task 3.1 & 3.2: Cổng duyệt Trưởng phòng & ký duyệt tờ trình
│   ├── workflow/
│   │   ├── state_store.py         # Lưu trữ & khôi phục trạng thái quy trình
│   │   └── orchestrator.py        # BPMN 2.0 Engine điều phối toàn diện
│   └── web/
│       └── app.py                 # Web UI & REST API trực quan hóa Swimlanes
├── artifacts/                     # Các file artifact trung gian (clean_dataset, audit_log,...)
├── reports/                       # Báo cáo đầu ra: .md, .json và Microsoft Word (.docx)
├── main.py                        # Giao diện dòng lệnh CLI (Demo tự động & Tương tác)
├── run_server.py                  # Khởi chạy Web Dashboard trên cổng 8088
├── test_workflow.py               # Bộ Unit & Integration test cho toàn bộ các nhánh rẽ
└── README.md                      # Tài liệu hướng dẫn sử dụng
```

---

## 3. Hướng Dẫn Vận Hành

### Cách 1: Chạy Demo Tự Động (CLI Mode)
Chạy toàn bộ quy trình từ Task 1.1 đến Task 3.2 trong terminal:
```bash
python c:\Agent\main.py
```

### Cách 2: Chạy Tương Tác Từng Bước (Interactive Step-by-Step)
Cho phép người dùng trực tiếp can thiệp vào các cổng Gateway và Human-in-the-Loop:
```bash
python c:\Agent\main.py --interactive
```
* Có thể nhập điều chỉnh tham số tại Task 2.2 để xem hệ thống ghi nhận vào `audit_log.json` và chấm điểm lại.
* Có thể thay đổi quyết định chốt địa bàn tại Gateway 3 của Trưởng phòng PTKD.

### Cách 3: Mở Web Dashboard Trực Quan (Giao Diện Đồ Họa)
Khởi động máy chủ Web trực quan:
```bash
python c:\Agent\run_server.py
```
Mở trình duyệt truy cập: **`http://localhost:8088`**
* Theo dõi trực quan trạng thái từng Node trên 3 Swimlanes.
* Tab Bảng xếp hạng với điểm chi tiết và cờ `Cost-to-Serve`.
* Tab Human Audit cho phép nhân viên tích chọn xác nhận hoặc override điểm số.
* Tải trực tiếp báo cáo Microsoft Word (`.docx`) và Markdown (`.md`) đã định dạng hoàn chỉnh.

### Cách 4: Chạy Kiểm Thử Toàn Diện (Unit & Integration Tests)
```bash
python c:\Agent\test_workflow.py
```

---

## 4. Kết Quả Sàng Lọc Mẫu 4 Địa Bàn

| Hạng | Địa bàn | Điểm Tổng | Score Cap | Ghi chú Trọng yếu | Khuyến nghị Trình BGĐ |
| :---: | :--- | :---: | :---: | :--- | :--- |
| **#1** | **Hải Phòng** | **88.12** | Không | 58 chuỗi bán lẻ, cụm kho cảng lớn, SLA trực tiếp cao tốc 1h45p. Nhu cầu batch/expiry rất cao. | ⭐ **CHỌN KHẢO SÁT #1** |
| **#2** | **Bắc Ninh** | **86.85** | Không | 42 chuỗi, 40km từ Hà Nội (SLA < 1h), rào cản chuyển đổi thấp, biên lợi nhuận cao. | ⭐ **CHỌN KHẢO SÁT #2** |
| **#3** | **Cần Thơ** | **85.60** | Không | 48 chuỗi, 160km từ TP.HCM, rào cản chuyển đổi cực thấp (92 điểm sẵn sàng). | Dự bị chiến lược |
| **#4** | **Đà Nẵng** | **66.87** | 80.0 | Cách HN/HCM 760km, vượt năng lực onsite 4h. Phải thuê đối tác ủy quyền (tăng chi phí 240tr/năm). | Cần đối tác địa phương |

