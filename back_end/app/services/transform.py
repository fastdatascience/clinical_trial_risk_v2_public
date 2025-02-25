from enum import Enum
from typing import Any

import numpy as np
from clinicaltrials.core import Metadata as ClinicalTrialMetadata
from pydantic import BaseModel

from app.models.weight_profile.base import RiskThresholdsDict, SampleSizeTertile, UserWeightProfile, WeightProfile, WeightProfileBase

# * List of low to medium income countries
LMIC_COUNTRIES = {
    "AF",
    "AL",
    "AM",
    "AO",
    "AR",
    "AS",
    "AZ",
    "BA",
    "BD",
    "BF",
    "BG",
    "BI",
    "BJ",
    "BO",
    "BR",
    "BT",
    "BW",
    "BY",
    "BZ",
    "CF",
    "CI",
    "CM",
    "CN",
    "CO",
    "CR",
    "CU",
    "CV",
    "DJ",
    "DM",
    "DO",
    "DZ",
    "EC",
    "ER",
    "ET",
    "FJ",
    "GA",
    "GD",
    "GE",
    "GH",
    "GN",
    "GQ",
    "GT",
    "GW",
    "GY",
    "HN",
    "HT",
    "ID",
    "IN",
    "IQ",
    "JM",
    "JO",
    "KE",
    "KH",
    "KI",
    "KM",
    "KZ",
    "LB",
    "LK",
    "LR",
    "LS",
    "LY",
    "MA",
    "MD",
    "ME",
    "MG",
    "MH",
    "MK",
    "ML",
    "MM",
    "MN",
    "MR",
    "MU",
    "MV",
    "MW",
    "MX",
    "MY",
    "MZ",
    "NA",
    "NE",
    "NG",
    "NI",
    "NP",
    "PA",
    "PE",
    "PG",
    "PH",
    "PK",
    "PY",
    "RO",
    "RS",
    "RU",
    "RW",
    "SB",
    "SD",
    "SL",
    "SN",
    "SO",
    "SR",
    "SS",
    "ST",
    "SV",
    "SY",
    "SZ",
    "TD",
    "TG",
    "TH",
    "TJ",
    "TL",
    "TM",
    "TN",
    "TO",
    "TR",
    "TV",
    "TZ",
    "UA",
    "UG",
    "UZ",
    "VN",
    "VU",
    "WS",
    "ZA",
    "ZM",
    "ZW",
}


# * Models for transformers
class CTNode(BaseModel):
    feature: str
    description: str
    value: int | float
    weight: int | float
    score: int | float

    @classmethod
    def get_node(cls, nodes: list["CTNode"], feature: str) -> "CTNode | None":
        return next((node for node in nodes if node.feature == feature), None)

    @classmethod
    def get_value_by_feature(cls, nodes: list["CTNode"], feature: str) -> int | float | None:
        node = cls.get_node(nodes=nodes, feature=feature)
        return node.value if node else None

    @classmethod
    def get_description_by_feature(cls, nodes: list["CTNode"], feature: str) -> str | None:
        node = cls.get_node(nodes=nodes, feature=feature)
        return node.description if node else None

    @classmethod
    def filter_nodes(cls, nodes: list["CTNode"], ignore_features: tuple[str, ...] | None = None) -> list["CTNode"]:
        """
        Return a list of nodes excluding those with features in ignore_features
        """
        if ignore_features is None:
            ignore_features = ()
        return [node for node in nodes if node.feature not in ignore_features]

    @staticmethod
    def create_node(feature: str, description: str = "", value: Any = 0, weight: float = 1.0) -> "CTNode":
        numeric_value = float(value) if isinstance(value, int | float) else 0
        numeric_weight = float(weight) if isinstance(weight, int | float) else 0
        score = numeric_value * numeric_weight if not (numeric_value == 0 or numeric_weight == 0) else 0

        return CTNode(
            feature=feature,
            description=description,
            value=value or 0.0,
            weight=weight,
            score=score,
        )

    @staticmethod
    def append_node(nodes: list["CTNode"], feature: str, description: str = "", value: Any = 0, weight: float = 1.0):
        nodes.append(CTNode.create_node(feature=feature, description=description, value=value, weight=weight))
        return True


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
            risk_thresholds (RiskThresholdsDict): With 'low' and 'high' thresholds

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
    def get_trial_size(cls, condition: str, phase: float, sample_size: int, sample_size_tertiles: list[SampleSizeTertile]) -> "TrialSize":
        """
        Determine the trial size based on condition, phase, and sample size

        Priority for matching:
            1. Exact condition and exact phase
            2. Wildcard condition and exact phase
            3. Exact condition and wildcard phase
            4. Wildcard condition and wildcard phase
        """
        # * Priority of matching conditions
        priority = [(condition, phase), ("*", phase), (condition, "*"), ("*", "*")]

        # * Find the first matching tertile based on priority
        matching_tertile = None
        for cond, ph in priority:
            matching_tertile = next((tertile for tertile in sample_size_tertiles if tertile.condition == cond and tertile.phase == ph), None)
            if matching_tertile:
                break

        # * Default to MEDIUM if no matching tertile is found
        if not matching_tertile:
            return cls.MEDIUM

        if sample_size < matching_tertile.lower_tertile:
            return cls.SMALL
        if sample_size < matching_tertile.upper_tertile:
            return cls.MEDIUM

        return cls.LARGE


def transform_data_for_rac(
    metadata: list[ClinicalTrialMetadata], result: dict, module_weight: WeightProfile | UserWeightProfile, selected_param: dict
) -> tuple[list[CTNode], list[CTNode]]:
    """
    General transformer for risk and cost
    """
    # * Transform to WeightProfileBase
    mapped_weights = WeightProfileBase(**module_weight.weights)

    cost_nodes: list[CTNode] = []
    risk_nodes: list[CTNode] = []

    for meta in metadata or []:
        if meta.feature_type == "text" and meta.id != "drug":
            continue

        prediction = result.get(meta.id, {}).get("prediction")

        cost_weight = mapped_weights.get_cost_by_name(name=meta.id)
        risk_weight = mapped_weights.get_risk_by_name(name=meta.id)

        selected_value = selected_param.get(meta.id, prediction)

        description = meta.get_description(selected_value=selected_value)
        value = meta.get_value(selected_value, prediction)

        if meta.id == "drug":
            prediction = result.get(meta.id, {}).get("prediction")
            if type(prediction) is list:
                num_drugs = len(prediction)
            else:
                num_drugs = 1

            dummy_key = "num_drugs"

            cost_nodes.append(CTNode.create_node(feature=dummy_key, description=description, value=num_drugs, weight=cost_weight))
            risk_nodes.append(CTNode.create_node(feature=dummy_key, description=description, value=num_drugs, weight=risk_weight))

            continue

        if meta.id in ["regimen", "age"]:
            dummy_weights = mapped_weights.get_cost_risk_model_for_dummy_variable(key=f"{meta.id}=")

            if type(prediction) is dict:
                for key, sub_value in prediction.items():
                    # * Composite key, following the same feature=dummy convention

                    dummy_key = f"{meta.id}={key}"
                    cost_weight = dummy_weights.get_cost_by_name(name=key)
                    risk_weight = mapped_weights.get_risk_by_name(name=key)

                    cost_nodes.append(CTNode.create_node(feature=dummy_key, description=description, value=sub_value, weight=cost_weight))
                    risk_nodes.append(CTNode.create_node(feature=dummy_key, description=description, value=sub_value, weight=risk_weight))
                continue

        if meta.id == "regimen_duration":
            continue

        # * Determine if trial is international
        if meta.id == "country":
            # * Add extra derived node
            if prediction is None:
                international_value = 0
            else:
                international_value = int(len(prediction) > 1)

            international_cost_weight = mapped_weights.get_cost_by_name(name="international", default=0)
            international_risk_weight = mapped_weights.get_risk_by_name(name="international", default=0)

            lmic_weight = module_weight.weights.get(meta.id, {}).get("lmic", 0)

            # * Check if it's in any low to medium income country
            if prediction is not None:
                lmic_countries_in_trial = LMIC_COUNTRIES.intersection(prediction)
            else:
                lmic_countries_in_trial = set()
            if lmic_countries_in_trial is not None:
                is_lmic = int(len(lmic_countries_in_trial) > 0)
            else:
                is_lmic = 0
            if is_lmic:
                lmic_description = f"Is lmic, countries found {', '.join(prediction)}"
            else:
                lmic_description = "Is not in lmic"

            lmic_score = is_lmic * lmic_weight

            # * Add international feature to both cost and risk
            cost_nodes.append(
                CTNode.create_node(feature="international", description=f"Is international: {international_value}", value=international_value, weight=international_cost_weight)
            )
            risk_nodes.append(
                CTNode.create_node(feature="international", description=f"Is international: {international_value}", value=international_value, weight=international_risk_weight)
            )

            # * Add lmic feature to both cost and risk
            cost_nodes.append(
                CTNode(
                    feature="lmic",
                    description=lmic_description,
                    value=is_lmic,
                    weight=lmic_weight,
                    score=lmic_score,
                )
            )
            risk_nodes.append(
                CTNode(
                    feature="lmic",
                    description=lmic_description,
                    value=is_lmic,
                    weight=lmic_weight,
                    score=lmic_score,
                )
            )

            # todo These need to be added to the result dictionary itself to ensure that the data read on the client side remains consistent
            result.setdefault("international", {}).setdefault("prediction", international_value)
            result.setdefault("lmic", {}).setdefault("prediction", is_lmic)

            continue

        cost_nodes.append(CTNode.create_node(feature=meta.id, description=description, value=value, weight=cost_weight))
        risk_nodes.append(CTNode.create_node(feature=meta.id, description=description, value=value, weight=risk_weight))

        # Add other tertiles - we need to unify this later
        if meta.id in ("duration", "recency", "num_sites", "num_visits"):
            tertile_meta_id = meta.id + "_tertile"
            risk_weight = mapped_weights.get_risk_by_name(name=tertile_meta_id)
            if meta.id == "num_visits":
                value = int(np.floor(value / 20))
            tertile_number = max([value, 2])
            score = risk_weight * tertile_number
            risk_nodes.append(
                CTNode(
                    feature=tertile_meta_id,
                    description=f"Tertile of {meta.id}",
                    value=tertile_number,
                    weight=risk_weight,
                    score=score,
                )
            )

    # * Add constant node
    constant_cost_weight = mapped_weights.get_cost_by_name("constant")
    constant_risk_weight = mapped_weights.get_risk_by_name("constant")

    cost_nodes.append(
        CTNode.create_node(feature="constant", description="constant", value=1, weight=constant_cost_weight),
    )
    risk_nodes.append(
        CTNode.create_node(feature="constant", description="constant", value=1, weight=constant_risk_weight),
    )

    # * Get trial size
    condition_node = CTNode.get_description_by_feature(nodes=risk_nodes, feature="condition")
    phase_node = CTNode.get_value_by_feature(nodes=risk_nodes, feature="phase")
    sample_size_node = CTNode.get_value_by_feature(nodes=risk_nodes, feature="sample_size")

    if condition_node is not None and phase_node is not None and sample_size_node is not None:
        trial_size: TrialSize = TrialSize.get_trial_size(
            condition=condition_node, phase=phase_node, sample_size=int(sample_size_node), sample_size_tertiles=mapped_weights.sample_size_tertiles
        )
        trial_size_weight = mapped_weights.get_risk_by_name(name="sample_size_tertile", default=10)
        trial_size_tertile_number = trial_size.id
        trial_size_score = trial_size_weight * trial_size_tertile_number
        risk_nodes.append(
            CTNode(
                feature="trial_size",
                description=f"Trial size based on condition and phase {trial_size.name}",
                value=trial_size_tertile_number,
                weight=trial_size_weight,
                score=trial_size_score,
            )
        )

    return (cost_nodes, risk_nodes)


def calculate_lmic_condition_cost(lmic_condition_coefficient: WeightProfileBase, conditions: list[str]) -> float:
    """
    Calculate the total cost contribution from the specified conditions
    using the LMIC condition coefficients

    Parameters:
        conditions (list of str): A list of condition names

    Returns:
        float: The total cost contribution from the conditions
    """
    total_cost = 0.0
    for condition in conditions:
        cost = lmic_condition_coefficient.get_cost_by_name(name=condition)
        total_cost += cost
    return total_cost


def get_total_cost_or_risk_per_participant(ct_nodes: list[CTNode], ignore_features: tuple[str, ...] = ()) -> int | float:
    """
    Calculate the total cost per participant by summing the scores of CTNodes,
    excluding nodes with features listed in ignore_features
    """
    filtered_nodes = CTNode.filter_nodes(nodes=ct_nodes, ignore_features=ignore_features)
    return sum(node.score for node in filtered_nodes)


def get_total_trial_cost(ct_nodes: list[CTNode], module_weight: WeightProfile | UserWeightProfile) -> tuple[float, float]:
    """
    Calculate the total trial cost and total cost per participant.
    """
    sample_size = CTNode.get_value_by_feature(nodes=ct_nodes, feature="sample_size")

    if sample_size is None:
        raise ValueError("No sample size found")

    total_cost_per_participant = get_total_cost_or_risk_per_participant(ct_nodes=ct_nodes)

    condition_node = CTNode.get_description_by_feature(nodes=ct_nodes, feature="condition")

    if condition_node is None:
        raise ValueError("No condition found")

    total_cost_per_participant += calculate_lmic_condition_cost(
        conditions=[condition_node],
        lmic_condition_coefficient=WeightProfileBase(**module_weight.weights).get_cost_risk_model_for_dummy_variable(
            "condition=",
        ),
    )

    trial_cost = float(total_cost_per_participant) * float(sample_size)

    return trial_cost, float(total_cost_per_participant)


def get_trial_risk_score(ct_node: list[CTNode], module_weight: WeightProfile | UserWeightProfile) -> tuple[float, str]:
    """
    Determine the trial risk score based on the total cost per participant.

    The total risk score is calculated using the `get_total_cost_or_risk_per_participant` function,
    and it is clamped to ensure it falls within the range [0, 100]. Based on this clamped score,
    the corresponding TrialRiskLevel ("Low", "Medium", or "High") is determined.

    Args:
        ct_node (List[CTNode]): A list of CTNode instances representing clinical trial nodes

    Returns:
        str: The label of the corresponding TrialRiskLevel ("Low", "Medium", or "High")
    """
    total_risk_score = get_total_cost_or_risk_per_participant(ct_node)
    mapped_weights = WeightProfileBase(**module_weight.weights)
    risk_level = TrialRiskLevel.is_within_threshold(total_risk_score, mapped_weights.risk_thresholds)

    total_risk_score = max(0, min(100, total_risk_score))

    # * If no specific thresholds are met, return MEDIUM
    return total_risk_score, risk_level.label
