from collections import OrderedDict
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from clinicaltrials.core import Metadata as ClinicalTrialMetadata
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import BigInteger, Boolean, Column, DateTime, Field, ForeignKey, Session, SQLModel, Text, UniqueConstraint, select, text


class WeightTypeEnum(str, Enum):
    # * Cost Risk Models
    CRM = "crm"
    # * Sample Size Tertiles
    SST = "sst"
    # * Risk Thresholds
    RT = "rt"

    @staticmethod
    def parse(value: str | None):
        if value is None or value.strip() == "":
            return None
        value = value.lower()
        try:
            return WeightTypeEnum(value)
        except ValueError as e:
            allowed_values = [member.value for member in WeightTypeEnum]
            raise ValueError(f"Invalid value for 't'. Allowed values are {allowed_values}.") from e


class CostRiskModel(BaseModel):
    cost: float
    risk: float


class SampleSizeTertile(BaseModel):
    condition: str | float
    phase: str | float
    lower_tertile: int | float
    upper_tertile: int | float


class RiskThresholdsDict(BaseModel):
    low: int | float
    high: int | float


class RawWeight(BaseModel):
    cost_risk_models: dict[str, CostRiskModel]
    sample_size_tertiles: list[SampleSizeTertile]
    risk_thresholds: RiskThresholdsDict

    def to_serializable_cost_risk_models(self, group=False) -> dict[str, dict[str, float]]:
        if group:
            return self.group()

        return {key: value.model_dump() for key, value in self.cost_risk_models.items()}

    def to_serializable_sample_size_tertiles(self) -> list[dict[str, Any]]:
        return [t.model_dump() for t in self.sample_size_tertiles]

    def to_serializable_risk_thresholds(self) -> dict[str, float]:
        return self.risk_thresholds.model_dump()

    def to_serializable(self, group=False) -> dict:
        return {
            "cost_risk_models": self.group() if group else self.to_serializable_cost_risk_models(),
            "sample_size_tertiles": self.to_serializable_sample_size_tertiles(),
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
    Has cost_risk_models, sample_size_tertiles, and risk_thresholds fields.
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

        return WeightProfileBase(cost_risk_models=cost_risk_model, sample_size_tertiles=self.sample_size_tertiles, risk_thresholds=self.risk_thresholds)


class DynamicProfile(WeightProfileBase):
    name: str


class UpdateDynamicProfile(WeightProfileBase):
    name: str | None = None


class WeightProfile(SQLModel, table=True):
    """
    Default weight profile provided by core lib. All other profiles will be copied from this.
    """

    __tablename__: str = "weight_profile"  # type: ignore
    __table_args__: tuple = dict(comment="Base weight profile directly comes from core lib")

    id: int = Field(sa_column=Column(BigInteger(), primary_key=True), default=None)
    name: str = Field(nullable=False, unique=True)
    weights: dict = Field(sa_column=Column(JSONB(), nullable=False))
    default: bool = Field(default=False, sa_column=Column(Boolean(), server_default=text("false"), nullable=False))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(), server_default=text("CURRENT_TIMESTAMP"), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(), server_default=text("CURRENT_TIMESTAMP"), nullable=False),
    )

    @staticmethod
    def sync_default_weights(session: Session, metadata: list[ClinicalTrialMetadata]):
        """
        This static method can be used to seed the default weight profile or to sync new modules between core lib and weights
        """
        logger.info("Starting default weight sync")

        # * Get default weight profile
        default_weight_profile = session.exec(select(WeightProfile).where(WeightProfile.default == True)).first()

        target_weights: dict[str, dict[str, float]] = {metadata_value.id: {**metadata_value.default_weights} for metadata_value in metadata}

        if default_weight_profile is None:
            logger.info("Default weight profile not found. Creating default...")
            new_default_profile = WeightProfile(name="Default Weight Profile", weights=target_weights, default=True)

            session.add(new_default_profile)
            session.commit()
            logger.info("Default weight profile created successfully")
            return

        # * Initialize a flag to track if updates are needed
        is_updated = False

        # * Iterate over target_weights to ensure all keys are present in default_weight_profile.weights
        for key, weights in target_weights.items():
            if key not in default_weight_profile.weights:
                logger.info(f"Adding missing key '{key}' to default weights.")
                default_weight_profile.weights[key] = weights
                is_updated = True

        if is_updated:
            default_weight_profile.updated_at = datetime.now(UTC)
            session.add(default_weight_profile)
            session.commit()
            logger.info("Default weights updated with new keys")
        else:
            logger.info("Weights synced, no update required")


class UserWeightProfile(SQLModel, table=True):
    __tablename__: str = "user_weight_profile"  # type: ignore
    __table_args__: tuple = (
        UniqueConstraint("user_id", "name"),
        dict(comment=None),
    )

    id: int = Field(sa_column=Column(BigInteger(), primary_key=True), default=None)
    user_id: int = Field(sa_column=Column(BigInteger(), ForeignKey("user.id", ondelete="CASCADE"), nullable=False))
    name: str = Field(max_length=1000, nullable=False)
    weight_profile_id: int | None = Field(sa_column=Column(BigInteger(), ForeignKey("weight_profile.id"), nullable=True), default=None)
    weights: dict = Field(sa_column=Column(JSONB(), nullable=False))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(), server_default=text("CURRENT_TIMESTAMP"), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(), server_default=text("CURRENT_TIMESTAMP"), nullable=False),
    )

    # Relationships
    # user: "User" = Relationship(back_populates="user_weight_profile")


class DocumentRunWeightProfile(SQLModel, table=True):
    __tablename__: str = "document_run_weight_profile"  # type: ignore
    __table_args__: tuple = dict(comment=None)

    id: int = Field(sa_column=Column(BigInteger(), primary_key=True), default=None)
    document_id: int = Field(sa_column=Column(BigInteger(), ForeignKey("document.id", ondelete="CASCADE"), nullable=False))
    weights: dict = Field(sa_column=Column(JSONB(), nullable=False))
    notes: str | None = Field(sa_column=Column(Text(), nullable=True), default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(), server_default=text("CURRENT_TIMESTAMP"), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(), server_default=text("CURRENT_TIMESTAMP"), nullable=False),
    )
