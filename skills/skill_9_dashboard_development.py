"""
Skill 9: Dashboard Development Skill
Đặc tả cấu trúc trực quan hóa, thông số kỹ thuật biểu đồ và hệ thống tương tác
cho 10 phân hệ của nền tảng SaaS Business Intelligence.
Hỗ trợ cross-filtering, drill-down và dynamic rendering.
"""

from typing import Dict, Any, List

class DashboardDevelopmentSkill:
    def __init__(self):
        self.skill_name = "Dashboard Development Skill"
        self.version = "1.0.0"

    def get_dashboard_spec(self) -> Dict[str, Any]:
        """Trả về đặc tả toàn diện cho 10 phân hệ giao diện SaaS BI."""
        return {
            "platform_theme": {
                "style": "Modern Enterprise SaaS BI (Palantir/PowerBI Dark Navy Aesthetic)",
                "palette": {
                    "primary_bg": "#0B1120",      # Deep Navy Canvas
                    "card_bg": "#111827",         # Charcoal Slate Card
                    "card_border": "#1F2937",     # Subtle Slate Border
                    "accent_cyan": "#06B6D4",     # Metric Highlights & Funnels
                    "accent_blue": "#3B82F6",     # Primary Charts & Series
                    "accent_purple": "#8B5CF6",   # Secondary Series & Segments
                    "accent_emerald": "#10B981",  # Surpassed Targets & Health
                    "accent_amber": "#F59E0B",    # Warnings & Lagging Metrics
                    "accent_rose": "#F43F5E",     # Critical Anomalies & Defect
                    "text_primary": "#F9FAFB",
                    "text_secondary": "#9CA3AF"
                }
            },
            "modules": [
                {
                    "id": "executive_overview",
                    "name": "1. Executive Overview",
                    "target_audience": "C-Level, Ban Giám Đốc",
                    "components": [
                        {"type": "kpi_ribbon", "cards": ["NetRevenue", "GrossMarginPct", "TotalOrders", "AOV", "ROAS", "ReturnRatePct"]},
                        {"type": "combo_chart", "title": "Doanh thu Thực tế vs Mục tiêu Ngân sách 12 Tháng", "series": ["ActualRevenue", "TargetRevenue"]},
                        {"type": "donut_chart", "title": "Cơ cấu Doanh số theo Danh mục Sản phẩm"},
                        {"type": "bar_horizontal", "title": "Hiệu suất Doanh thu & Biên lợi nhuận theo Kênh bán"}
                    ]
                },
                {
                    "id": "data_workspace",
                    "name": "2. Data Workspace",
                    "target_audience": "Data Engineer, BI Analyst",
                    "components": [
                        {"type": "file_uploader", "supported_formats": [".csv", ".xlsx", ".json"]},
                        {"type": "data_preview_table", "interactive_pagination": True},
                        {"type": "data_quality_scorecard", "metrics": ["Completeness", "Uniqueness", "Validity", "Referential Integrity"]}
                    ]
                },
                {
                    "id": "data_modeling",
                    "name": "3. Data Modeling",
                    "target_audience": "BI Architect, Data Analyst",
                    "components": [
                        {"type": "schema_graph_visualizer", "model": "Star Schema", "tables": ["fact_sales", "fact_marketing", "dim_customer", "dim_product", "dim_date"]},
                        {"type": "grain_dictionary", "level": "Order Item Grain"}
                    ]
                },
                {
                    "id": "kpi_center",
                    "name": "4. KPI Center",
                    "target_audience": "Strategy & Finance Leaders",
                    "components": [
                        {"type": "mece_metric_tree_interactive", "root": "Net Profit"},
                        {"type": "target_vs_actual_gauge", "metrics": ["Revenue Target", "Gross Margin Target", "AOV Target"]}
                    ]
                },
                {
                    "id": "bi_analytics",
                    "name": "5. BI Analytics & OLAP",
                    "target_audience": "Business Analyst, Growth Lead",
                    "components": [
                        {"type": "olap_slicer_dicer", "dimensions": ["Quarter", "Channel", "Category", "Region"]},
                        {"type": "cross_tab_matrix", "title": "Pivot Table: Kênh bán hàng x Danh mục sản phẩm"},
                        {"type": "rfm_scatter_matrix", "title": "Bản đồ Khách hàng RFM 6 Phân cụm"}
                    ]
                },
                {
                    "id": "dashboard_studio",
                    "name": "6. Dashboard Studio",
                    "target_audience": "Tất cả các bộ phận",
                    "components": [
                        {"type": "marketing_funnel_chart", "title": "Phễu chuyển đổi Tiếp thị: Impressions -> Orders"},
                        {"type": "carrier_logistics_radar", "title": "Thời gian giao hàng & Tỷ lệ đúng hạn theo Đơn vị vận chuyển"}
                    ]
                },
                {
                    "id": "ai_bi_assistant",
                    "name": "7. AI BI Assistant",
                    "target_audience": "Mọi người dùng doanh nghiệp",
                    "components": [
                        {"type": "chat_interface", "features": ["Natural Language to Insights", "SQL/Metric auto-computation", "Instant drill-down answers"]}
                    ]
                },
                {
                    "id": "insight_center",
                    "name": "8. Insight Center",
                    "target_audience": "C-Level, Trưởng phòng",
                    "components": [
                        {"type": "insight_feed", "structure": "Observation -> Finding -> Hypothesis -> Conclusion -> Action"}
                    ]
                },
                {
                    "id": "report_center",
                    "name": "9. Report Center",
                    "target_audience": "Ban Giám Đốc, Nhà đầu tư",
                    "components": [
                        {"type": "minto_pyramid_executive_brief", "export_pdf": True, "export_markdown": True}
                    ]
                },
                {
                    "id": "history_monitoring",
                    "name": "10. History & Monitoring",
                    "target_audience": "System Admin, BI Operations",
                    "components": [
                        {"type": "etl_execution_log", "audit_trail": True, "lineage_tracker": True}
                    ]
                }
            ]
        }

if __name__ == "__main__":
    dash = DashboardDevelopmentSkill()
    spec = dash.get_dashboard_spec()
    print("Skill 9 Output Summary:")
    print(f"- Modules Designed: {len(spec['modules'])}")
    for m in spec['modules']:
        print(f"  • {m['name']} ({len(m['components'])} components)")
