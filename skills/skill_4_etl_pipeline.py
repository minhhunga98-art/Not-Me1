"""
Skill 4: ETL/ELT Pipeline Skill
Làm sạch, chuẩn hóa kiểu dữ liệu, tính toán các trường phái sinh tài chính cơ bản
(Gross Revenue, Net Revenue, COGS, Gross Profit, Margin %), chuẩn hóa Grain
và xuất ra các bảng processed sẵn sàng nạp vào Data Warehouse.
"""

import os
import csv
from datetime import datetime
from typing import Dict, Any, List

class ETLPipelineSkill:
    def __init__(self):
        self.skill_name = "ETL/ELT Pipeline Skill"
        self.version = "1.0.0"

    def transform_sales(self, raw_sales: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Làm sạch và tính toán các metrics phái sinh ở cấp độ dòng đơn hàng (Order Item Grain)."""
        cleaned_sales = []
        for row in raw_sales:
            try:
                qty = int(row["Quantity"])
                unit_price = float(row["UnitPrice"])
                unit_cost = float(row["UnitCost"])
                discount = float(row.get("DiscountAmount", 0))
                shipping = float(row.get("ShippingFee", 0))
                
                # In transactions, UnitPrice is the actual selling unit price
                net_sales = qty * unit_price
                gross_sales = net_sales + discount
                total_cogs = qty * unit_cost
                gross_profit = net_sales - total_cogs
                margin_pct = (gross_profit / net_sales * 100.0) if net_sales > 0 else 0.0

                order_date_str = row["OrderDate"]
                dt = datetime.strptime(order_date_str, "%Y-%m-%d")
                year_month = dt.strftime("%Y-%m")
                quarter = f"Q{(dt.month - 1) // 3 + 1}-{dt.year}"

                cleaned_sales.append({
                    "TransactionID": row["TransactionID"],
                    "OrderID": row["OrderID"],
                    "OrderDate": order_date_str,
                    "YearMonth": year_month,
                    "Quarter": quarter,
                    "CustomerID": row["CustomerID"],
                    "ProductID": row["ProductID"],
                    "Channel": row["Channel"],
                    "Quantity": qty,
                    "UnitPrice": unit_price,
                    "UnitCost": unit_cost,
                    "DiscountAmount": discount,
                    "ShippingFee": shipping,
                    "GrossSales": gross_sales,
                    "NetSales": net_sales,
                    "TotalCOGS": total_cogs,
                    "GrossProfit": gross_profit,
                    "GrossMarginPct": round(margin_pct, 2),
                    "OrderStatus": row["OrderStatus"],
                    "SalesRepID": row["SalesRepID"],
                    "PaymentMethod": row["PaymentMethod"]
                })
            except Exception as e:
                # Log bad records
                continue
        return cleaned_sales

    def transform_customers(self, raw_customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Chuẩn hóa dữ liệu khách hàng."""
        cleaned_cust = []
        for row in raw_customers:
            cleaned_cust.append({
                "CustomerID": row["CustomerID"].strip(),
                "CustomerName": row["CustomerName"].strip(),
                "Email": row["Email"].strip().lower(),
                "Phone": row["Phone"].strip(),
                "City": row["City"].strip(),
                "Region": row["Region"].strip(),
                "CustomerSegment": row["CustomerSegment"].strip(),
                "RegistrationDate": row["RegistrationDate"].strip()
            })
        return cleaned_cust

    def transform_products(self, raw_products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Chuẩn hóa dữ liệu sản phẩm."""
        cleaned_prods = []
        for row in raw_products:
            cost = float(row["CostPrice"])
            list_p = float(row["ListPrice"])
            standard_margin = ((list_p - cost) / list_p * 100.0) if list_p > 0 else 0.0
            cleaned_prods.append({
                "ProductID": row["ProductID"].strip(),
                "ProductName": row["ProductName"].strip(),
                "Category": row["Category"].strip(),
                "Subcategory": row["Subcategory"].strip(),
                "CostPrice": cost,
                "ListPrice": list_p,
                "TargetMarginPct": round(standard_margin, 2),
                "Supplier": row["Supplier"].strip()
            })
        return cleaned_prods

    def execute(self, raw_dir: str = "data/raw", out_dir: str = "data/processed") -> Dict[str, Any]:
        """Thực thi pipeline ETL đầy đủ và lưu ra thư mục data/processed."""
        os.makedirs(out_dir, exist_ok=True)
        try:
            from skills.skill_2_data_ingestion import DataIngestionSkill
        except ImportError:
            from skill_2_data_ingestion import DataIngestionSkill
        ingestor = DataIngestionSkill()

        raw_sales = ingestor.read_csv_file(os.path.join(raw_dir, "raw_sales_transactions.csv"))
        raw_custs = ingestor.read_csv_file(os.path.join(raw_dir, "raw_customers.csv"))
        raw_prods = ingestor.read_csv_file(os.path.join(raw_dir, "raw_products.csv"))

        cleaned_sales = self.transform_sales(raw_sales)
        cleaned_custs = self.transform_customers(raw_custs)
        cleaned_prods = self.transform_products(raw_prods)

        # Lưu processed sales
        sales_out = os.path.join(out_dir, "processed_sales_transactions.csv")
        with open(sales_out, "w", newline="", encoding="utf-8") as f:
            if cleaned_sales:
                writer = csv.DictWriter(f, fieldnames=list(cleaned_sales[0].keys()))
                writer.writeheader()
                writer.writerows(cleaned_sales)

        # Lưu processed customers
        cust_out = os.path.join(out_dir, "processed_customers.csv")
        with open(cust_out, "w", newline="", encoding="utf-8") as f:
            if cleaned_custs:
                writer = csv.DictWriter(f, fieldnames=list(cleaned_custs[0].keys()))
                writer.writeheader()
                writer.writerows(cleaned_custs)

        # Lưu processed products
        prod_out = os.path.join(out_dir, "processed_products.csv")
        with open(prod_out, "w", newline="", encoding="utf-8") as f:
            if cleaned_prods:
                writer = csv.DictWriter(f, fieldnames=list(cleaned_prods[0].keys()))
                writer.writeheader()
                writer.writerows(cleaned_prods)

        return {
            "status": "SUCCESS",
            "sales_processed": len(cleaned_sales),
            "customers_processed": len(cleaned_custs),
            "products_processed": len(cleaned_prods),
            "output_directory": out_dir
        }

if __name__ == "__main__":
    etl = ETLPipelineSkill()
    res = etl.execute()
    print("Skill 4 Output Summary:")
    print(f"- Processed Sales: {res['sales_processed']} rows")
    print(f"- Processed Customers: {res['customers_processed']} rows")
    print(f"- Processed Products: {res['products_processed']} rows")
