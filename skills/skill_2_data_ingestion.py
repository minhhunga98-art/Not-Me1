"""
Skill 2: Data Ingestion Skill
Tiếp nhận và nạp dữ liệu từ các tệp CSV, Excel, JSON.
Tự động nhận diện cấu trúc cột, phân tích định dạng dữ liệu ban đầu và số lượng bản ghi.
"""

import os
import csv
import json
from typing import Dict, Any, List

class DataIngestionSkill:
    def __init__(self):
        self.skill_name = "Data Ingestion Skill"
        self.version = "1.0.0"

    def read_csv_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Đọc tệp CSV và trả về danh sách các bản ghi (dict)."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Tệp không tồn tại: {file_path}")
        
        records = []
        with open(file_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(dict(row))
        return records

    def profile_schema(self, records: List[Dict[str, Any]]) -> Dict[str, str]:
        """Tự động phân tích kiểu dữ liệu dự kiến của từng cột."""
        if not records:
            return {}
        
        sample_row = records[0]
        schema = {}
        for col, val in sample_row.items():
            # Kiểm tra kiểu
            val_str = str(val).strip()
            if val_str.isdigit() or (val_str.startswith('-') and val_str[1:].isdigit()):
                schema[col] = "INTEGER"
            else:
                try:
                    float(val_str)
                    schema[col] = "FLOAT"
                except ValueError:
                    if len(val_str) == 10 and val_str[4] == '-' and val_str[7] == '-':
                        schema[col] = "DATE"
                    else:
                        schema[col] = "STRING"
        return schema

    def execute(self, data_directory: str = "data/raw") -> Dict[str, Any]:
        """
        Nạp toàn bộ dữ liệu từ thư mục raw.
        """
        ingested_tables = {}
        summary = []

        files = [
            ("raw_products.csv", "Products"),
            ("raw_customers.csv", "Customers"),
            ("raw_sales_transactions.csv", "SalesTransactions"),
            ("raw_marketing_campaigns.csv", "MarketingCampaigns"),
            ("raw_operations_logistics.csv", "OperationsLogistics"),
            ("raw_financial_targets.csv", "FinancialTargets")
        ]

        for fname, table_alias in files:
            fpath = os.path.join(data_directory, fname)
            if os.path.exists(fpath):
                data = self.read_csv_file(fpath)
                schema = self.profile_schema(data)
                ingested_tables[table_alias] = {
                    "file_name": fname,
                    "record_count": len(data),
                    "columns": list(data[0].keys()) if data else [],
                    "detected_schema": schema,
                    "sample": data[:3] if data else []
                }
                summary.append({
                    "table": table_alias,
                    "file": fname,
                    "records": len(data),
                    "columns_count": len(schema)
                })
            else:
                ingested_tables[table_alias] = {"error": f"Tệp {fname} không tìm thấy."}

        return {
            "status": "SUCCESS",
            "ingested_count": len(summary),
            "summary": summary,
            "tables": ingested_tables
        }

if __name__ == "__main__":
    skill = DataIngestionSkill()
    res = skill.execute()
    print("Skill 2 Output Summary:")
    print(f"- Tables Ingested: {res['ingested_count']}")
    for s in res['summary']:
        print(f"  • {s['table']}: {s['records']} rows, {s['columns_count']} cols")
