"""
Pipeline Step 5: Classify Failures

Classifies failures from explicit evidence only.
Per contract, NEVER infers failures from absence of "success" text.

Sources of failure evidence:
- Explicit audit outputs with exit codes
- Explicit schema validator outputs
- Missing or malformed required artifacts
- Invalid seal
- Malformed run envelope
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any

from .load_run import RunContext
from .detect_seal import SealStatus
from .scan_artifacts import ArtifactEntry
from .parse_artifacts import ParsedArtifact, ParseResult


@dataclass
class EvidenceRef:
    """Reference to source evidence."""
    artifact_path: str
    source_check_id: Optional[str] = None
    rule_id: Optional[str] = None
    line_number: Optional[int] = None
    excerpt: Optional[str] = None


@dataclass
class Failure:
    """A classified failure."""
    failure_id: str
    failure_class: str  # SEAL_INVALID, RUN_ENVELOPE_MALFORMED, AUDIT_FAILED, ARTIFACT_MISSING, ARTIFACT_MALFORMED, SCHEMA_VIOLATION, EVIDENCE_INCOMPLETE, UNKNOWN
    severity: str       # CRITICAL, ERROR, WARNING, INFO
    confidence: str     # HIGH, MEDIUM, LOW, NONE
    description: str
    evidence_refs: List[EvidenceRef]


@dataclass
class NonClaim:
    """A claim that was withheld due to insufficient evidence."""
    non_claim_id: str
    reason: str  # EVIDENCE_MISSING, EVIDENCE_AMBIGUOUS, PARSE_FAILURE, OUT_OF_SCOPE
    description: str
    attempted_artifact: Optional[str] = None


@dataclass
class NextAction:
    """A recommended next action."""
    action_id: str
    action_type: str  # INVESTIGATE, REMEDIATE, DOCUMENT, ESCALATE, NONE
    description: str
    priority: str     # P0, P1, P2, P3
    related_failure_ids: List[str] = field(default_factory=list)


@dataclass
class ClassificationResult:
    """Result of failure classification."""
    failures: List[Failure]
    non_claims: List[NonClaim]
    next_actions: List[NextAction]
    overall_confidence: str


def classify_seal_failures(seal_status: SealStatus) -> List[Failure]:
    """Classify failures from seal status."""
    failures = []

    if seal_status.is_sealed and not seal_status.seal_valid:
        # Invalid seal is CRITICAL
        evidence_refs = []

        if seal_status.manifest_json_present:
            evidence_refs.append(EvidenceRef(
                artifact_path="manifest.json",
                source_check_id="seal_validation"
            ))

        if seal_status.manifest_sha256_present:
            evidence_refs.append(EvidenceRef(
                artifact_path="MANIFEST.sha256",
                source_check_id="seal_validation"
            ))

        description_parts = ["Seal validation failed."]
        if seal_status.hash_mismatches:
            description_parts.append(f"Hash mismatches: {len(seal_status.hash_mismatches)}")
            # Add first mismatch as excerpt
            if evidence_refs and seal_status.hash_mismatches:
                evidence_refs[0].excerpt = seal_status.hash_mismatches[0][:500]

        failures.append(Failure(
            failure_id="F-SEAL-001",
            failure_class="SEAL_INVALID",
            severity="CRITICAL",
            confidence="HIGH",
            description=" ".join(description_parts),
            evidence_refs=evidence_refs if evidence_refs else [EvidenceRef(artifact_path="MANIFEST.sha256")]
        ))

    return failures


def classify_envelope_failures(context: RunContext) -> List[Failure]:
    """Classify failures from run envelope validation."""
    failures = []

    for error in context.load_errors:
        if "RUN_ENVELOPE_MALFORMED" in error:
            failures.append(Failure(
                failure_id=f"F-ENV-{len(failures)+1:03d}",
                failure_class="RUN_ENVELOPE_MALFORMED",
                severity="CRITICAL",
                confidence="HIGH",
                description=error,
                evidence_refs=[EvidenceRef(
                    artifact_path="run.json",
                    source_check_id="envelope_validation",
                    excerpt=error[:500]
                )]
            ))

    return failures


def classify_artifact_failures(
    artifacts: List[ArtifactEntry],
    parse_result: ParseResult
) -> List[Failure]:
    """Classify failures from artifact scanning and parsing."""
    failures = []

    # Check for missing required artifacts
    required_artifacts = {"run.json"}
    found_artifacts = {a.artifact_path for a in artifacts}

    for required in required_artifacts:
        if required not in found_artifacts:
            failures.append(Failure(
                failure_id=f"F-ART-{len(failures)+1:03d}",
                failure_class="ARTIFACT_MISSING",
                severity="CRITICAL",
                confidence="HIGH",
                description=f"Required artifact missing: {required}",
                evidence_refs=[EvidenceRef(
                    artifact_path=required,
                    source_check_id="artifact_scan"
                )]
            ))

    # Check for parse failures
    for error in parse_result.parse_failures:
        # Extract artifact path from error message
        match = re.match(r"ARTIFACT_MALFORMED: ([^:]+):", error)
        artifact_path = match.group(1) if match else "unknown"

        failures.append(Failure(
            failure_id=f"F-ART-{len(failures)+1:03d}",
            failure_class="ARTIFACT_MALFORMED",
            severity="ERROR",
            confidence="HIGH",
            description=error,
            evidence_refs=[EvidenceRef(
                artifact_path=artifact_path,
                source_check_id="artifact_parse",
                excerpt=error[:500]
            )]
        ))

    return failures


def classify_audit_failures(
    context: RunContext,
    parse_result: ParseResult
) -> List[Failure]:
    """
    Classify failures from explicit audit outputs.

    IMPORTANT: Only classify from EXPLICIT evidence.
    Phase 3 audit exit codes: 0=PASS, 1=FAIL, 2=ERROR
    Look for explicit "AUDIT RESULT: FAIL" or similar patterns.
    """
    failures = []

    # Patterns indicating explicit audit failure
    audit_fail_patterns = [
        r"AUDIT RESULT:\s*FAIL",
        r"AUDIT_RESULT=FAIL",
        r"exit[_\s]*code[:\s]*1\b",
        r"exit[_\s]*code[:\s]*2\b",
        r"FAIL.*violations.*detected",
        r"Total violations:\s*[1-9]",
    ]

    for artifact_path, parsed in parse_result.parsed.items():
        if parsed.artifact_type != "audit_output":
            continue

        if parsed.parse_status != "SUCCESS":
            continue

        content = parsed.content
        if content is None:
            continue

        # Convert content to searchable text
        if isinstance(content, list):
            # Text file as lines
            text = "\n".join(str(line) for line in content)
        elif isinstance(content, dict):
            # JSON audit output - look for status fields
            text = str(content)
        else:
            text = str(content)

        # Search for explicit failure patterns
        for pattern in audit_fail_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Extract line number if content is lines
                line_number = None
                excerpt = match.group(0)

                if isinstance(content, list):
                    for i, line in enumerate(content, 1):
                        if re.search(pattern, str(line), re.IGNORECASE):
                            line_number = i
                            excerpt = str(line)[:500]
                            break

                failures.append(Failure(
                    failure_id=f"F-AUD-{len(failures)+1:03d}",
                    failure_class="AUDIT_FAILED",
                    severity="ERROR",
                    confidence="HIGH",
                    description=f"Audit failure detected in {artifact_path}",
                    evidence_refs=[EvidenceRef(
                        artifact_path=artifact_path,
                        source_check_id="audit_output_scan",
                        line_number=line_number,
                        excerpt=excerpt
                    )]
                ))
                break  # One failure per artifact

    return failures


def build_non_claims(
    seal_status: SealStatus,
    artifacts: List[ArtifactEntry],
    parse_result: ParseResult,
    strict_mode: bool
) -> List[NonClaim]:
    """
    Build non-claims for evidence that could not support claims.

    - Missing evidence → EVIDENCE_MISSING
    - Ambiguous evidence → EVIDENCE_AMBIGUOUS
    - Parse failure → PARSE_FAILURE
    - Out-of-scope artifacts → OUT_OF_SCOPE (strict mode)
    """
    non_claims = []
    nc_id = 1

    # Non-sealed runs: cannot claim seal validity
    if not seal_status.is_sealed:
        non_claims.append(NonClaim(
            non_claim_id=f"NC-{nc_id:03d}",
            reason="EVIDENCE_MISSING",
            description="Seal status could not be verified; manifest.json or MANIFEST.sha256 not present.",
            attempted_artifact="manifest.json" if not seal_status.manifest_json_present else "MANIFEST.sha256"
        ))
        nc_id += 1

    # Parse failures
    for artifact_path, parsed in parse_result.parsed.items():
        if parsed.parse_status == "PARSE_ERROR":
            non_claims.append(NonClaim(
                non_claim_id=f"NC-{nc_id:03d}",
                reason="PARSE_FAILURE",
                description=f"Artifact could not be parsed: {parsed.parse_error}",
                attempted_artifact=artifact_path
            ))
            nc_id += 1

    # Out-of-scope artifacts (strict mode)
    if strict_mode:
        for artifact in artifacts:
            if artifact.artifact_type == "other":
                non_claims.append(NonClaim(
                    non_claim_id=f"NC-{nc_id:03d}",
                    reason="OUT_OF_SCOPE",
                    description=f"Artifact type not recognized; no interpretation attempted.",
                    attempted_artifact=artifact.artifact_path
                ))
                nc_id += 1

    return non_claims


def build_next_actions(failures: List[Failure]) -> List[NextAction]:
    """Build recommended next actions based on failures."""
    actions = []
    action_id = 1

    # Group failures by class for action recommendations
    failure_by_class: Dict[str, List[Failure]] = {}
    for f in failures:
        failure_by_class.setdefault(f.failure_class, []).append(f)

    # SEAL_INVALID -> INVESTIGATE P0
    if "SEAL_INVALID" in failure_by_class:
        actions.append(NextAction(
            action_id=f"A-{action_id:03d}",
            action_type="INVESTIGATE",
            description="Investigate seal integrity failure. Verify manifest hashes match actual file contents.",
            priority="P0",
            related_failure_ids=[f.failure_id for f in failure_by_class["SEAL_INVALID"]]
        ))
        action_id += 1

    # RUN_ENVELOPE_MALFORMED -> REMEDIATE P0
    if "RUN_ENVELOPE_MALFORMED" in failure_by_class:
        actions.append(NextAction(
            action_id=f"A-{action_id:03d}",
            action_type="REMEDIATE",
            description="Fix run envelope structure. Ensure all required fields are present in run.json.",
            priority="P0",
            related_failure_ids=[f.failure_id for f in failure_by_class["RUN_ENVELOPE_MALFORMED"]]
        ))
        action_id += 1

    # AUDIT_FAILED -> INVESTIGATE P1
    if "AUDIT_FAILED" in failure_by_class:
        actions.append(NextAction(
            action_id=f"A-{action_id:03d}",
            action_type="INVESTIGATE",
            description="Review audit failures and remediate underlying issues.",
            priority="P1",
            related_failure_ids=[f.failure_id for f in failure_by_class["AUDIT_FAILED"]]
        ))
        action_id += 1

    # ARTIFACT_MISSING -> INVESTIGATE P1
    if "ARTIFACT_MISSING" in failure_by_class:
        actions.append(NextAction(
            action_id=f"A-{action_id:03d}",
            action_type="INVESTIGATE",
            description="Locate or regenerate missing artifacts.",
            priority="P1",
            related_failure_ids=[f.failure_id for f in failure_by_class["ARTIFACT_MISSING"]]
        ))
        action_id += 1

    # ARTIFACT_MALFORMED -> INVESTIGATE P2
    if "ARTIFACT_MALFORMED" in failure_by_class:
        actions.append(NextAction(
            action_id=f"A-{action_id:03d}",
            action_type="INVESTIGATE",
            description="Review malformed artifacts and determine root cause.",
            priority="P2",
            related_failure_ids=[f.failure_id for f in failure_by_class["ARTIFACT_MALFORMED"]]
        ))
        action_id += 1

    return actions


def compute_overall_confidence(
    failures: List[Failure],
    non_claims: List[NonClaim]
) -> str:
    """
    Compute overall confidence.

    Confidence = minimum confidence across contributing factors.
    """
    if not failures and not non_claims:
        return "HIGH"

    confidence_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "NONE": 3}
    min_confidence = "HIGH"

    for f in failures:
        if confidence_order.get(f.confidence, 3) > confidence_order[min_confidence]:
            min_confidence = f.confidence

    # Non-claims with EVIDENCE_AMBIGUOUS reduce confidence
    for nc in non_claims:
        if nc.reason == "EVIDENCE_AMBIGUOUS":
            if confidence_order["MEDIUM"] > confidence_order[min_confidence]:
                min_confidence = "MEDIUM"

    return min_confidence


def classify_failures(
    context: RunContext,
    seal_status: SealStatus,
    artifacts: List[ArtifactEntry],
    parse_result: ParseResult,
    strict_mode: bool = False
) -> ClassificationResult:
    """
    Main entry point: Classify all failures from explicit evidence.

    Uses ONLY these sources:
    - Explicit audit outputs
    - Explicit schema validator outputs
    - Missing or malformed required artifacts
    - Invalid seal
    - Malformed run envelope

    NEVER infers failures from absence of "success" text.
    """
    failures = []

    # 1. Seal failures
    failures.extend(classify_seal_failures(seal_status))

    # 2. Envelope failures
    failures.extend(classify_envelope_failures(context))

    # 3. Artifact failures
    failures.extend(classify_artifact_failures(artifacts, parse_result))

    # 4. Audit failures
    failures.extend(classify_audit_failures(context, parse_result))

    # Build non-claims
    non_claims = build_non_claims(seal_status, artifacts, parse_result, strict_mode)

    # Build next actions
    next_actions = build_next_actions(failures)

    # Compute overall confidence
    overall_confidence = compute_overall_confidence(failures, non_claims)

    return ClassificationResult(
        failures=failures,
        non_claims=non_claims,
        next_actions=next_actions,
        overall_confidence=overall_confidence
    )
