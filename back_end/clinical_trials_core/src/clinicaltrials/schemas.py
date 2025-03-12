from collections import OrderedDict
from typing import Any

from pydantic import BaseModel


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


class Tertile(BaseModel):
    condition: str | float
    phase: str | float
    lower_tertile: int | float
    upper_tertile: int | float


class RiskThresholdsDict(BaseModel):
    low: int | float
    high: int | float


class CostRiskModel(BaseModel):
    cost: float
    risk: float


class RawWeight(BaseModel):
    cost_risk_models: dict[str, CostRiskModel]
    risk_thresholds: RiskThresholdsDict
    tertiles: dict[str, list[Tertile]]

    def to_serializable_cost_risk_models(self, group=False) -> dict[str, dict[str, float]]:
        if group:
            return self.group()

        return {key: value.model_dump() for key, value in self.cost_risk_models.items()}

    def to_serializable_tertiles(self) -> dict[str, list[Tertile]]:
        return {k: [t.model_dump() for t in v] for k, v in self.tertiles.items()}

    def to_serializable_risk_thresholds(self) -> dict[str, float]:
        return self.risk_thresholds.model_dump()

    def to_serializable(self, group=False) -> dict:
        return {
            "cost_risk_models": self.group() if group else self.to_serializable_cost_risk_models(),
            "tertiles": self.to_serializable_tertiles(),
            "risk_thresholds": self.to_serializable_risk_thresholds(),
        }

    def sorted_cost_risk_models(self) -> OrderedDict[str, CostRiskModel]:
        return OrderedDict(sorted(self.cost_risk_models.items(), key=lambda item: item[0].lower()))

    def group(self):
        """
        Walk through each key in cost_risk_models. For keys that contain '=',
        split them into two parts and nest the value accordingly

        For a given parent:
        - If there are nested entries (e.g. "condition=TB") and there is also a non split
            key "condition", then the non split value will be stored under the "base" key
        - If there are no nested entries for a key, the non split key remains unchanged
        """
        result = {}

        for key, value in self.cost_risk_models.items():
            dumped = value.model_dump()
            if isinstance(key, str) and "=" in key:
                parent, child = key.split("=", 1)
                # * If the parent already exists but isn't structured for grouping, wrap its existing value into a "base" entry.
                if parent in result:
                    if not (isinstance(result[parent], dict) and "base" in result[parent]):
                        result[parent] = {"base": result[parent]}
                else:
                    result[parent] = {}
                result[parent][child] = dumped
            elif key in result and isinstance(result[key], dict):
                # * For non-nested keys:  If nested entries exist, save the non‑split value under "base"s
                result[key]["base"] = dumped
            else:
                result[key] = dumped

        return result


class WeightProfileBase(RawWeight):
    """
    Has cost_risk_models, tertiles, and risk_thresholds fields.
    """

    @staticmethod
    def validate_allowed_keys(weights: dict[str, CostRiskModel], allowed_modules: list[str]) -> None:
        invalid_keys = [key for key in weights.keys() if key not in allowed_modules]
        if invalid_keys:
            raise ValueError(f"Invalid keys: {invalid_keys}. Allowed keys are: {allowed_modules}")

    def get_cost_by_name(self, name: str, default=0.0) -> float:
        """Retrieve the cost value for a given module name"""
        return self.cost_risk_models.get(name, CostRiskModel(cost=default, risk=default)).cost

    def get_risk_by_name(self, name: str, default=0.0) -> float:
        """Retrieve the risk value for a given module name"""
        return self.cost_risk_models.get(name, CostRiskModel(cost=default, risk=default)).risk

    def get_cost_risk_model_for_dummy_variable(self, key: str) -> "WeightProfileBase":
        cost_risk_model: dict[str, CostRiskModel] = {}
        for module, value in self.cost_risk_models.items():
            if module.startswith(key):
                _, _key = module.split("=", 1)
                cost_risk_model[_key] = value

        return WeightProfileBase(
            cost_risk_models=cost_risk_model,
            risk_thresholds=self.risk_thresholds,
            tertiles=self.tertiles,
        )
