"""
Pipeline Step 6: Build Report

Builds the canonical JSON report conforming to AUDIT_INTERPRETATION_REPORT_v0.1.json schema.

Overall Status Precedence (documented):
    1. UNKNOWN dominates if seal is invalid OR any EVIDENCE_INCOMPLETE failure exists
    2. Else FAIL if any CRITICAL or ERROR severity failures exist
    3. Else PASS if no failures exist (warnings only do not cause FAIL)
"""

import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from .load_run import RunContext
from .detect_seal import SealStatus
from .scan_artifacts import ArtifactEntry
from .classify_failures import ClassificationResult, Failure, NonClaim, NextAction, EvidenceRef


# Schema constants
SCHEMA_VERSION = "0.1"
INTERPRETER_VERSION = "0.1"
CONTRACT_VERSION = "AGENT_AUDIT_INTERPRETER_CONTRACT_v0.1"
AUTHORITY_STATEMENT = "NON-AUTHORITATIVE: This report is derived and does not constitute source truth."


def compute_deterministic_suffix(
    run_id: str,
    schema_version: str,
    interpreter_version: str,
    evidence_index: List[Dict[str, Any]]
) -> str:
    """
    Compute a deterministic 8-hex suffix for report_id.

    Derived from stable hash of:
      - run_id
      - schema_version
      - interpreter_version
      - sorted list of evidence_index entries (artifact_path + sha256 or read_status)

    Returns first 8 hex characters of SHA256 digest.
    """
    hasher = hashlib.sha256()

    # Add fixed components
    hasher.update(run_id.encode('utf-8'))
    hasher.update(schema_version.encode('utf-8'))
    hasher.update(interpreter_version.encode('utf-8'))

    # Sort evidence_index by artifact_path for determinism
    sorted_evidence = sorted(evidence_index, key=lambda e: e.get("artifact_path", ""))

    for entry in sorted_evidence:
        artifact_path = entry.get("artifact_path", "")
        sha256 = entry.get("sha256")
        read_status = entry.get("read_status", "")

        hasher.update(artifact_path.encode('utf-8'))
        if sha256:
            hasher.update(sha256.encode('utf-8'))
        else:
            hasher.update(read_status.encode('utf-8'))

    return hasher.hexdigest()[:8]


def generate_report_id(
    run_id: str,
    schema_version: str,
    interpreter_version: str,
    evidence_index: List[Dict[str, Any]],
    generated_utc: datetime
) -> str:
    """
    Generate a deterministic report ID.

    Format: AIR-YYYYMMDDTHHMMSSZ-<8 hex chars>

    The timestamp comes from generated_utc.
    The 8-hex suffix is deterministically derived from run_id, schema_version,
    interpreter_version, and sorted evidence_index entries.
    """
    timestamp = generated_utc.strftime("%Y%m%dT%H%M%SZ")
    suffix = compute_deterministic_suffix(
        run_id, schema_version, interpreter_version, evidence_index
    )
    return f"AIR-{timestamp}-{suffix}"


def build_seal_status_section(seal_status: SealStatus) -> Dict[str, Any]:
    """Build seal_status section of report."""
    return {
        "is_sealed": seal_status.is_sealed,
        "seal_valid": seal_status.seal_valid,
        "root_sha256": seal_status.root_sha256
    }


def build_interpretation_summary(
    failures: List[Failure],
    overall_confidence: str
) -> Dict[str, Any]:
    """
    Build interpretation_summary section.

    Overall Status Precedence:
        1. UNKNOWN dominates if seal is invalid OR any EVIDENCE_INCOMPLETE failure exists
        2. Else FAIL if any CRITICAL or ERROR severity failures exist
        3. Else PASS if no failures exist (warnings only do not cause FAIL)
    """
    failure_count = len(failures)
    warning_count = sum(1 for f in failures if f.severity == "WARNING")

    # Determine overall status using documented precedence
    has_critical = any(f.severity == "CRITICAL" for f in failures)
    has_error = any(f.severity == "ERROR" for f in failures)
    has_seal_invalid = any(f.failure_class == "SEAL_INVALID" for f in failures)
    has_evidence_incomplete = any(f.failure_class == "EVIDENCE_INCOMPLETE" for f in failures)

    # Precedence 1: UNKNOWN dominates if seal invalid or evidence incomplete
    if has_seal_invalid or has_evidence_incomplete:
        overall_status = "UNKNOWN"
    # Precedence 2: FAIL if any CRITICAL or ERROR failures
    elif has_critical or has_error:
        overall_status = "FAIL"
    # Precedence 3: PASS otherwise (warnings only do not cause FAIL)
    else:
        overall_status = "PASS"

    return {
        "overall_status": overall_status,
        "failure_count": failure_count,
        "warning_count": warning_count,
        "confidence": overall_confidence
    }


def build_evidence_ref(ref: EvidenceRef) -> Dict[str, Any]:
    """Build an evidence_ref object."""
    return {
        "artifact_path": ref.artifact_path,
        "source_check_id": ref.source_check_id,
        "rule_id": ref.rule_id,
        "line_number": ref.line_number,
        "excerpt": ref.excerpt[:500] if ref.excerpt else None
    }


def build_failure_entry(failure: Failure) -> Dict[str, Any]:
    """Build a failure entry for the report."""
    return {
        "failure_id": failure.failure_id,
        "failure_class": failure.failure_class,
        "severity": failure.severity,
        "confidence": failure.confidence,
        "description": failure.description,
        "evidence_refs": [build_evidence_ref(ref) for ref in failure.evidence_refs]
    }


def build_non_claim_entry(non_claim: NonClaim) -> Dict[str, Any]:
    """Build a non_claim entry for the report."""
    return {
        "non_claim_id": non_claim.non_claim_id,
        "reason": non_claim.reason,
        "description": non_claim.description,
        "attempted_artifact": non_claim.attempted_artifact
    }


def build_next_action_entry(action: NextAction) -> Dict[str, Any]:
    """Build a next_action entry for the report."""
    return {
        "action_id": action.action_id,
        "action_type": action.action_type,
        "description": action.description,
        "priority": action.priority,
        "related_failure_ids": action.related_failure_ids
    }


def build_evidence_index(artifacts: List[ArtifactEntry]) -> List[Dict[str, Any]]:
    """Build evidence_index section from scanned artifacts."""
    entries = []

    for artifact in artifacts:
        entries.append({
            "artifact_path": artifact.artifact_path,
            "artifact_type": artifact.artifact_type,
            "read_status": artifact.read_status,
            "sha256": artifact.sha256
        })

    return entries


def build_report(
    context: RunContext,
    seal_status: SealStatus,
    artifacts: List[ArtifactEntry],
    classification: ClassificationResult,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point: Build the canonical interpretation report.

    MUST conform exactly to AUDIT_INTERPRETATION_REPORT_v0.1.json schema.
    """
    now = datetime.now(timezone.utc)

    # Build evidence_index first (needed for deterministic report_id)
    evidence_index = build_evidence_index(artifacts)

    # Generate deterministic report_id
    report_id = generate_report_id(
        run_id=context.run_id,
        schema_version=SCHEMA_VERSION,
        interpreter_version=INTERPRETER_VERSION,
        evidence_index=evidence_index,
        generated_utc=now
    )

    report = {
        "schema_version": SCHEMA_VERSION,
        "report_id": report_id,
        "generated_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "interpreter_version": INTERPRETER_VERSION,
        "run_id": context.run_id,
        "run_type": context.run_type,
        "run_created_utc": context.run_created_utc,
        "seal_status": build_seal_status_section(seal_status),
        "interpretation_summary": build_interpretation_summary(
            classification.failures,
            classification.overall_confidence
        ),
        "failures": [build_failure_entry(f) for f in classification.failures],
        "non_claims": [build_non_claim_entry(nc) for nc in classification.non_claims],
        "next_actions": [build_next_action_entry(a) for a in classification.next_actions],
        "evidence_index": evidence_index,
        "metadata": {
            "contract_version": CONTRACT_VERSION,
            "authority_statement": AUTHORITY_STATEMENT,
            "notes": notes
        }
    }

    return report
