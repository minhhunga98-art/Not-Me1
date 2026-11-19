"""
Skill 7: OLAP Analysis Skill
Thực hiện các phép toán phân tích khối dữ liệu đa chiều (OLAP Cubes):
- Slice: Cắt lát dữ liệu theo 1 chiều (ví dụ: chỉ xem Kênh Shopee)
- Dice: Thái hạt lựu theo nhiều chiều (ví dụ: Q2-2025 AND Kênh Online AND Ngành Laptops)
- Roll-up: Tổng hợp dữ liệu lên cấp bậc cao hơn (từ Ngày -> Tháng -> Quý -> Năm)
- Drill-down: Đi sâu vào chi tiết cấp bậc thấp hơn (từ Danh mục -> Phân khúc -> Sản phẩm)
- Pivot / Cross-tabulation: Bảng xoay chiều ma trận 2 chiều (ví dụ: Kênh bán x Danh mục sản phẩm)
"""

import sqlite3
from typing import Dict, Any, List

class OLAPAnalysisSkill:
    def __init__(self, db_path: str = "warehouse/bi_datawarehouse.db"):
        self.skill_name = "OLAP Analysis Skill"
        self.version = "1.0.0"
        self.db_path = db_path

    def roll_up_time(self, level: str = "Month") -> List[Dict[str, Any]]:
        """Roll-up dữ liệu doanh thu theo cấp bậc thời gian (Month hoặc Quarter)."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        group_col = "s.YearMonth" if level.lower() == "month" else "s.Quarter"

        query = f"""
            SELECT 
                {group_col} as TimePeriod,
                COUNT(DISTINCT s.OrderID) as Orders,
                SUM(s.Quantity) as UnitsSold,
                SUM(s.NetSales) as NetRevenue,
                SUM(s.GrossProfit) as GrossProfit,
                ROUND(SUM(s.GrossProfit) * 100.0 / SUM(s.NetSales), 2) as MarginPct,
                ROUND(SUM(s.NetSales) * 1.0 / COUNT(DISTINCT s.OrderID), 0) as AOV
            FROM fact_sales s
            WHERE s.OrderStatus = 'Completed'
            GROUP BY {group_col}
            ORDER BY TimePeriod ASC
        """
        cur.execute(query)
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
        result = [dict(zip(cols, row)) for row in rows]
        conn.close()
        return result

    def drill_down_product_hierarchy(self, category_filter: str = None) -> List[Dict[str, Any]]:
        """Drill-down từ Danh mục sản phẩm xuống Phân loại sản phẩm (Subcategory) và Tên sản phẩm."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        where_clause = "WHERE s.OrderStatus = 'Completed'"
        params = []
        if category_filter:
            where_clause += " AND p.Category = ?"
            params.append(category_filter)

        query = f"""
            SELECT 
                p.Category,
                p.Subcategory,
                p.ProductName,
                SUM(s.Quantity) as TotalUnits,
                SUM(s.NetSales) as TotalRevenue,
                SUM(s.GrossProfit) as TotalProfit,
                ROUND(SUM(s.GrossProfit) * 100.0 / SUM(s.NetSales), 2) as MarginPct
            FROM fact_sales s
            JOIN dim_product p ON s.ProductID = p.ProductID
            {where_clause}
            GROUP BY p.Category, p.Subcategory, p.ProductName
            ORDER BY TotalRevenue DESC
        """
        cur.execute(query, params)
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
        result = [dict(zip(cols, row)) for row in rows]
        conn.close()
        return result

    def slice_channel(self, channel_name: str) -> Dict[str, Any]:
        """Slice: Cắt lát dữ liệu phân tích chỉ tập trung vào một kênh bán hàng duy nhất."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        query = """
            SELECT 
                s.Channel,
                COUNT(DISTINCT s.OrderID) as Orders,
                SUM(s.NetSales) as Revenue,
                SUM(s.GrossProfit) as Profit,
                ROUND(SUM(s.GrossProfit) * 100.0 / SUM(s.NetSales), 2) as MarginPct,
                ROUND(SUM(s.NetSales) * 1.0 / COUNT(DISTINCT s.OrderID), 0) as AOV
            FROM fact_sales s
            WHERE s.OrderStatus = 'Completed' AND s.Channel = ?
            GROUP BY s.Channel
        """
        cur.execute(query, (channel_name,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return {"Channel": channel_name, "error": "Không có dữ liệu"}
        return {
            "Channel": row[0],
            "Orders": row[1],
            "Revenue": row[2],
            "Profit": row[3],
            "MarginPct": row[4],
            "AOV": row[5]
        }

    def pivot_channel_by_category(self) -> Dict[str, Any]:
        """Tạo bảng ma trận chéo (Cross-tabulation Pivot): Doanh thu theo Kênh bán và Danh mục sản phẩm."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        query = """
            SELECT 
                s.Channel,
                p.Category,
                SUM(s.NetSales) as Revenue
            FROM fact_sales s
            JOIN dim_product p ON s.ProductID = p.ProductID
            WHERE s.OrderStatus = 'Completed'
            GROUP BY s.Channel, p.Category
        """
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        matrix = {}
        all_categories = set()
        all_channels = set()

        for ch, cat, rev in rows:
            all_channels.add(ch)
            all_categories.add(cat)
            if ch not in matrix:
                matrix[ch] = {}
            matrix[ch][cat] = rev

        categories_list = sorted(list(all_categories))
        channels_list = sorted(list(all_channels))

        pivot_table = []
        for ch in channels_list:
            row_data = {"Channel": ch}
            row_total = 0
            for cat in categories_list:
                val = matrix.get(ch, {}).get(cat, 0)
                row_data[cat] = val
                row_total += val
            row_data["TotalRevenue"] = row_total
            pivot_table.append(row_data)

        return {
            "channels": channels_list,
            "categories": categories_list,
            "pivot_data": pivot_table
        }

if __name__ == "__main__":
    olap = OLAPAnalysisSkill()
    time_series = olap.roll_up_time("Quarter")
    pivot = olap.pivot_channel_by_category()
    print("Skill 7 Output Summary:")
    print("- Quarterly Roll-up:")
    for q in time_series:
        print(f"  • {q['TimePeriod']}: Rev={q['NetRevenue']:,.0f} đ, Margin={q['MarginPct']}%, AOV={q['AOV']:,.0f} đ")
    print(f"- Cross-tab Matrix: {len(pivot['channels'])} channels x {len(pivot['categories'])} categories")
