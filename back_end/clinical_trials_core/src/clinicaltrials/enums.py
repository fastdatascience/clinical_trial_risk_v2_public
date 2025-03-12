from enum import Enum

from clinicaltrials.schemas import RiskThresholdsDict, Tertile
from clinicaltrials.utils import find_matching_tertile_by_priority


class TrialRiskLevel(Enum):
    LOW = "LOW"
    HIGH = "HIGH"

    # * Default category with no specific thresholds
    MEDIUM = "MEDIUM"

    def __init__(self, label: str):
        self.label = label

    @staticmethod
    def is_within_threshold(cost: float, risk_threshold: RiskThresholdsDict) -> "TrialRiskLevel":
        """
        Check if the given cost falls within the risk level's thresholds

        Args:
            cost (float): The cost to evaluate
            risk_threshold (RiskThresholdsDict): With 'low' and 'high' thresholds

        Returns:
            TrialRiskLevel: The corresponding risk level
        """

        if cost < risk_threshold.high:
            return TrialRiskLevel.HIGH
        if cost < risk_threshold.low:
            return TrialRiskLevel.MEDIUM

        return TrialRiskLevel.LOW


class TrialSize(Enum):
    SMALL = (0, "Small")
    MEDIUM = (1, "Medium")
    LARGE = (2, "Large")

    def __init__(self, id: int, label: str):
        self.id = id
        self.label = label

    def __str__(self):
        return self.label

    @classmethod
    def get_trial_size(cls, condition: str, phase: float, sample_size: int,
                       sample_size_tertiles: list[Tertile]) -> "TrialSize":
        """
        Determine the trial size based on condition, phase, and sample size

        Priority for matching:
            1. Exact condition and exact phase
            2. Wildcard condition and exact phase
            3. Exact condition and wildcard phase
            4. Wildcard condition and wildcard phase
        """

        # * Find the first matching tertile based on priority
        matching_tertile = find_matching_tertile_by_priority(
            priority=[(condition, phase), ("*", phase), (condition, "*"), ("*", "*")],
            tertiles=sample_size_tertiles,
        )

        # * Default to MEDIUM if no matching tertile is found
        if not matching_tertile:
            return cls.MEDIUM

        if sample_size < matching_tertile.lower_tertile:
            return cls.SMALL
        if sample_size < matching_tertile.upper_tertile:
            return cls.MEDIUM

        return cls.LARGE
