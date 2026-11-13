"""
Lane 2: Nhân viên PTKD (Human-in-the-Loop)
- Task 2.1: Kiểm tra chéo 20-30% mẫu trích dẫn gốc (Doc_ID Verification)
- Gateway 2: Xác nhận dữ liệu & ngữ cảnh có khớp hay không
- Task 2.2: Hiệu chỉnh tham số & Ghi Audit Log không thể tẩy xóa
"""

import random
import json
import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple
from src.models import (
    ProvinceScoreResult,
    AuditSampleItem,
    AuditLogEntry,
)
from src.paths import get_artifacts_dir


class PTKDAuditModule:
    def __init__(self, sample_ratio: float = 0.25):
        self.sample_ratio = sample_ratio

    def generate_audit_sample(self, score_results: List[ProvinceScoreResult]) -> List[AuditSampleItem]:
        """
        Extracts 20-30% randomized sample from all criteria citations across provinces.
        """
        all_citations: List[Tuple[str, Any]] = []
        for prov_res in score_results:
            for crit in prov_res.criteria_scores:
                all_citations.append((prov_res.province, crit))

        sample_size = max(2, int(len(all_citations) * self.sample_ratio))
        # Deterministic seed if needed or randomized
        sampled_pairs = random.sample(all_citations, min(sample_size, len(all_citations)))

        audit_samples: List[AuditSampleItem] = []
        for i, (prov, crit) in enumerate(sampled_pairs, 1):
            item = AuditSampleItem(
                sample_id=f"AUDIT-SMP-{i:03d}",
                province=prov,
                criterion_id=crit.criterion_id,
                criterion_name=crit.criterion_name,
                score_assigned=crit.raw_score,
                doc_id=crit.doc_id,
                citation_quote=crit.citation_quote,
                source_title=crit.data_source_title,
                verified=False,
                mismatch_detected=False,
                human_notes=""
            )
            audit_samples.append(item)

        # Save artifact audit_sample_queue.json
        artifacts_dir = get_artifacts_dir()
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        sample_path = artifacts_dir / "audit_sample_queue.json"

        with open(sample_path, "w", encoding="utf-8") as f:
            json.dump([item.__dict__ for item in audit_samples], f, ensure_ascii=False, indent=2)

        return audit_samples

    def record_manual_override(
        self,
        actor: str,
        target_province: str,
        criterion_id: str,
        previous_value: float,
        new_value: float,
        justification: str,
        state: Dict[str, Any]
    ) -> AuditLogEntry:
        """
        Task 2.2: Logs manual parameter modification to immutable audit log.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = AuditLogEntry(
            log_id=f"LOG-{int(datetime.datetime.now().timestamp())}",
            timestamp=timestamp,
            actor=actor,
            action="SCORE_OVERRIDE",
            target_province=target_province,
            field_affected=f"criteria_score:{criterion_id}",
            previous_value=previous_value,
            new_value=new_value,
            justification=justification
        )

        # Append to state audit trail
        if "audit_logs" not in state:
            state["audit_logs"] = []
        state["audit_logs"].append(log_entry.__dict__)

        # Update parameter overrides in state
        if "parameter_overrides" not in state:
            state["parameter_overrides"] = {"score_overrides": {}, "weights": {}}
        if "score_overrides" not in state["parameter_overrides"]:
            state["parameter_overrides"]["score_overrides"] = {}
        if criterion_id not in state["parameter_overrides"]["score_overrides"]:
            state["parameter_overrides"]["score_overrides"][criterion_id] = {}

        state["parameter_overrides"]["score_overrides"][criterion_id][target_province] = new_value

        # Persist audit_log.json
        artifacts_dir = get_artifacts_dir()
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        log_path = artifacts_dir / "audit_log.json"

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(state["audit_logs"], f, ensure_ascii=False, indent=2)

        return log_entry

