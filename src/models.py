"""
Data models and schemas for Hưng Phát Market Expansion Multi-Agent System.
Strict adherence to BPMN 2.0 specifications with 100% auditability & Doc_ID citations.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional
import datetime
import uuid


class DataSourceType(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"


class HurdleStatus(str, Enum):
    PASS = "PASS"
    FAIL_CAPACITY = "FAIL_CAPACITY"


class StepStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    WAITING_HUMAN_AUDIT = "WAITING_HUMAN_AUDIT"
    WAITING_MANAGER_REVIEW = "WAITING_MANAGER_REVIEW"


@dataclass
class CleanDataRecord:
    doc_id: str
    raw_id: str
    province: str
    source_title: str
    publisher: str
    publication_year: int
    normalized_year: int
    metrics: Dict[str, Any]
    direct_quote: str
    source_type: str = "primary"
    verification_hash: str = ""

    def __post_init__(self):
        if not self.verification_hash:
            # Deterministic hash for 100% auditability
            content = f"{self.doc_id}:{self.province}:{self.normalized_year}:{self.source_title}"
            self.verification_hash = str(uuid.uuid5(uuid.NAMESPACE_DNS, content))[:12]


@dataclass
class FitFeasibilityRecord:
    province: str
    doc_id_market: str
    doc_id_feedback: str
    feature_match_pct: float
    switching_barrier: str
    readiness_score: float
    distance_km: float
    travel_time_hours: float
    meets_direct_sla: bool
    hurdle_status: HurdleStatus
    rationale: str
    assigned_hub: Optional[str] = None


@dataclass
class CostToServeRecord:
    province: str
    is_capped: bool
    score_cap: float
    outsourced_partner_monthly_vnd: float
    quarterly_trip_vnd: float
    annual_extra_cost_vnd: float
    margin_impact_pct: float
    mitigation_strategy: str


@dataclass
class CriterionScoreItem:
    criterion_id: str
    criterion_name: str
    weight: float
    raw_score: float  # 0 - 100
    weighted_score: float
    doc_id: str
    citation_quote: str
    data_source_title: str


@dataclass
class ProvinceScoreResult:
    province: str
    rank: int = 0
    raw_composite_score: float = 0.0
    is_score_capped: bool = False
    score_cap: Optional[float] = None
    final_score: float = 0.0
    criteria_scores: List[CriterionScoreItem] = field(default_factory=list)
    cost_to_serve_flag: bool = False
    notes: str = ""


@dataclass
class AuditSampleItem:
    sample_id: str
    province: str
    criterion_id: str
    criterion_name: str
    score_assigned: float
    doc_id: str
    citation_quote: str
    source_title: str
    verified: bool = False
    mismatch_detected: bool = False
    human_notes: str = ""


@dataclass
class AuditLogEntry:
    log_id: str
    timestamp: str
    actor: str  # e.g., 'PTKD_Auditor', 'BD_Manager', 'AI_System'
    action: str  # e.g., 'SAMPLE_VERIFIED', 'SCORE_OVERRIDE', 'WEIGHT_ADJUST', 'MANAGER_APPROVE'
    target_province: str
    field_affected: str
    previous_value: Any
    new_value: Any
    justification: str


@dataclass
class SurveyQuestion:
    question_id: str
    province: str
    category: str
    question_text: str
    target_respondent: str
    blindspot_addressed: str
    priority: str  # HIGH, MEDIUM


@dataclass
class BODProposalReport:
    report_id: str
    generated_at: str
    company_name: str
    solution_name: str
    selected_provinces: List[str]
    executive_summary: str
    detailed_provinces: List[Dict[str, Any]]
    survey_agenda: List[SurveyQuestion]
    audit_trail_summary: Dict[str, Any]
    approval_status: str = "PENDING_BOD_SUBMISSION"
    signed_by: Optional[str] = None
    sign_off_date: Optional[str] = None

