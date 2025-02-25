import io
import re
import time
from collections import OrderedDict
from typing import Any

import numpy as np
import pandas as pd
from clinicaltrials.core import ClassifierConfig
from plotly import express as px
from plotly import graph_objects as pgo
from plotly import subplots as psp
from pydantic import BaseModel, Field
from spacy.tokens import Doc as SpacyDoc

from app import schemas, services, utils
from app.models.document.document import Document
from app.models.weight_profile.base import WeightProfileBase
from app.services.transform import CTNode


class HeatMapResult(BaseModel):
    graph_base64: str = Field("Graph base64.")
    extra_surtitle_text: str = Field("Surtitle text.")
    context: dict = Field("Context.")
    log: str = Field("Log.")


class AnalysisReportData:
    def __init__(
        self,
        db_document: Document,
        tokenised_pages: list[SpacyDoc],
        user_resource_usage_result: dict,
        trial_risk_score: tuple[float, str],
        ct_cost_nodes: list[CTNode],
        ct_risk_nodes: list[CTNode],
        weights: WeightProfileBase,
        logs: OrderedDict[str, list[str]],
        analysis_run_time: float = None,
    ):
        """
        :param db_document: The document from db.
        :param user_resource_usage_result: The user resource usage result.
        :param trial_risk_score: The trial risk score.
        :param ct_risk_nodes: The clinical Trials risk nodes.
        :param ct_cost_nodes: The clinical Trials cost nodes.
        :param weights: The weights.
        :param logs: Analysis log.
        :param analysis_run_time: The analysis run time.
        """

        # Log
        if not logs:
            self.__logs: OrderedDict[str, list[str]] = OrderedDict()
        else:
            self.__logs = logs

        # Analysis run time
        self.__analysis_run_time = analysis_run_time

        # Document
        self.__db_document: Document = db_document

        # Tokenised pages
        self.__tokenised_pages = tokenised_pages

        # Trial risk score
        self.__trial_risk_score = trial_risk_score

        # User resource usage result
        self.__user_resource_usage_result = user_resource_usage_result

        # CT nodes
        self.__ct_risk_nodes = ct_risk_nodes
        self.__ct_cost_nodes = ct_cost_nodes
        self.__ct_risk_nodes_dict = {x.feature: x for x in ct_risk_nodes}
        self.__ct_cost_nodes_dict = {x.feature: x for x in ct_cost_nodes}

        # Risk Threshold
        self.__risk_threshold = weights.risk_thresholds

        # Tertiles data
        self.__tertiles_data_transformed = self.__tertile_data_transformed(sample_size_tertiles=weights.to_serializable_sample_size_tertiles())

        # List of page numbers
        self.__page_numbers = list(range(1, 1 + len(self.__tokenised_pages)))

        # Filename
        self.__filename = self.__db_document.original_document_name

        # Risk
        self.__risk_score = self.__trial_risk_score[0]
        self.__risk_level = self.__trial_risk_score[1]
        self.__risk_score_100_point_scale = self.__calculate_risk_score_100_point_scale()

        # Condition result
        condition_result: dict = self.__user_resource_usage_result["condition"]
        self.__condition_prediction: str = condition_result["prediction"]
        self.__condition_score: float = condition_result["score"]
        self.__condition_pages: dict[str, list[float]] = condition_result["pages"]
        self.__condition_page_scores: list[float] = condition_result.get("page_scores", [])
        self.__condition_score_percentage: str = self.__score_to_percentage(self.__condition_score)
        self.__condition_context: dict[str, list[float]] = condition_result.get("context", {})

        # Phase result
        phase_result: dict = self.__user_resource_usage_result["phase"]
        self.__phase_prediction: int = int(phase_result["prediction"])
        self.__phase_pages: dict[str, list[float]] = phase_result["pages"]
        self.__phase_page_scores: list[float] = phase_result.get("page_scores", [])
        self.__phase_context: dict[str, list[float]] = phase_result.get("context", {})

        # SAP result
        sap_result: dict = self.__user_resource_usage_result["sap"]
        self.__sap_prediction: int = int(sap_result["prediction"])
        self.__sap_pages: dict[str, list[float]] = sap_result["pages"]
        self.__sap_page_scores: list[float] = sap_result.get("page_scores", [])
        self.__sap_score: float = sap_result["score"]
        self.__sap_score_percentage: str = self.__score_to_percentage(self.__sap_score)
        self.__sap_context: dict[str, list[float]] = sap_result.get("context", {})

        # Effect estimate result
        effect_estimate_result: dict = self.__user_resource_usage_result["effect_estimate"]
        self.__effect_estimate_prediction: int = int(effect_estimate_result["prediction"])
        self.__effect_estimate_score: float = effect_estimate_result["score"]
        self.__effect_estimate_pages: dict[str, list[float]] = effect_estimate_result["pages"]
        self.__effect_estimate_page_scores: list[float] = effect_estimate_result.get("page_scores", [])
        self.__effect_estimate_score_percentage: str = self.__score_to_percentage(self.__effect_estimate_score)
        self.__effect_estimate_context: dict[str, list[float]] = effect_estimate_result.get("context", {})

        # Country result
        country_result: dict = self.__user_resource_usage_result["country"]
        self.__country_prediction: list[str] = country_result["prediction"]
        self.__country_pages: dict[str, list[float]] = country_result["pages"]
        self.__country_page_scores: list[float] = country_result.get("page_scores", [])
        self.__country_context: dict[str, list[float]] = country_result.get("context", {})

        # Simulation result
        simulation_result: dict = self.__user_resource_usage_result["simulation"]
        self.__simulation_prediction: int = int(simulation_result["prediction"])
        self.__simulation_score: float = simulation_result["score"]
        self.__simulation_score_percentage: str = self.__score_to_percentage(self.__simulation_score)
        self.__simulation_pages: dict[str, list[float]] = simulation_result["pages"]
        self.__simulation_page_scores: list[float] = simulation_result.get("page_scores", [])
        self.__simulation_context: dict[str, list[float]] = simulation_result.get("context", {})

        # Sample size result
        sample_size_result: dict = self.__user_resource_usage_result["sample_size"]
        self.__sample_size_prediction: int = int(sample_size_result["prediction"])
        self.__sample_size_score: float = sample_size_result["score"]
        self.__sample_size_pages: dict[str, list[float]] = sample_size_result["pages"]
        self.__sample_size_page_scores: list[float] = sample_size_result.get("page_scores", [])
        self.__sample_size_score_percentage: str = self.__score_to_percentage(self.__sample_size_score)
        self.__sample_size_context: dict[str, list[float]] = sample_size_result.get("context", {})

        # Number of Arms result
        num_arms_result: dict = self.__user_resource_usage_result["num_arms"]
        self.__num_arms_prediction: int = int(num_arms_result["prediction"])
        self.__num_arms_pages: dict[str, list[float]] = num_arms_result["pages"]
        self.__num_arms_page_scores: list[float] = num_arms_result.get("page_scores", [])
        self.__num_arms_context: dict[str, list[float]] = num_arms_result.get("context", {})

    def generate(self) -> schemas.AnalysisReportData:
        """
        Generate analysis report data.

        :returns: The analysis report data. This data can be passed to the pdf generator service to generate the
         analysis report in PDF.
        """

        # Wordcloud
        wordcloud = self.__get_wordcloud()

        # Key protocol info
        key_protocol_info = self.__get_key_protocol_info()

        # Risk calculation
        risk_calculation = self.__get_risk_calculation()

        # Sample size tertiles
        sample_size_tertiles = self.__get_sample_size_tertiles()

        # Explanation Overview of Word Counts by Page
        explanation_overview_of_word_counts_by_page = self.__get_explanation_overview_of_word_counts_by_page()

        # Explanation Condition
        explanation_condition = self.__get_explanation_by_key(
            key_name=self.__condition_prediction,
            pages=self.__condition_pages,
            page_scores=self.__condition_page_scores,
            context=self.__condition_context,
        )

        # Explanation Phase
        explanation_phase = self.__get_explanation_by_key(
            key_name="PHASE",
            pages=self.__phase_pages,
            page_scores=self.__phase_page_scores,
            context=self.__phase_context,
        )

        # Explanation SAP
        explanation_sap = self.__get_explanation_by_key(
            key_name="SAP",
            pages=self.__sap_pages,
            page_scores=self.__sap_page_scores,
            context=self.__sap_context,
        )

        # Explanation Effect Estimate
        explanation_effect_estimate = self.__get_explanation_by_key(
            key_name="EFFECT ESTIMATE",
            pages=self.__effect_estimate_pages,
            page_scores=self.__effect_estimate_page_scores,
            context=self.__effect_estimate_context,
        )

        # Explanation Sample Size
        explanation_sample_size = self.__get_explanation_by_key(
            key_name="NUMBER OF SUBJECTS",
            pages=self.__sample_size_pages,
            page_scores=self.__sample_size_page_scores,
            context=self.__sample_size_context,
        )

        # Explanation Number of Arms
        explanation_num_arms = self.__get_explanation_by_key(
            key_name="NUMBER OF ARMS",
            pages=self.__num_arms_pages,
            page_scores=self.__num_arms_page_scores,
            context=self.__num_arms_context,
        )

        # Explanation Country
        explanation_country = self.__get_explanation_by_key(
            key_name="COUNTRY",
            pages=self.__country_pages,
            page_scores=self.__country_page_scores,
            context=self.__country_context,
        )

        # Explanation Simulation
        explanation_simulation = self.__get_explanation_by_key(
            key_name="SIMULATION",
            pages=self.__simulation_pages,
            page_scores=self.__simulation_page_scores,
            context=self.__simulation_context,
        )

        if self.__analysis_run_time:
            self.__logs["analysis_runtime"] = [f"The NLP analysis ran in {self.__analysis_run_time} seconds."]

        return schemas.AnalysisReportData(
            filename=self.__filename,
            wordcloud=schemas.WordcloudReportData(
                img_base64=wordcloud["wordcloud_base64"],
            ),
            risk=schemas.RiskReportData(
                level=self.__risk_level.upper(),
                score=str(self.__risk_score_100_point_scale),
                calculation=risk_calculation,
            ),
            condition=schemas.ConditionReportData(
                prediction=self.__condition_prediction,
                score_percentage=self.__condition_score_percentage,
                explanation_img_base64=explanation_condition.graph_base64,
                explanation_extra_surtitle_text=explanation_condition.extra_surtitle_text,
                context=explanation_condition.context,
            ),
            phase=schemas.PhaseReportData(
                prediction=str(int(self.__phase_prediction)),
                explanation_img_base64=explanation_phase.graph_base64,
                explanation_extra_surtitle_text=explanation_phase.extra_surtitle_text,
                context=explanation_phase.context,
            ),
            overview_word_counts_by_page=schemas.OverviewWordCountsByPageReportData(explanation_img_base64=explanation_overview_of_word_counts_by_page["graph_base64"]),
            sap=schemas.SapReportData(
                prediction=str(self.__sap_prediction),
                explanation_img_base64=explanation_sap.graph_base64,
                explanation_extra_surtitle_text=explanation_sap.extra_surtitle_text,
                context=explanation_sap.context,
            ),
            effect_estimate=schemas.EffectEstimateReportData(
                prediction=str(self.__effect_estimate_prediction),
                score_percentage=self.__effect_estimate_score_percentage,
                explanation_img_base64=explanation_effect_estimate.graph_base64,
                explanation_extra_surtitle_text=explanation_effect_estimate.extra_surtitle_text,
                context=explanation_effect_estimate.context,
            ),
            sample_size=schemas.SampleSizeEstimateReportData(
                prediction=str(self.__sample_size_prediction),
                score_percentage=self.__sample_size_score_percentage,
                explanation_img_base64=explanation_sample_size.graph_base64,
                explanation_extra_surtitle_text=explanation_sample_size.extra_surtitle_text,
                context=explanation_sample_size.context,
            ),
            num_arms=schemas.NumberOfArmsReportData(
                prediction=str(self.__num_arms_prediction),
                explanation_img_base64=explanation_num_arms.graph_base64,
                explanation_extra_surtitle_text=explanation_num_arms.extra_surtitle_text,
                context=explanation_num_arms.context,
            ),
            country=schemas.CountryReportData(
                prediction=utils.pretty_print_countries(countries=self.__country_prediction),
                explanation_img_base64=explanation_country.graph_base64,
                explanation_extra_surtitle_text=explanation_country.extra_surtitle_text,
                context=explanation_country.context,
            ),
            simulation=schemas.SimulationReportData(
                prediction=str(self.__simulation_prediction),
                score_percentage=self.__simulation_score_percentage,
                explanation_img_base64=explanation_simulation.graph_base64,
                explanation_extra_surtitle_text=explanation_simulation.extra_surtitle_text,
                context=explanation_simulation.context,
            ),
            key_protocol_info=key_protocol_info,
            sample_size_tertiles=sample_size_tertiles,
            logs=self.__logs,
        )

    def __calculate_risk_score_100_point_scale(self) -> int:
        """
        Calculate risk score on a 100-point scale.
        """

        score = int(min((100, np.round(self.__risk_score))))

        return score

    def __get_wordcloud(self) -> dict[str, str]:
        """
        Get wordcloud.
        """

        # Do not generate wordcloud if falsy
        if not self.__tokenised_pages:
            return {
                "wordcloud_base64": "",
                "log": "No wordcloud created.",
            }

        # Generate wordcloud
        classifier_config = ClassifierConfig()
        res_wordcloud_generator = services.WordcloudGenerator(classifier_path=f"{classifier_config.classifier_storage_path}/idfs_for_word_cloud.pkl.bz2").generate(
            tokenised_pages=self.__tokenised_pages,
            condition_to_pages=self.__user_resource_usage_result["condition"]["pages"],
        )

        return {
            "wordcloud_base64": res_wordcloud_generator["wordcloud_base64"],
            "log": res_wordcloud_generator["log"],
        }

    def __get_key_protocol_info(self) -> dict:
        """
        Get key protocol info.
        """

        # DF
        df = pd.DataFrame()

        # Parameter
        df["Parameter"] = [
            "Page count",
            "Word count",
            "Average words per page",
            "Condition",
            "Phase",
            "Has the Statistical Analysis Plan been completed?",
            "Has the Effect Estimate been disclosed?",
            "Number of subjects",
            "Countries of investigation",
            "Trial uses simulation for sample size?",
        ]

        # TODO: Value (approved by user if applicable)
        word_count = sum([len(t) for t in self.__tokenised_pages])
        df["Value (approved by user if applicable)"] = [
            f"{len(self.__tokenised_pages)} pages",
            f"{word_count} words",
            f"{word_count / len(self.__tokenised_pages):.1f} words",
            "",  # TODO: condition
            "",  # TODO: phase
            "",  # TODO: yes_or_no(sap)
            "",  # TODO: yes_or_no(effect_estimate)
            "",  # TODO: num_subjects
            "",  # TODO: pretty_print_countries(countries)
            "",  # TODO: yes_or_no(simulation)
        ]

        # Value found by AI
        df["Value found by AI"] = [
            "",
            "",
            "",
            self.__condition_prediction,
            self.__phase_prediction,
            utils.yes_or_no(self.__sap_prediction),
            utils.yes_or_no(self.__effect_estimate_prediction),
            self.__sample_size_prediction,
            utils.pretty_print_countries(countries=self.__country_prediction),
            utils.yes_or_no(self.__simulation_prediction),
        ]

        # Confidence
        df["Confidence"] = [
            "",
            "",
            "",
            self.__condition_score_percentage,
            "",
            self.__sap_score_percentage,
            self.__effect_estimate_score_percentage,
            "",
            "",
            self.__simulation_score_percentage,
        ]

        return df.to_dict("split")

    def __get_risk_calculation(self) -> dict:
        """
        Get risk calculation.
        """

        self.__logs["risk"] = []

        # Score calculation start time
        score_calc_start_time = time.time()

        # Risk nodes
        num_arms_node = self.__ct_risk_nodes_dict["num_arms"]
        phase_node = self.__ct_risk_nodes_dict["phase"]
        sap_node = self.__ct_risk_nodes_dict["sap"]
        effect_estimate_node = self.__ct_risk_nodes_dict["effect_estimate"]
        sample_size_node = self.__ct_risk_nodes_dict["sample_size"]
        international_node = self.__ct_risk_nodes_dict["international"]
        simulation_node = self.__ct_risk_nodes_dict["simulation"]
        constant_node = self.__ct_risk_nodes_dict["constant"]

        # DF
        df = pd.DataFrame()

        # Parameter
        df["Parameter"] = [
            self.__db_document.original_document_name,
            "Trial is for condition",
            "Number of subjects",
            "Lower tertile number of subjects for phase and pathology",
            "Upper tertile number of subjects for phase and pathology",
            "Number of arms",
            "Trial phase",
            "SAP completed?",
            "Effect Estimate disclosed?",
            "Number of subjects low/medium/high",
            "International?",
            "Simulation?",
            "Constant",
        ]

        # Calculate sample size tertile
        res_calculate_sample_size_tertile = self.__calculate_sample_size_tertile()
        sample_size_tertile = res_calculate_sample_size_tertile["sample_size_tertile"]
        lower_tertile = res_calculate_sample_size_tertile["lower_tertile"]
        upper_tertile = res_calculate_sample_size_tertile["upper_tertile"]

        if self.__phase_prediction is None or self.__phase_prediction == -1:
            (
                phase_prediction_str,
                lower_tertile_str,
                upper_tertile_str,
                sample_size_tertile_str,
                sample_size_tertile_name,
            ) = ("-", "-", "-", "-", "-")
        else:
            phase_prediction_str = str(self.__phase_prediction)
            lower_tertile_str = str(lower_tertile)
            upper_tertile_str = str(upper_tertile)
            sample_size_tertile_str = str(sample_size_tertile)
            if sample_size_tertile == 0:
                sample_size_tertile_name = "small"
            elif sample_size_tertile == 1:
                sample_size_tertile_name = "medium"
            else:
                sample_size_tertile_name = "large"

        # Reason
        df["Reason"] = [
            self.__db_document.original_document_name,
            "",
            "",
            "",
            "",
            f"because the trial has {self.__num_arms_prediction} arm{'s'[: self.__num_arms_prediction ^ 1]}",
            f"because the trial is Phase {phase_prediction_str}",
            "because the trial included a Statistical Analysis Plan (SAP)",
            "because the authors disclosed an effect estimate",
            f"because the sample size is {sample_size_tertile_name}",
            "because the trial takes place in multiple countries",
            "because the authors used sample size simulation",
            "CONSTANT",
        ]

        # Value
        df["Value"] = [
            "",
            self.__condition_prediction,
            self.__sample_size_prediction,
            lower_tertile_str,
            upper_tertile_str,
            num_arms_node.value,
            phase_node.value,
            sap_node.value,
            effect_estimate_node.value,
            sample_size_tertile_str,
            international_node.value,
            simulation_node.value,
            constant_node.value,
        ]

        # Weight
        df["Weight"] = [
            "",
            "",
            "",
            "",
            "",
            num_arms_node.weight,
            phase_node.weight,
            sap_node.weight,
            effect_estimate_node.weight,
            sample_size_node.weight,
            international_node.weight,
            simulation_node.weight,
            constant_node.weight,
        ]

        # Score
        df["Score"] = [
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            num_arms_node.score,
            phase_node.score,
            sap_node.score,
            effect_estimate_node.score,
            sample_size_node.score,
            international_node.score,
            simulation_node.score,
            constant_node.score,
        ]

        # The index where score values start appearing in the dataframe
        start_score_index = 5

        # Excel formula
        df["Excel Formula"] = [f"=B{r}*C{r}" if r > start_score_index + 1 else "" for r in range(2, len(df) + 2)]

        self.__logs["risk"].append("Calculating the total score.")
        for idx in range(-1, len(df) - 1):
            if df["Score"].iloc[idx] is not None and (df["Score"].iloc[idx] > 0 or df["Score"].iloc[idx] < 0):
                if df["Reason"].iloc[idx] == "CONSTANT":
                    self.__logs["risk"].append(f"Start at {df['Score'].iloc[idx]} points.")
                else:
                    self.__logs["risk"].append(f"Add {df['Score'].iloc[idx]} points {df['Reason'].iloc[idx]}.")

        # Calculate total score
        total_score = int(df["Score"].dropna().sum())
        df["Score"] = df["Score"].fillna("")

        # Score calculation end time
        score_calc_end_time = time.time()

        self.__logs["risk"].append(f"Total score is {total_score}.")
        self.__logs["risk"].append(
            f"Scores between {self.__risk_threshold.low} and 100 are low risk, scores between {self.__risk_threshold.high} and {self.__risk_threshold.low} are medium risk, and scores between 0 and {self.__risk_threshold.high} are high risk."
        )
        self.__logs["risk"].append(f"Risk is therefore {self.__risk_level.upper()}.")
        self.__logs["risk"].append(f"Score calculated in {score_calc_end_time - score_calc_start_time:.2f} seconds.")

        # Add total score row
        df.loc[len(df)] = [
            f"Total score ({self.__risk_threshold.low}-100=low risk, 0-{self.__risk_threshold.low}=high risk)",
            "",
            "",
            "",
            str(total_score),
            f"=MIN(100,SUM(D{start_score_index + 2}:D{len(df) + 1}))",
        ]

        # Add risk level row
        df.loc[len(df)] = [
            "Risk level",
            "",
            "",
            "",
            self.__risk_level.upper(),
            f'=IF(D{len(df) + 1}<40,"HIGH",IF(D{len(df) + 1}<50,"MEDIUM","LOW"))',
        ]

        # Convert float to int
        df["Value"] = df["Value"].apply(lambda x: int(x) if type(x) is float else x)
        df["Score"] = df["Score"].apply(lambda x: int(x) if type(x) is float else x)

        # Drop column Reason
        df = df.drop("Reason", axis=1)

        return df.to_dict("split")

    def __get_sample_size_tertiles(self) -> dict:
        """
        Get sample size tertiles.
        """

        # DF
        df = pd.DataFrame(self.__tertiles_data_transformed)

        return df.to_dict("split")

    def __get_explanation_overview_of_word_counts_by_page(self) -> dict[str, str]:
        """
        Get explanation overview of word counts by page.

        :returns: A dict response e.g.
         {"graph_base64": ..., "log": ...}.
        """

        # Do not generate graph if falsy
        if not self.__tokenised_pages:
            return {
                "graph_base64": "",
                "log": "No graph created.",
            }

        # Start time
        start_time = time.time()

        # List of word counts
        word_counts: list[int] = [len(tokens) for tokens in self.__tokenised_pages]

        # Total words count
        total_words_count: int = sum(word_counts)

        # DF
        df = pd.DataFrame({"page": self.__page_numbers, "word count": word_counts})

        # Create figure
        fig = px.bar(df, x="page", y="word count")
        fig.update_xaxes(title_text="Page number")
        fig.update_yaxes(title_text="Word count")

        # Figure layout
        fig.update_layout(
            dict1=dict(
                title=f"Word counts of each page. Page count: {len(self.__tokenised_pages)}, word count: {total_words_count}",
                width=850,
                height=450,
                paper_bgcolor="#ffffff",
            )
        )

        # Image buffer
        buffer = io.BytesIO()
        fig.write_image(buffer, engine="kaleido")

        # Encode figure image to base64
        encoded = utils.img_to_base64(buffer.getvalue())

        # End time
        end_time = time.time()

        return {
            "graph_base64": encoded,
            "log": f"Explanation overview of words count by page graph generated in {end_time - start_time:.2f} seconds.",
        }

    def __get_explanation_by_key(
        self,
        key_name: str,
        pages: dict[str, list[float]],
        page_scores: list[float],
        context: dict,
    ) -> HeatMapResult:
        """
        Get explanation by key.

        :param key_name: The key name.
        :param pages: The pages.
        :param page_scores: The page scores.
        :param context: The context.
        :returns: A dict response e.g.
         {"graph_base64": ..., "extra_surtitle_text": ..., "log": ...}.
        """

        # Create heatmap
        res_heatmap = self.__create_heatmap(
            pages=pages,
            key_name=key_name,
            page_scores=page_scores,
            context=context,
        )

        # Log
        res_heatmap.log = self.__prepend_text(current_text=res_heatmap.log, new_text=f"Explanation {key_name}")

        return res_heatmap

    def __create_heatmap(
        self,
        key_name: str,
        pages: dict[str, list[float]],
        page_scores: list[float],
        context: dict,
    ) -> HeatMapResult:
        """
        Create heatmap.

        :param key_name: The key name.
        :param pages: The pages.
        :param page_scores: The page scores.
        :param context: The context.
        :returns: A dict response e.g.
         {"graph_base64": ..., "extra_surtitle_text": ..., "log": ...}.
        """

        # Do not generate graph if falsy
        if not self.__tokenised_pages or not pages:
            return HeatMapResult(
                graph_base64="",
                extra_surtitle_text="",
                context={"key_name": key_name, "items": []},
                log="No graph created.",
            )

        # Start time
        start_time = time.time()

        # Extra surtitle text
        extra_surtitle_text = ""
        total_terms_found = 0
        for page_value in pages.values():
            total_terms_found += len(page_value)
        if total_terms_found == 0:
            extra_surtitle_text = f"No terms relating to {key_name} were found in the document."

        # Page matrix with zeros
        page_matrix = np.zeros(
            shape=(
                len(pages),
                len(self.__tokenised_pages),
            ),
            dtype=np.int32,
        )

        # Words to display in y-axis
        words: list[str] = []

        # Find words and build page matrix
        pages_sorted = sorted(pages.items(), key=lambda x: len(x[1]))
        for word_index, (word, page_numbers_containing_word) in enumerate(pages_sorted):
            for page_number in page_numbers_containing_word:
                page_matrix[word_index, int(page_number)] += 1
            if key_name == "COUNTRY":
                word = word.upper()

            words.append(word)

        # Create figure
        fig = psp.make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            pgo.Heatmap(
                z=page_matrix,
                x=self.__page_numbers,
                y=words,
                showscale=False,
                hoverinfo="text",
                colorscale="Blues",
                textfont={"size": 20},
                colorbar=None,
            ),
            secondary_y=False,
        )

        # Figure layout
        fig.update_layout(
            dict1=dict(
                title=f"Graph of key {key_name} related terms by page number in document",
                width=850,
                height=450,
                paper_bgcolor="#ffffff",
            )
        )
        fig.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))

        # Context
        context_dict: dict = {"key_name": key_name, "items": []}
        if context:
            # Context item pages
            for key, value in context.items():
                context_item_pages: list[str] = []
                if type(value) is str and "Page" in value:
                    start_points = [x.start() for x in re.finditer(r"Page \d+:", value)]
                    if len(start_points) > 1:
                        for i in range(len(start_points)):
                            if i < len(start_points) - 1:
                                end = start_points[i + 1]
                            else:
                                end = len(value)
                            context_item_pages.append(value[start_points[i] : end])
                        if len(context_item_pages) < 1:
                            context_item_pages = [value]

                if not context_item_pages:
                    continue

                # Context item title
                if key_name == "COUNTRY":
                    context_item_title = utils.pretty_print_countries(countries=[key])
                else:
                    context_item_title = key

                # Append context item
                context_dict["items"].append({"title": context_item_title, "pages": context_item_pages})

        # Add probability trace
        if page_scores:
            fig.add_trace(
                pgo.Bar(
                    x=list(range(1, len(page_scores) + 1)),
                    y=page_scores,
                    marker=dict(
                        color="#f64e8b",
                    ),
                    name="probability of each page",
                    showlegend=True,
                ),
                secondary_y=True,
            )
            fig.update_yaxes(
                title_text=f"Probability that {key_name} is on this page",
                secondary_y=True,
                visible=True,
            )
            fig.update_layout(dict1=dict(yaxis2=dict(range=[0, 1])))

        # Axes title text
        fig.update_xaxes(title_text="Page number")
        fig.update_yaxes(title_text="Word mentioned in document", secondary_y=False)

        # Image buffer
        buffer = io.BytesIO()
        fig.write_image(buffer, format="jpeg", engine="kaleido")

        # Encode figure image to base64
        encoded = utils.img_to_base64(buffer.getvalue())

        # End time
        end_time = time.time()

        return HeatMapResult(
            graph_base64=encoded,
            extra_surtitle_text=extra_surtitle_text,
            context=context_dict,
            log=f"Graph generated in {end_time - start_time:.2f} seconds.",
        )

    @staticmethod
    def __tertile_data_transformed(sample_size_tertiles: list[dict[str, Any]]) -> list[dict]:
        """
        Transform tertile data to the following structure: [ {"Phase": 0.0, "HIV lower tertile": 10, "HIV upper tertile": 15, "TB lower tertile": 10, "TB upper tertile": 15}, ...].

        :return: A list of dictionaries per phase with the tertile data.
        """

        # Create a dict of phases
        # E.g. {0.0: [{"HIV lower tertile": 10}, {"HIV upper tertile": 15}, {"TB lower tertile": 10}, ...], 0.5: [...]}
        data_dict: dict[str, list] = {}
        for sample_size_tertile in sample_size_tertiles:
            phase = sample_size_tertile.get("phase")
            if type(phase) is not float:
                continue
            condition = sample_size_tertile.get("condition")
            if condition not in ["HIV", "TB"]:
                continue

            lower_tertile: float = sample_size_tertile["lower_tertile"]
            upper_tertile: float = sample_size_tertile["upper_tertile"]

            if not data_dict.get(phase):
                data_dict[phase] = []

            data_dict[phase].append({f"{condition} lower tertile": lower_tertile})
            data_dict[phase].append({f"{condition} upper tertile": upper_tertile})

        # Convert data_dict to a list of dict
        # E.g. [ {"Phase": 0.0, "HIV lower tertile": 10, "HIV upper tertile": 15, "TB lower tertile": 10, "TB upper tertile": 15}, ...]
        data_list: list[dict] = []
        for phase, list_conditions_tertiles in data_dict.items():
            phase_dict = {"Phase": phase}
            for condition_tertile in list_conditions_tertiles:
                for condition_text, tertile in condition_tertile.items():
                    phase_dict[condition_text] = tertile

            data_list.append(phase_dict)

        return data_list

    def __calculate_sample_size_tertile(self) -> dict[str, str | float]:
        """
        Calculate sample size tertile.

        :returns: Sample size and tertile.
        """

        sample_size_tertile_key_name = "sample_size_tertile"
        lower_tertile_key_name = "lower_tertile"
        upper_tertile_key_name = "upper_tertile"

        if not self.__sample_size_prediction or not self.__phase_prediction or (self.__condition_prediction != "HIV" and self.__condition_prediction != "TB"):
            return {
                sample_size_tertile_key_name: 0,
                lower_tertile_key_name: 0,
                upper_tertile_key_name: 0,
            }

        # Lookup
        if self.__phase_prediction == 4:
            lookup = 7
        else:
            lookup = self.__phase_prediction * 2

        # Lower tertile and upper tertile
        lower = self.__tertiles_data_transformed[lookup][self.__condition_prediction + " lower tertile"]
        upper = self.__tertiles_data_transformed[lookup][self.__condition_prediction + " upper tertile"]

        if self.__sample_size_prediction < lower:
            return {
                sample_size_tertile_key_name: 0,
                lower_tertile_key_name: lower,
                upper_tertile_key_name: upper,
            }
        elif self.__sample_size_prediction < upper:
            return {
                sample_size_tertile_key_name: 1,
                lower_tertile_key_name: lower,
                upper_tertile_key_name: upper,
            }
        else:
            return {
                sample_size_tertile_key_name: 2,
                lower_tertile_key_name: lower,
                upper_tertile_key_name: upper,
            }

    @staticmethod
    def __prepend_text(current_text: str, new_text: str) -> str:
        """
        Prepend text to an existing text.

        :param current_text: The current text.
        :param new_text: The new text.
        """

        if not current_text:
            current_text = ""
        if not new_text:
            new_text = ""

        # Lower the first char
        if current_text:
            current_text = current_text[0].lower() + current_text[1:]

        # Prepend the new text
        if current_text and new_text:
            result = f"{new_text} {current_text}"
        elif current_text:
            result = current_text
        elif new_text:
            result = new_text
        else:
            result = ""

        # Upper the first char
        if result:
            result = result[0].upper() + result[1:]

        # Add dot at end if there isn't one yet
        if result:
            if result[-1] != ".":
                result += "."

        return result

    @staticmethod
    def __score_to_percentage(score: float) -> str:
        """
        Score to percentage e.g. 0.50 -> 50%.

        :param score: The score.
        """

        return f"{100 * score:.1f}%"
