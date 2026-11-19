"""
Skill 1: Business Understanding Skill
Xác định bối cảnh kinh doanh, chân dung người dùng (C-Level, Sales Head, Marketing, Ops, Analyst),
thiết lập mục tiêu SMART và các câu hỏi quản trị kinh doanh cốt lõi.
"""

from typing import Dict, Any, List

class BusinessUnderstandingSkill:
    def __init__(self):
        self.skill_name = "Business Understanding Skill"
        self.version = "1.0.0"

    def execute(self, company_name: str = "NovaTech Retail & E-Commerce Vietnam") -> Dict[str, Any]:
        """
        Phân tích bối cảnh kinh doanh, xác định mục tiêu và stakeholder requirements.
        """
        stakeholders = {
            "Executive (Ban Giám Đốc)": {
                "focus": ["Tổng doanh thu", "Biên lợi nhuận gộp/ròng", "Tốc độ tăng trưởng", "Hiệu quả sử dụng vốn"],
                "key_questions": [
                    "Doanh nghiệp có đạt chỉ tiêu doanh thu và lợi nhuận năm không?",
                    "Khu vực và kênh bán hàng nào đang dẫn dắt tăng trưởng?",
                    "Những rủi ro vận hành và tài chính lớn nhất hiện nay là gì?"
                ],
                "reporting_cadence": "Hàng tháng / Hàng quý"
            },
            "Head of Sales (Trưởng phòng Kinh doanh)": {
                "focus": ["Doanh số theo kênh/khu vực", "Giá trị đơn hàng trung bình (AOV)", "Năng suất nhân viên sales", "Top sản phẩm bán chạy"],
                "key_questions": [
                    "Kênh bán nào đang có doanh số cao nhất và kênh nào sụt giảm?",
                    "Tại sao AOV biến động giữa các kênh online và cửa hàng trực tiếp?",
                    "Hiệu suất của các sales reps đang chênh lệch như thế nào?"
                ],
                "reporting_cadence": "Hàng tuần / Hàng tháng"
            },
            "Marketing Team (Bộ phận Tiếp thị)": {
                "focus": ["Chi phí thu hút khách hàng (CAC)", "Tỷ lệ chuyển đổi phễu", "Lợi tức chi tiêu quảng cáo (ROAS)", "Chất lượng Lead"],
                "key_questions": [
                    "Kênh marketing nào mang lại đơn hàng với chi phí rẻ nhất (Tối ưu CAC)?",
                    "Điểm nghẽn phễu từ Impression -> Clicks -> Leads -> Orders nằm ở đâu?",
                    "ROAS của chiến dịch Facebook Ads vs Google Search vs TikTok khác nhau ra sao?"
                ],
                "reporting_cadence": "Hàng ngày / Hàng tuần"
            },
            "Operations Team (Bộ phận Vận hành & Kho vận)": {
                "focus": ["Thời gian xử lý & giao hàng", "Tỷ lệ giao đúng hạn (OTD)", "Tỷ lệ đơn hàng hoàn/hủy", "Chi phí fulfillment"],
                "key_questions": [
                    "Kho hàng nào có thời gian xuất kho chậm nhất?",
                    "Đơn vị vận chuyển nào có tỷ lệ chậm trễ hoặc hư hỏng cao nhất?",
                    "Nguyên nhân chính dẫn đến 5% tỷ lệ trả hàng (Returns) là gì?"
                ],
                "reporting_cadence": "Hàng tuần / Real-time"
            },
            "BI & Data Analyst": {
                "focus": ["Chất lượng dữ liệu", "Mô hình Star Schema", "Cây chỉ số MECE", "Tự động hóa báo cáo"],
                "key_questions": [
                    "Dữ liệu có thiếu sót, trùng lặp hoặc bất thường không?",
                    "Các bảng Fact và Dimension đã được liên kết đúng Grain chưa?",
                    "Các công thức tính toán có đồng nhất giữa các báo cáo không?"
                ],
                "reporting_cadence": "Liên tục"
            }
        }

        smart_objectives = [
            {
                "id": "OBJ-1",
                "area": "Tài chính & Doanh thu",
                "smart_statement": "Đạt tổng doanh thu thuần 22.5 tỷ VNĐ trong năm 2025 với biên lợi nhuận gộp tối thiểu 25.5%.",
                "kpis": ["Net Revenue", "Gross Margin %"]
            },
            {
                "id": "OBJ-2",
                "area": "Khách hàng & Bán lẻ",
                "smart_statement": "Nâng giá trị đơn hàng trung bình (AOV) từ 18 triệu lên 21.5 triệu VNĐ và tăng tỷ lệ khách hàng quay lại lên 32%.",
                "kpis": ["AOV", "Customer Retention Rate", "Repeat Purchase Rate"]
            },
            {
                "id": "OBJ-3",
                "area": "Marketing Tối ưu",
                "smart_statement": "Giảm CAC trung bình xuống dưới 420,000 VNĐ/khách hàng và duy trì ROAS toàn kênh trên 4.2x.",
                "kpis": ["CAC", "ROAS", "Funnel Conversion Rate"]
            },
            {
                "id": "OBJ-4",
                "area": "Vận hành xuất sắc",
                "smart_statement": "Giảm tỷ lệ trả hàng từ 6% xuống dưới 3.5% và duy trì tỷ lệ giao hàng đúng hạn trên 93%.",
                "kpis": ["Return Rate %", "On-Time Delivery Rate %", "Average Delivery Time"]
            }
        ]

        return {
            "status": "SUCCESS",
            "company": company_name,
            "industry": "Retail & Consumer Electronics Omnichannel",
            "stakeholders": stakeholders,
            "smart_objectives": smart_objectives,
            "core_framework": "DATA -> INFORMATION -> INSIGHT -> DECISION -> ACTION"
        }

if __name__ == "__main__":
    skill = BusinessUnderstandingSkill()
    res = skill.execute()
    print("Skill 1 Output Summary:")
    print(f"- Company: {res['company']}")
    print(f"- Stakeholder groups: {len(res['stakeholders'])}")
    print(f"- SMART Objectives: {len(res['smart_objectives'])}")
