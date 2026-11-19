"""
Skill 5: Data Modeling Skill
Xác định Grain, xây dựng mô hình dữ liệu quan hệ Star Schema (Lược đồ hình sao)
cho Data Warehouse, bao gồm Fact Tables và Dimension Tables.
Tự động khởi tạo cơ sở dữ liệu phân tích SQLite (warehouse/bi_datawarehouse.db).
"""

import os
import sqlite3
import csv
from datetime import datetime, timedelta
from typing import Dict, Any, List

class DataModelingSkill:
    def __init__(self, db_path: str = "warehouse/bi_datawarehouse.db"):
        self.skill_name = "Data Modeling Skill"
        self.version = "1.0.0"
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    def define_star_schema(self) -> Dict[str, Any]:
        """Đặc tả chi tiết kiến trúc Star Schema của Data Warehouse."""
        return {
            "warehouse_name": "NovaTech Enterprise BI Warehouse",
            "schema_type": "Star Schema",
            "fact_tables": {
                "fact_sales": {
                    "grain": "Mỗi dòng tương ứng với một sản phẩm trong một đơn hàng (Order Item Grain)",
                    "primary_key": "TransactionID",
                    "foreign_keys": {
                        "CustomerID": "dim_customer.CustomerID",
                        "ProductID": "dim_product.ProductID",
                        "OrderDate": "dim_date.DateKey",
                        "Channel": "dim_channel.ChannelName"
                    },
                    "measures": ["Quantity", "UnitPrice", "UnitCost", "GrossSales", "DiscountAmount", "NetSales", "TotalCOGS", "GrossProfit", "ShippingFee"]
                },
                "fact_marketing": {
                    "grain": "Mỗi dòng tương ứng với một chiến dịch tiếp thị theo tháng/kênh (Campaign Month Grain)",
                    "primary_key": "CampaignID",
                    "foreign_keys": {
                        "StartDate": "dim_date.DateKey"
                    },
                    "measures": ["SpendVND", "Impressions", "Clicks", "Leads", "AttributedOrders"]
                },
                "fact_operations": {
                    "grain": "Mỗi dòng tương ứng với một vận đơn giao hàng (Shipment Fulfillment Grain)",
                    "primary_key": "DeliveryID",
                    "foreign_keys": {
                        "OrderID": "fact_sales.OrderID",
                        "DispatchDate": "dim_date.DateKey"
                    },
                    "measures": ["FulfillmentCostVND", "DeliveryStatus"]
                }
            },
            "dimension_tables": {
                "dim_customer": {
                    "primary_key": "CustomerID",
                    "attributes": ["CustomerName", "Email", "Phone", "City", "Region", "CustomerSegment", "RegistrationDate"]
                },
                "dim_product": {
                    "primary_key": "ProductID",
                    "attributes": ["ProductName", "Category", "Subcategory", "CostPrice", "ListPrice", "TargetMarginPct", "Supplier"]
                },
                "dim_date": {
                    "primary_key": "DateKey",
                    "attributes": ["FullDate", "Day", "Month", "MonthName", "Quarter", "Year", "DayOfWeek", "IsWeekend"]
                },
                "dim_channel": {
                    "primary_key": "ChannelName",
                    "attributes": ["ChannelType", "Platform", "Region"]
                }
            }
        }

    def generate_dim_date(self, start_date_str: str = "2025-01-01", end_date_str: str = "2025-12-31") -> List[Dict[str, Any]]:
        """Sinh bảng Dimension Thời gian (Dim_Date) chuẩn phục vụ phân tích chuỗi thời gian."""
        start_d = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_d = datetime.strptime(end_date_str, "%Y-%m-%d")
        
        date_records = []
        cur_d = start_d
        month_names = ["", "Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6",
                       "Tháng 7", "Tháng 8", "Tháng 9", "Tháng 10", "Tháng 11", "Tháng 12"]
        
        while cur_d <= end_d:
            d_str = cur_d.strftime("%Y-%m-%d")
            quarter_str = f"Q{(cur_d.month - 1) // 3 + 1}-{cur_d.year}"
            is_weekend = 1 if cur_d.weekday() >= 5 else 0
            
            date_records.append({
                "DateKey": d_str,
                "FullDate": d_str,
                "Day": cur_d.day,
                "Month": cur_d.month,
                "MonthName": month_names[cur_d.month],
                "Quarter": quarter_str,
                "Year": cur_d.year,
                "DayOfWeek": cur_d.strftime("%A"),
                "IsWeekend": is_weekend
            })
            cur_d += timedelta(days=1)
            
        return date_records

    def build_warehouse_db(self, processed_dir: str = "data/processed", raw_dir: str = "data/raw") -> Dict[str, Any]:
        """Tạo cấu trúc bảng và nạp dữ liệu sạch vào SQLite Data Warehouse."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # 1. Dim_Date
        cur.execute("""
            CREATE TABLE IF NOT EXISTS dim_date (
                DateKey TEXT PRIMARY KEY,
                FullDate TEXT,
                Day INTEGER,
                Month INTEGER,
                MonthName TEXT,
                Quarter TEXT,
                Year INTEGER,
                DayOfWeek TEXT,
                IsWeekend INTEGER
            )
        """)
        dim_dates = self.generate_dim_date()
        cur.executemany("""
            INSERT OR REPLACE INTO dim_date VALUES (:DateKey, :FullDate, :Day, :Month, :MonthName, :Quarter, :Year, :DayOfWeek, :IsWeekend)
        """, dim_dates)

        # 2. Dim_Product
        cur.execute("""
            CREATE TABLE IF NOT EXISTS dim_product (
                ProductID TEXT PRIMARY KEY,
                ProductName TEXT,
                Category TEXT,
                Subcategory TEXT,
                CostPrice REAL,
                ListPrice REAL,
                TargetMarginPct REAL,
                Supplier TEXT
            )
        """)
        prod_path = os.path.join(processed_dir, "processed_products.csv")
        if os.path.exists(prod_path):
            with open(prod_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                cur.executemany("""
                    INSERT OR REPLACE INTO dim_product VALUES (:ProductID, :ProductName, :Category, :Subcategory, :CostPrice, :ListPrice, :TargetMarginPct, :Supplier)
                """, list(reader))

        # 3. Dim_Customer
        cur.execute("""
            CREATE TABLE IF NOT EXISTS dim_customer (
                CustomerID TEXT PRIMARY KEY,
                CustomerName TEXT,
                Email TEXT,
                Phone TEXT,
                City TEXT,
                Region TEXT,
                CustomerSegment TEXT,
                RegistrationDate TEXT
            )
        """)
        cust_path = os.path.join(processed_dir, "processed_customers.csv")
        if os.path.exists(cust_path):
            with open(cust_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                cur.executemany("""
                    INSERT OR REPLACE INTO dim_customer VALUES (:CustomerID, :CustomerName, :Email, :Phone, :City, :Region, :CustomerSegment, :RegistrationDate)
                """, list(reader))

        # 4. Fact_Sales
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fact_sales (
                TransactionID TEXT PRIMARY KEY,
                OrderID TEXT,
                OrderDate TEXT,
                YearMonth TEXT,
                Quarter TEXT,
                CustomerID TEXT,
                ProductID TEXT,
                Channel TEXT,
                Quantity INTEGER,
                UnitPrice REAL,
                UnitCost REAL,
                DiscountAmount REAL,
                ShippingFee REAL,
                GrossSales REAL,
                NetSales REAL,
                TotalCOGS REAL,
                GrossProfit REAL,
                GrossMarginPct REAL,
                OrderStatus TEXT,
                SalesRepID TEXT,
                PaymentMethod TEXT,
                FOREIGN KEY (OrderDate) REFERENCES dim_date(DateKey),
                FOREIGN KEY (CustomerID) REFERENCES dim_customer(CustomerID),
                FOREIGN KEY (ProductID) REFERENCES dim_product(ProductID)
            )
        """)
        sales_path = os.path.join(processed_dir, "processed_sales_transactions.csv")
        if os.path.exists(sales_path):
            with open(sales_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                cur.executemany("""
                    INSERT OR REPLACE INTO fact_sales VALUES (
                        :TransactionID, :OrderID, :OrderDate, :YearMonth, :Quarter,
                        :CustomerID, :ProductID, :Channel, :Quantity, :UnitPrice,
                        :UnitCost, :DiscountAmount, :ShippingFee, :GrossSales, :NetSales,
                        :TotalCOGS, :GrossProfit, :GrossMarginPct, :OrderStatus, :SalesRepID, :PaymentMethod
                    )
                """, list(reader))

        # 5. Fact_Marketing
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fact_marketing (
                CampaignID TEXT PRIMARY KEY,
                CampaignName TEXT,
                MarketingChannel TEXT,
                StartDate TEXT,
                EndDate TEXT,
                SpendVND REAL,
                Impressions INTEGER,
                Clicks INTEGER,
                Leads INTEGER,
                AttributedOrders INTEGER
            )
        """)
        mkt_path = os.path.join(raw_dir, "raw_marketing_campaigns.csv")
        if os.path.exists(mkt_path):
            with open(mkt_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                cur.executemany("""
                    INSERT OR REPLACE INTO fact_marketing VALUES (
                        :CampaignID, :CampaignName, :MarketingChannel, :StartDate, :EndDate,
                        :SpendVND, :Impressions, :Clicks, :Leads, :AttributedOrders
                    )
                """, list(reader))

        conn.commit()
        
        # Verify counts
        cur.execute("SELECT COUNT(*) FROM fact_sales")
        sales_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM dim_customer")
        cust_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM dim_product")
        prod_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM dim_date")
        date_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM fact_marketing")
        mkt_count = cur.fetchone()[0]

        conn.close()

        return {
            "status": "SUCCESS",
            "db_path": self.db_path,
            "table_counts": {
                "fact_sales": sales_count,
                "dim_customer": cust_count,
                "dim_product": prod_count,
                "dim_date": date_count,
                "fact_marketing": mkt_count
            }
        }

    def execute(self) -> Dict[str, Any]:
        schema = self.define_star_schema()
        build_res = self.build_warehouse_db()
        return {
            "status": "SUCCESS",
            "schema_definition": schema,
            "warehouse_status": build_res
        }

if __name__ == "__main__":
    modeler = DataModelingSkill()
    res = modeler.execute()
    print("Skill 5 Output Summary:")
    print(f"- Data Warehouse DB: {res['warehouse_status']['db_path']}")
    for tbl, cnt in res['warehouse_status']['table_counts'].items():
        print(f"  • {tbl}: {cnt} rows")
