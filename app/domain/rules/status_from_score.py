from app.domain.enum.candidate_status import CandidateStatus

APPROVAL_THRESHOLD = 0.7


def status_from_score(score: float) -> CandidateStatus:
    return CandidateStatus.APPROVED if score >= APPROVAL_THRESHOLD else CandidateStatus.REJECTED