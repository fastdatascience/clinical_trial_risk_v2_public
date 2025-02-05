from pydantic import BaseModel, Field


class WordcloudReportData(BaseModel):
    img_base64: str = Field(description="Image base64.")


class RiskReportData(BaseModel):
    level: str = Field(description="Level.")
    score: str = Field(description="Score.")
    calculation: dict = Field(description="Calculation.")


class OverviewWordCountsByPageReportData(BaseModel):
    explanation_img_base64: str = Field(description="Image base64.")


class BaseExplanationReportData(BaseModel):
    prediction: str = Field(description="Prediction.")
    explanation_extra_surtitle_text: str = Field(
        description="Explanation extra surtitle text."
    )
    explanation_img_base64: str = Field(description="Explanation image base64.")


class ScorePercentageExplanationReportData(BaseModel):
    score_percentage: str = Field(description="Score in %.")


class ContextExplanationReportData(BaseModel):
    context: dict = Field(description="Context.")


class ConditionReportData(
    BaseExplanationReportData,
    ScorePercentageExplanationReportData,
    ContextExplanationReportData,
):
    pass


class PhaseReportData(BaseExplanationReportData, ContextExplanationReportData):
    pass


class SapReportData(BaseExplanationReportData, ContextExplanationReportData):
    pass


class EffectEstimateReportData(
    BaseExplanationReportData,
    ScorePercentageExplanationReportData,
    ContextExplanationReportData,
):
    pass


class SampleSizeEstimateReportData(
    BaseExplanationReportData,
    ScorePercentageExplanationReportData,
    ContextExplanationReportData,
):
    pass


class NumberOfArmsReportData(BaseExplanationReportData, ContextExplanationReportData):
    pass


class CountryReportData(BaseExplanationReportData, ContextExplanationReportData):
    pass


class SimulationReportData(
    BaseExplanationReportData,
    ScorePercentageExplanationReportData,
    ContextExplanationReportData,
):
    pass


class AnalysisReportData(BaseModel):
    filename: str = Field(description="Filename.")
    wordcloud: WordcloudReportData = Field("Wordcloud.")
    risk: RiskReportData = Field(description="Risk.")
    condition: ConditionReportData = Field(description="Condition.")
    phase: PhaseReportData = Field(description="Phase.")
    sap: SapReportData = Field(description="SAP.")
    effect_estimate: EffectEstimateReportData = Field(description="Effect estimate.")
    sample_size: SampleSizeEstimateReportData = Field(description="Sample size.")
    num_arms: NumberOfArmsReportData = Field(description="Number of Arms.")
    country: CountryReportData = Field(description="Country.")
    simulation: SimulationReportData = Field(description="Simulation.")
    key_protocol_info: dict = Field(description="Key protocol info.")
    sample_size_tertiles: dict = Field(description="Sample size tertiles.")
    logs: dict[str, list[str]] = Field(description="Logs.")
    overview_word_counts_by_page: OverviewWordCountsByPageReportData = Field(
        description="Overview of word counts by page."
    )
