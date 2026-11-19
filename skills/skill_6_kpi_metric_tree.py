"""
Skill 6: KPI & Metric Tree Skill
Xây dựng cây chỉ số đo lường (Metric Tree) theo nguyên tắc MECE (Mutually Exclusive, Collectively Exhaustive).
Tính toán chính xác các chỉ số tài chính, bán hàng, marketing, khách hàng, vận hành.
"""

import sqlite3
from typing import Dict, Any, List

class KPIMetricTreeSkill:
    def __init__(self, db_path: str = "warehouse/bi_datawarehouse.db"):
        self.skill_name = "KPI & Metric Tree Skill"
        self.version = "1.0.0"
        self.db_path = db_path

    def define_metric_tree(self) -> Dict[str, Any]:
        """Đặc tả cây phân rã chỉ số tài chính và vận hành (MECE Metric Tree)."""
        return {
            "root_goal": "Tối đa hóa Lợi nhuận Ròng (Net Operating Profit)",
            "level_1_breakdown": {
                "Revenue (Doanh thu thuần)": {
                    "formula": "Sum of NetSales = Total Orders * Average Order Value (AOV)",
                    "level_2_submetrics": {
                        "Total Orders (Số lượng đơn hàng)": {
                            "formula": "Traffic/Leads * Conversion Rate",
                            "drivers": ["Marketing Reach", "Website UI/UX", "Store Footfall", "Sales Promotion"]
                        },
                        "AOV (Giá trị đơn hàng TB)": {
                            "formula": "Units per Order (UPT) * Average Unit Price (AUP)",
                            "drivers": ["Cross-selling", "Bundling", "Upselling cao cấp"]
                        }
                    }
                },
                "COGS (Giá vốn hàng bán)": {
                    "formula": "Sum of (Quantity * UnitCost)",
                    "level_2_submetrics": {
                        "Procurement Unit Cost": "Chi phí nhập hàng từ nhà phân phối",
                        "Inventory Shrinkage": "Tỷ lệ hao hụt, hư hỏng sản phẩm"
                    }
                },
                "Operating Expenses (Chi phí hoạt động - OPEX)": {
                    "formula": "Marketing Spend + Fulfillment/Logistics Cost + Store Rental & Staff",
                    "level_2_submetrics": {
                        "Marketing CAC": "Spend / Attributed Customers",
                        "Fulfillment Cost per Order": "Chi phí đóng gói và vận chuyển / Đơn",
                        "Return & Defect Cost": "Chi phí xử lý đơn hoàn hủy"
                    }
                }
            }
        }

    def compute_core_kpis(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Truy vấn dữ liệu thực tế từ Data Warehouse và tính toán các KPI cốt lõi."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        where_clauses = ["OrderStatus = 'Completed'"]
        params = []

        if filters:
            if "channel" in filters:
                where_clauses.append("Channel = ?")
                params.append(filters["channel"])
            if "quarter" in filters:
                where_clauses.append("Quarter = ?")
                params.append(filters["quarter"])
            if "category" in filters:
                where_clauses.append("p.Category = ?")
                params.append(filters["category"])

        where_str = " AND ".join(where_clauses)

        query = f"""
            SELECT 
                COUNT(DISTINCT s.OrderID) as TotalOrders,
                COUNT(DISTINCT s.CustomerID) as UniqueCustomers,
                SUM(s.Quantity) as TotalUnitsSold,
                SUM(s.GrossSales) as TotalGrossRevenue,
                SUM(s.DiscountAmount) as TotalDiscounts,
                SUM(s.NetSales) as TotalNetRevenue,
                SUM(s.TotalCOGS) as TotalCOGS,
                SUM(s.GrossProfit) as TotalGrossProfit,
                SUM(s.ShippingFee) as TotalShippingFee
            FROM fact_sales s
            JOIN dim_product p ON s.ProductID = p.ProductID
            WHERE {where_str}
        """

        cur.execute(query, params)
        row = cur.fetchone()
        
        total_orders = row[0] or 0
        unique_customers = row[1] or 0
        total_units = row[2] or 0
        gross_rev = row[3] or 0.0
        discounts = row[4] or 0.0
        net_rev = row[5] or 0.0
        total_cogs = row[6] or 0.0
        gross_profit = row[7] or 0.0
        shipping_collected = row[8] or 0.0

        # Return / Cancelled rates
        cur.execute("SELECT OrderStatus, COUNT(*) FROM fact_sales GROUP BY OrderStatus")
        status_counts = dict(cur.fetchall())
        all_orders = sum(status_counts.values())
        return_rate_pct = round((status_counts.get("Returned", 0) / all_orders * 100.0), 2) if all_orders else 0.0
        cancel_rate_pct = round((status_counts.get("Cancelled", 0) / all_orders * 100.0), 2) if all_orders else 0.0

        # Marketing metrics
        cur.execute("SELECT SUM(SpendVND), SUM(AttributedOrders), SUM(Clicks), SUM(Impressions) FROM fact_marketing")
        mkt_row = cur.fetchone()
        total_mkt_spend = mkt_row[0] or 0.0
        mkt_attributed_orders = mkt_row[1] or 0
        total_clicks = mkt_row[2] or 0
        total_impressions = mkt_row[3] or 0

        # Ratios
        aov = round(net_rev / total_orders, 0) if total_orders else 0.0
        upt = round(total_units / total_orders, 2) if total_orders else 0.0
        gross_margin_pct = round((gross_profit / net_rev * 100.0), 2) if net_rev else 0.0
        discount_rate_pct = round((discounts / gross_rev * 100.0), 2) if gross_rev else 0.0
        cac = round(total_mkt_spend / unique_customers, 0) if unique_customers else 0.0
        roas = round(net_rev / total_mkt_spend, 2) if total_mkt_spend else 0.0

        conn.close()

        return {
            "status": "SUCCESS",
            "kpis": {
                "NetRevenue": {
                    "value": net_rev,
                    "formatted": f"{net_rev:,.0f} đ",
                    "unit": "VNĐ",
                    "name": "Doanh thu thuần",
                    "description": "Tổng doanh thu bán sau khi trừ giảm giá khuyến mại"
                },
                "GrossProfit": {
                    "value": gross_profit,
                    "formatted": f"{gross_profit:,.0f} đ",
                    "unit": "VNĐ",
                    "name": "Lợi nhuận gộp",
                    "description": "Doanh thu thuần trừ đi giá vốn hàng bán (COGS)"
                },
                "GrossMarginPct": {
                    "value": gross_margin_pct,
                    "formatted": f"{gross_margin_pct}%",
                    "unit": "%",
                    "name": "Biên lợi nhuận gộp",
                    "description": "Tỷ lệ phần trăm lợi nhuận gộp trên doanh thu thuần"
                },
                "TotalOrders": {
                    "value": total_orders,
                    "formatted": f"{total_orders:,}",
                    "unit": "Đơn",
                    "name": "Số đơn hoàn tất",
                    "description": "Số lượng đơn hàng giao dịch thành công"
                },
                "AOV": {
                    "value": aov,
                    "formatted": f"{aov:,.0f} đ",
                    "unit": "VNĐ/Đơn",
                    "name": "Giá trị đơn hàng TB (AOV)",
                    "description": "Average Order Value = Doanh thu thuần / Số đơn hoàn tất"
                },
                "UPT": {
                    "value": upt,
                    "formatted": f"{upt} SP/Đơn",
                    "unit": "Sản phẩm",
                    "name": "Số sản phẩm / Đơn (UPT)",
                    "description": "Units per Transaction"
                },
                "CAC": {
                    "value": cac,
                    "formatted": f"{cac:,.0f} đ",
                    "unit": "VNĐ/Khách",
                    "name": "Chi phí thu hút KH (CAC)",
                    "description": "Customer Acquisition Cost = Tổng Marketing Spend / Khách hàng mới"
                },
                "ROAS": {
                    "value": roas,
                    "formatted": f"{roas}x",
                    "unit": "Lần",
                    "name": "Lợi tức quảng cáo (ROAS)",
                    "description": "Return on Ad Spend = Doanh thu thuần / Chi tiêu Marketing"
                },
                "ReturnRatePct": {
                    "value": return_rate_pct,
                    "formatted": f"{return_rate_pct}%",
                    "unit": "%",
                    "name": "Tỷ lệ hoàn trả (Return Rate)",
                    "description": "Tỷ lệ đơn hàng bị trả do hư hỏng hoặc khách từ chối"
                },
                "CancelRatePct": {
                    "value": cancel_rate_pct,
                    "formatted": f"{cancel_rate_pct}%",
                    "unit": "%",
                    "name": "Tỷ lệ hủy đơn (Cancel Rate)",
                    "description": "Tỷ lệ đơn hàng bị hủy trước khi đóng gói hoặc xuất kho"
                }
            }
        }

if __name__ == "__main__":
    kpi_skill = KPIMetricTreeSkill()
    res = kpi_skill.compute_core_kpis()
    print("Skill 6 Output Summary:")
    for k, v in res["kpis"].items():
        print(f"  • {v['name']} ({k}): {v['formatted']}")
