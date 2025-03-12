from datetime import UTC, datetime
from enum import Enum

from loguru import logger
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import BigInteger, Boolean, Column, DateTime, Field, ForeignKey, Session, SQLModel, Text, \
    UniqueConstraint, select, text

from clinicaltrials.core import Metadata as ClinicalTrialMetadata
from clinicaltrials.schemas import WeightProfileBase


class WeightTypeEnum(str, Enum):
    # * Cost Risk Models
    CRM = "crm"
    # * Tertiles
    TT = "tt"
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

        target_weights: dict[str, dict[str, float]] = {metadata_value.id: {**metadata_value.default_weights} for
                                                       metadata_value in metadata}

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
    weight_profile_id: int | None = Field(
        sa_column=Column(BigInteger(), ForeignKey("weight_profile.id"), nullable=True), default=None)
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
    document_id: int = Field(
        sa_column=Column(BigInteger(), ForeignKey("document.id", ondelete="CASCADE"), nullable=False))
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
