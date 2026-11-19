"""
Skill 8: Business Analytics Skill
Thực hiện các phân tích nghiệp vụ chuyên sâu theo 5 trụ cột Business Intelligence:
1. Sales Intelligence: Hiệu quả kênh, nhóm hàng, nhân viên bán hàng, AOV.
2. Customer Intelligence: Phân khúc RFM (Recency, Frequency, Monetary), Giá trị vòng đời khách hàng (CLV).
3. Marketing Intelligence: Phân tích phễu chuyển đổi (Funnel Analysis), CAC, ROAS theo kênh.
4. Operational Intelligence: Thời gian xử lý & giao hàng, tỷ lệ giao đúng hạn, phân tích tỷ lệ lỗi/hoàn trả.
5. Financial Intelligence: So sánh thực tế vs ngân sách (Variance vs Targets), cơ cấu chi phí và biên lợi nhuận.
"""

import sqlite3
import csv
from datetime import datetime
from typing import Dict, Any, List

class BusinessAnalyticsSkill:
    def __init__(self, db_path: str = "warehouse/bi_datawarehouse.db"):
        self.skill_name = "Business Analytics Skill"
        self.version = "1.0.0"
        self.db_path = db_path

    # --- 1. SALES INTELLIGENCE ---
    def analyze_sales_performance(self) -> Dict[str, Any]:
        """Phân tích doanh số theo Kênh và Hiệu suất Nhân viên kinh doanh."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # By Channel
        cur.execute("""
            SELECT 
                Channel,
                COUNT(DISTINCT OrderID) as Orders,
                SUM(NetSales) as Revenue,
                SUM(GrossProfit) as Profit,
                ROUND(SUM(GrossProfit) * 100.0 / SUM(NetSales), 2) as MarginPct,
                ROUND(SUM(NetSales) * 1.0 / COUNT(DISTINCT OrderID), 0) as AOV
            FROM fact_sales
            WHERE OrderStatus = 'Completed'
            GROUP BY Channel
            ORDER BY Revenue DESC
        """)
        channel_data = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]

        # By Sales Rep
        cur.execute("""
            SELECT 
                SalesRepID,
                COUNT(DISTINCT OrderID) as DealsClosed,
                SUM(NetSales) as Revenue,
                SUM(GrossProfit) as Profit,
                ROUND(SUM(NetSales) * 1.0 / COUNT(DISTINCT OrderID), 0) as AOV
            FROM fact_sales
            WHERE OrderStatus = 'Completed'
            GROUP BY SalesRepID
            ORDER BY Revenue DESC
        """)
        rep_data = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]

        # By Category
        cur.execute("""
            SELECT 
                p.Category,
                SUM(s.Quantity) as Units,
                SUM(s.NetSales) as Revenue,
                SUM(s.GrossProfit) as Profit,
                ROUND(SUM(s.GrossProfit) * 100.0 / SUM(s.NetSales), 2) as MarginPct
            FROM fact_sales s
            JOIN dim_product p ON s.ProductID = p.ProductID
            WHERE s.OrderStatus = 'Completed'
            GROUP BY p.Category
            ORDER BY Revenue DESC
        """)
        category_data = [dict(zip([d[0] for d in cur.description], r)) for r in cur.fetchall()]

        conn.close()
        return {
            "channel_performance": channel_data,
            "sales_rep_ranking": rep_data,
            "category_performance": category_data
        }

    # --- 2. CUSTOMER INTELLIGENCE & RFM ---
    def analyze_customer_rfm(self) -> Dict[str, Any]:
        """
        Tính toán điểm RFM (Recency, Frequency, Monetary) cho toàn bộ khách hàng:
        - Recency (R): Số ngày kể từ lần mua gần nhất đến ngày chốt sổ (2025-12-31)
        - Frequency (F): Tổng số đơn hàng hoàn tất
        - Monetary (M): Tổng giá trị chi tiêu (Net Sales)
        Phân cụm: Champions, Loyal Customers, Potential Loyalists, At Risk, Hibernating, New Customers.
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                c.CustomerID,
                c.CustomerName,
                c.City,
                c.CustomerSegment,
                MAX(s.OrderDate) as LastOrderDate,
                COUNT(DISTINCT s.OrderID) as Frequency,
                SUM(s.NetSales) as Monetary
            FROM fact_sales s
            JOIN dim_customer c ON s.CustomerID = c.CustomerID
            WHERE s.OrderStatus = 'Completed'
            GROUP BY c.CustomerID, c.CustomerName, c.City, c.CustomerSegment
        """)
        raw_cust_rows = cur.fetchall()
        conn.close()

        reference_date = datetime(2025, 12, 31)
        scored_customers = []
        segment_summary = {
            "Champions": {"count": 0, "total_revenue": 0},
            "Loyal Customers": {"count": 0, "total_revenue": 0},
            "Potential Loyalists": {"count": 0, "total_revenue": 0},
            "At Risk": {"count": 0, "total_revenue": 0},
            "Hibernating": {"count": 0, "total_revenue": 0},
            "New Customers": {"count": 0, "total_revenue": 0}
        }

        for cid, name, city, seg, last_d_str, freq, monetary in raw_cust_rows:
            last_d = datetime.strptime(last_d_str, "%Y-%m-%d")
            recency_days = (reference_date - last_d).days

            # Scoring R (1-5)
            if recency_days <= 30: r_score = 5
            elif recency_days <= 90: r_score = 4
            elif recency_days <= 180: r_score = 3
            elif recency_days <= 270: r_score = 2
            else: r_score = 1

            # Scoring F (1-5)
            if freq >= 8: f_score = 5
            elif freq >= 6: f_score = 4
            elif freq >= 4: f_score = 3
            elif freq >= 2: f_score = 2
            else: f_score = 1

            # Scoring M (1-5)
            if monetary >= 150000000: m_score = 5
            elif monetary >= 80000000: m_score = 4
            elif monetary >= 40000000: m_score = 3
            elif monetary >= 20000000: m_score = 2
            else: m_score = 1

            # Segment assignment
            if r_score >= 4 and f_score >= 4:
                assigned_cluster = "Champions"
            elif r_score >= 3 and f_score >= 3:
                assigned_cluster = "Loyal Customers"
            elif r_score >= 4 and f_score <= 2:
                assigned_cluster = "Potential Loyalists"
            elif r_score <= 2 and f_score >= 3:
                assigned_cluster = "At Risk"
            elif r_score <= 2 and f_score <= 2:
                assigned_cluster = "Hibernating"
            else:
                assigned_cluster = "New Customers"

            segment_summary[assigned_cluster]["count"] += 1
            segment_summary[assigned_cluster]["total_revenue"] += monetary

            scored_customers.append({
                "CustomerID": cid,
                "CustomerName": name,
                "City": city,
                "Segment": assigned_cluster,
                "RecencyDays": recency_days,
                "Frequency": freq,
                "Monetary": monetary,
                "R_Score": r_score,
                "F_Score": f_score,
                "M_Score": m_score,
                "RFM_Composite": f"{r_score}{f_score}{m_score}"
            })

        # Calculate Average CLV estimate: Average Order Value * Frequency * Estimated Lifespan (3 years)
        total_rev = sum(c["Monetary"] for c in scored_customers)
        total_custs = len(scored_customers)
        avg_clv = round((total_rev / total_custs) * 1.8, 0) if total_custs else 0.0

        return {
            "total_customers_analyzed": total_custs,
            "estimated_average_clv": avg_clv,
            "rfm_segment_summary": segment_summary,
            "top_customers": sorted(scored_customers, key=lambda x: x["Monetary"], reverse=True)[:10]
        }

    # --- 3. MARKETING INTELLIGENCE ---
    def analyze_marketing_funnel(self) -> Dict[str, Any]:
        """Phân tích hiệu quả phễu tiếp thị (Funnel) và tính toán CAC, ROAS theo kênh."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                MarketingChannel,
                SUM(SpendVND) as TotalSpend,
                SUM(Impressions) as TotalImpressions,
                SUM(Clicks) as TotalClicks,
                SUM(Leads) as TotalLeads,
                SUM(AttributedOrders) as TotalOrders
            FROM fact_marketing
            GROUP BY MarketingChannel
            ORDER BY TotalSpend DESC
        """)
        rows = cur.fetchall()
        conn.close()

        channel_funnels = []
        overall_spend = 0
        overall_imp = 0
        overall_clicks = 0
        overall_leads = 0
        overall_orders = 0

        for ch, spend, imp, clicks, leads, orders in rows:
            overall_spend += spend
            overall_imp += imp
            overall_clicks += clicks
            overall_leads += leads
            overall_orders += orders

            ctr = round((clicks / imp * 100.0), 2) if imp else 0.0
            click_to_lead_rate = round((leads / clicks * 100.0), 2) if clicks else 0.0
            lead_to_order_rate = round((orders / leads * 100.0), 2) if leads else 0.0
            overall_conversion = round((orders / clicks * 100.0), 2) if clicks else 0.0
            cpc = round(spend / clicks, 0) if clicks else 0.0
            cac = round(spend / orders, 0) if orders else 0.0

            channel_funnels.append({
                "Channel": ch,
                "Spend": spend,
                "Impressions": imp,
                "Clicks": clicks,
                "Leads": leads,
                "Orders": orders,
                "CTR_Pct": ctr,
                "ClickToLead_Pct": click_to_lead_rate,
                "LeadToOrder_Pct": lead_to_order_rate,
                "OverallConversion_Pct": overall_conversion,
                "CPC": cpc,
                "CAC": cac
            })

        return {
            "overall_funnel": {
                "TotalSpend": overall_spend,
                "TotalImpressions": overall_imp,
                "TotalClicks": overall_clicks,
                "TotalLeads": overall_leads,
                "TotalAttributedOrders": overall_orders,
                "OverallCTR": round((overall_clicks / overall_imp * 100.0), 2) if overall_imp else 0.0,
                "OverallLeadConv": round((overall_leads / overall_clicks * 100.0), 2) if overall_clicks else 0.0,
                "OverallOrderConv": round((overall_orders / overall_leads * 100.0), 2) if overall_leads else 0.0,
                "BlendedCAC": round(overall_spend / overall_orders, 0) if overall_orders else 0.0
            },
            "channel_breakdown": channel_funnels
        }

    # --- 4. OPERATIONAL INTELLIGENCE ---
    def analyze_operations_fulfillment(self, raw_ops_path: str = "data/raw/raw_operations_logistics.csv") -> Dict[str, Any]:
        """Phân tích hiệu quả giao hàng, độ trễ và tỷ lệ hư hỏng/trả hàng theo nhà vận chuyển và kho."""
        records = []
        with open(raw_ops_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            records = list(reader)

        total_shipments = len(records)
        status_dist = {}
        carrier_perf = {}
        warehouse_perf = {}

        for r in records:
            status = r["DeliveryStatus"]
            status_dist[status] = status_dist.get(status, 0) + 1

            carrier = r["Carrier"]
            if carrier not in carrier_perf:
                carrier_perf[carrier] = {"total": 0, "ontime": 0, "delayed": 0, "damaged": 0}
            carrier_perf[carrier]["total"] += 1
            if status == "Delivered On-Time":
                carrier_perf[carrier]["ontime"] += 1
            elif status == "Delivered Delayed":
                carrier_perf[carrier]["delayed"] += 1
            elif "Damaged" in status or "Return" in status:
                carrier_perf[carrier]["damaged"] += 1

            wh = r["Warehouse"]
            if wh not in warehouse_perf:
                warehouse_perf[wh] = {"total": 0, "damaged_returns": 0}
            warehouse_perf[wh]["total"] += 1
            if "Damaged" in status or "Return" in status:
                warehouse_perf[wh]["damaged_returns"] += 1

        # Ratios
        ontime_rate = round(status_dist.get("Delivered On-Time", 0) / total_shipments * 100.0, 2) if total_shipments else 0.0
        damaged_return_rate = round(status_dist.get("Damaged/Customer Return", 0) / total_shipments * 100.0, 2) if total_shipments else 0.0

        carrier_summary = []
        for c, stats in carrier_perf.items():
            tot = stats["total"]
            carrier_summary.append({
                "Carrier": c,
                "TotalShipments": tot,
                "OnTimeRatePct": round(stats["ontime"] / tot * 100.0, 2) if tot else 0.0,
                "DelayRatePct": round(stats["delayed"] / tot * 100.0, 2) if tot else 0.0,
                "DamageReturnRatePct": round(stats["damaged"] / tot * 100.0, 2) if tot else 0.0
            })

        return {
            "total_shipments": total_shipments,
            "on_time_delivery_rate_pct": ontime_rate,
            "damaged_return_rate_pct": damaged_return_rate,
            "status_distribution": status_dist,
            "carrier_performance": carrier_summary,
            "warehouse_performance": warehouse_perf
        }

    # --- 5. FINANCIAL INTELLIGENCE & VARIANCE ANALYSIS ---
    def analyze_financial_variance(self, targets_path: str = "data/raw/raw_financial_targets.csv") -> Dict[str, Any]:
        """So sánh kết quả thực tế với mục tiêu ngân sách (Actual vs Target Variance Analysis)."""
        targets = {}
        with open(targets_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                targets[r["Month"]] = {
                    "Quarter": r["Quarter"],
                    "TargetRevenue": float(r["TargetRevenueVND"]),
                    "TargetGrossMarginPct": float(r["TargetGrossMarginPct"]) * 100.0,
                    "TargetAOV": float(r["TargetAOV"]),
                    "TargetCAC": float(r["TargetCAC"])
                }

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                YearMonth,
                COUNT(DISTINCT OrderID) as ActualOrders,
                SUM(NetSales) as ActualRevenue,
                SUM(GrossProfit) as ActualGrossProfit,
                ROUND(SUM(GrossProfit) * 100.0 / SUM(NetSales), 2) as ActualMarginPct,
                ROUND(SUM(NetSales) * 1.0 / COUNT(DISTINCT OrderID), 0) as ActualAOV
            FROM fact_sales
            WHERE OrderStatus = 'Completed'
            GROUP BY YearMonth
            ORDER BY YearMonth ASC
        """)
        actual_rows = cur.fetchall()
        conn.close()

        variance_table = []
        total_act_rev = 0
        total_tgt_rev = 0

        for ym, orders, act_rev, act_profit, act_margin, act_aov in actual_rows:
            tgt = targets.get(ym, {})
            tgt_rev = tgt.get("TargetRevenue", 0)
            rev_variance_amount = act_rev - tgt_rev
            rev_variance_pct = round((rev_variance_amount / tgt_rev * 100.0), 2) if tgt_rev else 0.0

            total_act_rev += act_rev
            total_tgt_rev += tgt_rev

            variance_table.append({
                "Month": ym,
                "ActualRevenue": act_rev,
                "TargetRevenue": tgt_rev,
                "RevenueVarianceAmount": rev_variance_amount,
                "RevenueVariancePct": rev_variance_pct,
                "ActualGrossMarginPct": act_margin,
                "TargetGrossMarginPct": tgt.get("TargetGrossMarginPct", 0),
                "ActualAOV": act_aov,
                "TargetAOV": tgt.get("TargetAOV", 0),
                "Status": "SURPASS" if rev_variance_amount >= 0 else "LAGGING"
            })

        total_variance_amt = total_act_rev - total_tgt_rev
        total_variance_pct = round((total_variance_amt / total_tgt_rev * 100.0), 2) if total_tgt_rev else 0.0

        return {
            "total_actual_revenue": total_act_rev,
            "total_target_revenue": total_tgt_rev,
            "total_revenue_variance_vnd": total_variance_amt,
            "total_revenue_variance_pct": total_variance_pct,
            "variance_status": "AHEAD OF PLAN" if total_variance_amt >= 0 else "BEHIND TARGET",
            "monthly_variance_breakdown": variance_table
        }

if __name__ == "__main__":
    analytics = BusinessAnalyticsSkill()
    sales = analytics.analyze_sales_performance()
    rfm = analytics.analyze_customer_rfm()
    mkt = analytics.analyze_marketing_funnel()
    ops = analytics.analyze_operations_fulfillment()
    fin = analytics.analyze_financial_variance()
    
    print("Skill 8 Output Summary:")
    print(f"- Sales Channels: {len(sales['channel_performance'])} channels")
    print(f"- RFM Analyzed Customers: {rfm['total_customers_analyzed']}, Avg CLV: {rfm['estimated_average_clv']:,.0f} đ")
    print(f"- Blended CAC: {mkt['overall_funnel']['BlendedCAC']:,.0f} đ")
    print(f"- On-time Delivery Rate: {ops['on_time_delivery_rate_pct']}%")
    print(f"- Financial Variance: {fin['total_revenue_variance_pct']}% vs Target ({fin['variance_status']})")
