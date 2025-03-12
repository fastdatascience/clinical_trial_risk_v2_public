from typing import Any

from clinicaltrials.constants import LMIC_COUNTRIES
from clinicaltrials.core import Metadata
from clinicaltrials.enums import TrialRiskLevel, TrialSize
from clinicaltrials.schemas import CTNode, WeightProfileBase
from clinicaltrials.utils import find_matching_tertile_by_priority, list_has_2_items_or_more, list_has_1_item_or_more


def create_rac_nodes(
    metadata: list[Metadata],
    result: dict[str, Any],
    weight_profile_base: WeightProfileBase,
    selected_param: dict
) -> tuple[list[CTNode], list[CTNode]]:
    """
    Create risk and cost nodes.

    :param metadata: Clinical Trials metadata.
    :param result: The document processing result.
    :param weight_profile_base: The weight profile.
    :param selected_param: The selected param.
    :returns: The cost nodes and the risk nodes.
    """

    # Filter metadata list
    metadata = [] if metadata is None else metadata
    modules_to_skip = {"ner"}
    metadata = [x for x in metadata if x.id not in modules_to_skip]

    # Get condition and phase
    condition_prediction: str | None = result.get("condition", {}).get("prediction")
    phase_prediction: float | None = result.get("phase", {}).get("prediction")

    # Loop through each metadata and create the cost nodes and risk nodes
    cost_nodes: list[CTNode] = []
    risk_nodes: list[CTNode] = []
    for meta in metadata:
        meta_id = meta.id

        prediction = result.get(meta.id, {}).get("prediction")
        selected_value = selected_param.get(meta.id, prediction)
        value = meta.get_value(selected_value, prediction)
        description = meta.get_description(selected_value=prediction)

        # Add drug nodes
        if meta_id == "drug":
            cost_nodes, risk_nodes = add_num_drugs_nodes(
                cost_nodes=cost_nodes,
                risk_nodes=risk_nodes,
                weight_profile_base=weight_profile_base,
                prediction=prediction,
                description=description,
            )
            cost_nodes, risk_nodes = add_multiple_drugs_nodes(
                cost_nodes=cost_nodes,
                risk_nodes=risk_nodes,
                weight_profile_base=weight_profile_base,
                prediction=prediction,
                description=description,
            )

        # Add country nodes
        elif meta_id == "country":
            cost_nodes, risk_nodes = add_international_nodes(
                cost_nodes=cost_nodes,
                risk_nodes=risk_nodes,
                weight_profile_base=weight_profile_base,
                prediction=prediction,
                result=result,
            )
            cost_nodes, risk_nodes = add_lmic_nodes(
                cost_nodes=cost_nodes,
                risk_nodes=risk_nodes,
                weight_profile_base=weight_profile_base,
                prediction=prediction,
                result=result,
            )

        # Add nodes for module with multiple predictions
        elif meta.has_multiple_predictions:
            cost_nodes, risk_nodes = add_nodes_for_module_multiple_predictions(
                cost_nodes=cost_nodes,
                risk_nodes=risk_nodes,
                weight_profile_base=weight_profile_base,
                meta_id=meta_id,
                prediction=prediction,
            )

        # Add nodes for all other modules
        else:
            cost_nodes.append(
                CTNode.create_node(
                    feature=meta_id,
                    description=description,
                    value=value,
                    weight=weight_profile_base.get_cost_by_name(name=meta_id),
                )
            )
            risk_nodes.append(
                CTNode.create_node(
                    feature=meta_id,
                    description=description,
                    value=value,
                    weight=weight_profile_base.get_risk_by_name(name=meta_id),
                )
            )

        # Add tertile node to risk nodes if module is tertile
        if meta.is_tertile:
            risk_nodes = add_tertile_node_to_risk_nodes(
                risk_nodes=risk_nodes,
                weight_profile_base=weight_profile_base,
                meta_id=meta_id,
                value=value,
                condition=condition_prediction,
                phase=phase_prediction,
            )

    # Add constant nodes
    cost_nodes, risk_nodes = add_constant_nodes(
        cost_nodes=cost_nodes,
        risk_nodes=risk_nodes,
        weight_profile_base=weight_profile_base,
    )

    # Add trial size node to risk nodes
    risk_nodes = add_trial_size_node_to_risk_nodes(
        risk_nodes=risk_nodes,
        weight_profile_base=weight_profile_base,
    )

    # Add condition cost node
    cost_nodes = add_condition_cost_node(
        cost_nodes=cost_nodes,
        weight_profile_base=weight_profile_base,
    )

    return cost_nodes, risk_nodes


def add_condition_cost_node(
    cost_nodes: list[CTNode],
    weight_profile_base: WeightProfileBase
) -> list[CTNode]:
    """
    Add condition cost node.
    """

    # Calculate the total condition cost
    condition = CTNode.get_description_by_feature(nodes=cost_nodes, feature="condition")
    condition_cost = calculate_total_conditions_cost(
        conditions=[condition],
        weight_profile_base=weight_profile_base,
    )

    cost_nodes.append(
        CTNode(
            feature="condition_cost",
            description=f"Cost contribution from the condition {condition}",
            value=1,
            weight=condition_cost,
            score=condition_cost,
        )
    )

    return cost_nodes


def add_trial_size_node_to_risk_nodes(
    risk_nodes: list[CTNode],
    weight_profile_base: WeightProfileBase
) -> list[CTNode]:
    """
    Add trial size node to risk nodes.
    """

    condition_risk_description = CTNode.get_description_by_feature(feature="condition", nodes=risk_nodes)
    phase_risk_value = CTNode.get_value_by_feature(feature="phase", nodes=risk_nodes)
    sample_size_risk_value = CTNode.get_value_by_feature(feature="sample_size", nodes=risk_nodes)

    if condition_risk_description is not None and phase_risk_value is not None and sample_size_risk_value is not None:
        trial_size: TrialSize = TrialSize.get_trial_size(
            condition=condition_risk_description,
            phase=phase_risk_value,
            sample_size=int(sample_size_risk_value),
            sample_size_tertiles=weight_profile_base.tertiles["sample_size_tertiles"]
        )
        trial_size_weight = weight_profile_base.get_risk_by_name(name="sample_size_tertile", default=10)
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

    return risk_nodes


def add_tertile_node_to_risk_nodes(
    risk_nodes: list[CTNode],
    weight_profile_base: WeightProfileBase,
    meta_id: str,
    value: int,
    condition: str | None,
    phase: float | None,
) -> list[CTNode]:
    """
    Add tertile node to risk nodes.
    """

    tertiles = weight_profile_base.tertiles.get(f"{meta_id}_tertiles")
    if not tertiles:
        print(f"Could not find tertile data for {meta_id}.")

        return risk_nodes

    # Find the first matching tertile based on priority
    matching_tertile = find_matching_tertile_by_priority(
        priority=[(condition, phase), ("*", phase), (condition, "*"), ("*", "*")],
        tertiles=tertiles,
    )

    # Tertile not found
    if not matching_tertile:
        print(f"Could not find tertile data for {meta_id}.")

        return risk_nodes

    # Tertile value (should always be 0, 1 or 2)
    if value < matching_tertile.lower_tertile:
        tertile_value = 0
    elif value < matching_tertile.upper_tertile:
        tertile_value = 1
    else:
        tertile_value = 2

    tertile_key = f"{meta_id}_tertile"

    # Get tertile risk weight
    tertile_risk_weight = weight_profile_base.get_risk_by_name(name=tertile_key)

    risk_nodes.append(
        CTNode(
            feature=tertile_key,
            description=f"Tertile of {meta_id}",
            value=tertile_value,
            weight=tertile_risk_weight,
            score=tertile_value * tertile_risk_weight,
        )
    )

    return risk_nodes


def add_international_nodes(
    cost_nodes: list[CTNode],
    risk_nodes: list[CTNode],
    weight_profile_base: WeightProfileBase,
    prediction: Any,
    result: dict,
) -> tuple[list[CTNode], list[CTNode]]:
    """
    Add international nodes.
    """

    key = "international"
    if prediction is None:
        value = 0
    else:
        value = list_has_2_items_or_more(value=prediction)

    # Description
    if value:
        description = "Is international"
    else:
        description = "Is not international"

    # Add international nodes
    cost_nodes.append(
        CTNode.create_node(
            feature=key,
            description=description,
            value=value,
            weight=weight_profile_base.get_cost_by_name(name=key, default=0),
        )
    )
    risk_nodes.append(
        CTNode.create_node(
            feature=key,
            description=description,
            value=value,
            weight=weight_profile_base.get_risk_by_name(name=key, default=0),
        )
    )

    # TODO: These need to be added to the result dictionary itself to ensure that the data read on the client side remains consistent
    result.setdefault(key, {}).setdefault("prediction", value)

    return cost_nodes, risk_nodes


def add_lmic_nodes(
    cost_nodes: list[CTNode],
    risk_nodes: list[CTNode],
    weight_profile_base: WeightProfileBase,
    prediction: Any,
    result: dict,
) -> tuple[list[CTNode], list[CTNode]]:
    """
    Add lmic nodes.
    """

    key = "lmic"
    weight = weight_profile_base.model_dump().get("cost_risk_models", {}).get("country", {}).get(key, 0)

    # Check if it's in any low to medium income country
    if prediction is not None:
        countries_in_trial = LMIC_COUNTRIES.intersection(prediction)
    else:
        countries_in_trial = set()

    # Value
    if countries_in_trial is not None:
        value = list_has_1_item_or_more(value=countries_in_trial)
    else:
        value = 0

    # Description
    if value:
        description = f"Is in low to medium income country, countries found {', '.join(prediction)}"
    else:
        description = "Is not in low to medium income country"

    # Calculate score
    score = value * weight

    # Add lmic nodes
    cost_nodes.append(
        CTNode(
            feature=key,
            description=description,
            value=value,
            weight=weight,
            score=score,
        )
    )
    risk_nodes.append(
        CTNode(
            feature=key,
            description=description,
            value=value,
            weight=weight,
            score=score,
        )
    )

    # TODO: These need to be added to the result dictionary itself to ensure that the data read on the client side remains consistent
    result.setdefault(key, {}).setdefault("prediction", value)

    return cost_nodes, risk_nodes


def add_nodes_for_module_multiple_predictions(
    cost_nodes: list[CTNode],
    risk_nodes: list[CTNode],
    weight_profile_base: WeightProfileBase,
    meta_id: str,
    prediction: Any,
) -> tuple[list[CTNode], list[CTNode]]:
    """
    Add nodes for module with multiple predictions.
    E.g. if there are 3 predictions, this function will add 3 new nodes.
    """

    if type(prediction) is dict:
        dummy_weights = weight_profile_base.get_cost_risk_model_for_dummy_variable(key=f"{meta_id}=")
        for key, value in prediction.items():
            # Create dummy key e.g. if the meta_id is "regimen" and the key is "days_between_doses", the dummy key is
            # regimen=days_between_doses. This is also the key name for its cost/risk model in the weight profile.
            dummy_key = f"{meta_id}={key}"

            description: str = key.replace("_", " ")
            description: str = description[:1].upper() + description[1:]

            cost_nodes.append(
                CTNode.create_node(
                    feature=dummy_key,
                    description=description,
                    value=value,
                    weight=dummy_weights.get_cost_by_name(name=dummy_key),
                )
            )
            risk_nodes.append(
                CTNode.create_node(
                    feature=dummy_key,
                    description=description,
                    value=value,
                    weight=dummy_weights.get_risk_by_name(name=dummy_key),
                )
            )

    return cost_nodes, risk_nodes


def add_num_drugs_nodes(
    cost_nodes: list[CTNode],
    risk_nodes: list[CTNode],
    weight_profile_base: WeightProfileBase,
    prediction: Any,
    description: str,
) -> tuple[list[CTNode], list[CTNode]]:
    """
    Add num_drugs nodes to cost nodes and risk nodes.
    """

    num_drugs_key = "num_drugs"
    if type(prediction) is list:
        value = len(prediction)
    else:
        value = 1

    cost_nodes.append(
        CTNode.create_node(
            feature=num_drugs_key,
            description=description,
            value=value,
            weight=weight_profile_base.get_cost_by_name(num_drugs_key)
        )
    )
    risk_nodes.append(
        CTNode.create_node(
            feature=num_drugs_key,
            description=description,
            value=value,
            weight=weight_profile_base.get_risk_by_name(num_drugs_key)
        )
    )

    return cost_nodes, risk_nodes


def add_multiple_drugs_nodes(
    cost_nodes: list[CTNode],
    risk_nodes: list[CTNode],
    weight_profile_base: WeightProfileBase,
    prediction: Any,
    description: str,
) -> tuple[list[CTNode], list[CTNode]]:
    """
    Add multiple_drugs nodes to cost nodes and risk nodes.
    """

    multiple_drugs_key = "multiple_drugs"
    is_multiple = list_has_2_items_or_more(value=prediction)

    cost_nodes.append(
        CTNode.create_node(
            feature=multiple_drugs_key,
            description=description,
            value=is_multiple,
            weight=weight_profile_base.get_cost_by_name(multiple_drugs_key)
        )
    )
    risk_nodes.append(
        CTNode.create_node(
            feature=multiple_drugs_key,
            description=description,
            value=is_multiple,
            weight=weight_profile_base.get_risk_by_name(multiple_drugs_key)
        )
    )

    return cost_nodes, risk_nodes


def add_constant_nodes(
    cost_nodes: list[CTNode],
    risk_nodes: list[CTNode],
    weight_profile_base: WeightProfileBase,
) -> tuple[list[CTNode], list[CTNode]]:
    """
    Add constant nodes to cost nodes and risk nodes.
    """

    key = "constant"
    value = 1

    cost_nodes.append(
        CTNode.create_node(
            feature=key,
            description=key,
            value=value,
            weight=weight_profile_base.get_cost_by_name(key)
        ),
    )
    risk_nodes.append(
        CTNode.create_node(
            feature=key,
            description=key,
            value=value,
            weight=weight_profile_base.get_risk_by_name(key)
        ),
    )

    return cost_nodes, risk_nodes


def calculate_total_conditions_cost(weight_profile_base: WeightProfileBase, conditions: list[str]) -> float:
    """
    Calculate the total cost contribution from the specified conditions.

    Parameters:
        conditions (list of str): A list of condition names.
        weight_profile_base: Weight profile base.

    Returns:
        float: The total cost contribution from the conditions
    """

    total_cost = 0.0
    weight_profile_base_condition = weight_profile_base.get_cost_risk_model_for_dummy_variable(
        "condition=",
    )

    for condition in conditions:
        cost = weight_profile_base_condition.get_cost_by_name(name=condition)
        total_cost += cost

    return total_cost


def get_total_cost_or_risk_per_participant(
    ct_nodes: list[CTNode],
    ignore_features: tuple[str, ...] = (),
) -> int | float:
    """
    Calculate the total cost per participant by summing the scores of CTNodes,
    excluding nodes with features listed in ignore_features
    """

    filtered_nodes = CTNode.filter_nodes(nodes=ct_nodes, ignore_features=ignore_features)

    return sum(node.score for node in filtered_nodes)


def get_total_trial_cost(ct_nodes: list[CTNode]) -> tuple[float, float]:
    """
    Calculate the total trial cost and total cost per participant.
    """
    sample_size = CTNode.get_value_by_feature(nodes=ct_nodes, feature="sample_size")

    if sample_size is None:
        raise ValueError("No sample size found")

    total_cost_per_participant = get_total_cost_or_risk_per_participant(ct_nodes=ct_nodes)
    trial_cost = float(total_cost_per_participant) * float(sample_size)

    return trial_cost, float(total_cost_per_participant)


def get_trial_risk_score(
    ct_node: list[CTNode],
    weight_profile_base: WeightProfileBase,
) -> tuple[float, str]:
    """
    Determine the trial risk score based on the total cost per participant.

    The total risk score is calculated using the `get_total_cost_or_risk_per_participant` function,
    and it is clamped to ensure it falls within the range [0, 100]. Based on this clamped score,
    the corresponding TrialRiskLevel ("Low", "Medium", or "High") is determined.

    Args:
        ct_node (List[CTNode]): A list of CTNode instances representing clinical trial nodes.
        weight_profile_base: Weight profile.

    Returns:
        str: The label of the corresponding TrialRiskLevel ("Low", "Medium", or "High").
    """

    total_risk_score = get_total_cost_or_risk_per_participant(ct_node)
    risk_level = TrialRiskLevel.is_within_threshold(total_risk_score, weight_profile_base.risk_thresholds)

    total_risk_score = max(0, min(100, total_risk_score))

    # * If no specific thresholds are met, return MEDIUM
    return total_risk_score, risk_level.label
