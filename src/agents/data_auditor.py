"""
Task 1.1: Data Auditor Agent
Scans raw market data, deduplicates secondary copycat sources, normalizes baseline year to 2026,
and assigns canonical Doc_IDs with cryptographic verification hashes.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from src.agents.base_agent import BaseWorkflowAgent
from src.models import CleanDataRecord
from src.paths import get_artifacts_dir


class DataAuditorAgent(BaseWorkflowAgent):
    def __init__(self, baseline_year: int = 2026):
        super().__init__(
            name="DataAuditorAgent",
            role="Task 1.1: Chuẩn hóa kỳ thống kê & Khử trùng lặp nguồn dữ liệu gốc"
        )
        self.baseline_year = baseline_year

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        self.log(f"Bắt đầu Task 1.1: Quét và tiền xử lý gói dữ liệu thị trường (Năm cơ sở: {self.baseline_year})...")
        raw_items = state.get("raw_market_data", [])
        clean_records: List[CleanDataRecord] = []
        discarded_items: List[Dict[str, Any]] = []

        seen_provinces = set()

        for item in raw_items:
            source_type = item.get("source_type", "secondary").lower()
            province = item.get("province")

            # Rule: Strict deduplication - Only retain primary source per province
            if source_type != "primary":
                discarded_items.append({
                    "raw_id": item.get("raw_id"),
                    "province": province,
                    "reason": f"Nguồn thứ cấp/sao chép ({item.get('publisher')}). Ghi chú: {item.get('notes', 'Không phải nguồn gốc')}"
                })
                self.log(f"Loại bỏ dữ liệu thứ cấp/trùng lặp: {item.get('raw_id')} ({province})")
                continue

            if province in seen_provinces:
                discarded_items.append({
                    "raw_id": item.get("raw_id"),
                    "province": province,
                    "reason": "Phát hiện bản ghi sơ cấp trùng lặp thứ hai cho cùng địa bàn."
                })
                continue

            seen_provinces.add(province)
            pub_year = item.get("publication_year", self.baseline_year)
            metrics = dict(item.get("metrics", {}))

            # Normalize metrics to baseline year if published earlier
            if pub_year < self.baseline_year:
                years_diff = self.baseline_year - pub_year
                annual_growth = metrics.get("growth_rate_pct", 10.0) / 100.0
                growth_factor = (1.0 + annual_growth) ** years_diff

                if "retail_chain_count" in metrics:
                    original_val = metrics["retail_chain_count"]
                    normalized_val = round(original_val * growth_factor)
                    metrics["retail_chain_count"] = normalized_val
                    metrics["_normalized_note"] = f"Quy đổi từ {pub_year} ({original_val} chuỗi) sang {self.baseline_year} (+{annual_growth*100}%/năm) = {normalized_val} chuỗi"

            doc_id = item.get("doc_id") or f"DOC-HP-RAW-{len(clean_records)+1:03d}"

            record = CleanDataRecord(
                doc_id=doc_id,
                raw_id=item.get("raw_id", "UNKNOWN"),
                province=province,
                source_title=item.get("source_title", "N/A"),
                publisher=item.get("publisher", "N/A"),
                publication_year=pub_year,
                normalized_year=self.baseline_year,
                metrics=metrics,
                direct_quote=item.get("direct_quote", ""),
                source_type="primary"
            )
            clean_records.append(record)
            self.log(f"Đã chuẩn hóa & cấp Doc_ID: [{doc_id}] cho địa bàn {province} (Nguồn: {record.publisher})")

        # Save artifact clean_dataset.json
        artifacts_dir = get_artifacts_dir()
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        clean_dataset_path = artifacts_dir / "clean_dataset.json"

        artifact_data = {
            "baseline_year": self.baseline_year,
            "total_raw_scanned": len(raw_items),
            "clean_records_count": len(clean_records),
            "discarded_count": len(discarded_items),
            "discarded_summary": discarded_items,
            "records": [
                {
                    "doc_id": r.doc_id,
                    "raw_id": r.raw_id,
                    "province": r.province,
                    "publisher": r.publisher,
                    "publication_year": r.publication_year,
                    "normalized_year": r.normalized_year,
                    "metrics": r.metrics,
                    "direct_quote": r.direct_quote,
                    "verification_hash": r.verification_hash
                }
                for r in clean_records
            ]
        }

        with open(clean_dataset_path, "w", encoding="utf-8") as f:
            json.dump(artifact_data, f, ensure_ascii=False, indent=2)

        self.log(f"Hoàn tất Task 1.1: {len(clean_records)} địa bàn chuẩn hóa, loại bỏ {len(discarded_items)} bản ghi trùng lặp.")
        self.log(f"Artifact lưu tại: {clean_dataset_path}")

        # Return updated state
        return {
            "clean_dataset": clean_records,
            "clean_dataset_artifact": str(clean_dataset_path),
            "discarded_data": discarded_items
        }

