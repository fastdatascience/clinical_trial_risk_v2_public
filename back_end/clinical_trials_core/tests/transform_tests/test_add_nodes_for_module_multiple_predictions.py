from clinicaltrials.schemas import CTNode, WeightProfileBase
from clinicaltrials.transform import add_nodes_for_module_multiple_predictions


def test_add_nodes_for_module_multiple_predictions_3(weight_profile_base: WeightProfileBase) -> None:
    """
    Test add nodes for module with multiple predictions (3).
    """

    cost_nodes: list[CTNode] = [
        CTNode.create_node(
            feature="constant",
            description="",
            value=1,
            weight=27530,
        ),
    ]
    risk_nodes: list[CTNode] = [
        CTNode.create_node(
            feature="constant",
            description="",
            value=1,
            weight=27530,
        ),
    ]

    meta_id = "regimen"
    prediction = {
        "doses_per_day": 1,
        "days_between_doses": 0,
        "multiple_doses_per_day": 2,
    }

    cost_nodes, risk_nodes = add_nodes_for_module_multiple_predictions(
        cost_nodes=cost_nodes,
        risk_nodes=risk_nodes,
        weight_profile_base=weight_profile_base,
        meta_id=meta_id,
        prediction=prediction,
    )

    # There are 3 items in the dictionary, the constant node + thus we expect 3 new nodes
    expected_cost_nodes_count = 4
    expected_risk_nodes_count = 4

    # The nodes should contain these features
    expected_feature_types = sorted([
        "constant",
        "regimen=doses_per_day",
        "regimen=days_between_doses",
        "regimen=multiple_doses_per_day",
    ])

    assert (
               len(cost_nodes),
               len(risk_nodes),
               sorted([x.feature for x in cost_nodes]),
               sorted([x.feature for x in risk_nodes])
           ) == (
               expected_cost_nodes_count,
               expected_risk_nodes_count,
               expected_feature_types,
               expected_feature_types
           )


def test_add_nodes_for_module_multiple_predictions_not_dict(weight_profile_base: WeightProfileBase) -> None:
    """
    Test add nodes for module with multiple predictions when prediction is not of type dict.
    """

    cost_nodes: list[CTNode] = [
        CTNode.create_node(
            feature="constant",
            description="",
            value=1,
            weight=27530,
        ),
    ]
    risk_nodes: list[CTNode] = [
        CTNode.create_node(
            feature="constant",
            description="",
            value=1,
            weight=27530,
        ),
    ]

    meta_id = "condition"
    prediction = "HIV"

    cost_nodes, risk_nodes = add_nodes_for_module_multiple_predictions(
        cost_nodes=cost_nodes,
        risk_nodes=risk_nodes,
        weight_profile_base=weight_profile_base,
        meta_id=meta_id,
        prediction=prediction,
    )

    # Since prediction is not a dict, no new nodes should be added, thus we expect only the constant node
    expected_cost_nodes_count = 1
    expected_risk_nodes_count = 1

    # The nodes should contain these features
    expected_feature_types = sorted(["constant"])

    assert (
               len(cost_nodes),
               len(risk_nodes),
               sorted([x.feature for x in cost_nodes]),
               sorted([x.feature for x in risk_nodes])
           ) == (
               expected_cost_nodes_count,
               expected_risk_nodes_count,
               expected_feature_types,
               expected_feature_types
           )


def test_add_nodes_for_module_multiple_predictions_values(weight_profile_base: WeightProfileBase) -> None:
    """
    Test add nodes for module with multiple predictions and their values.
    """

    meta_id = "regimen"

    prediction = {
        "doses_per_day": 1,
        "days_between_doses": 0,
        "multiple_doses_per_day": 2,
    }

    cost_nodes, risk_nodes = add_nodes_for_module_multiple_predictions(
        cost_nodes=[],
        risk_nodes=[],
        weight_profile_base=weight_profile_base,
        meta_id=meta_id,
        prediction=prediction,
    )

    # Only 3 nodes should be added to cost nodes and risk nodes
    expected_cost_nodes_count = 3
    expected_risk_nodes_count = 3

    expected_regimen_doses_per_day_value = 1
    expected_regimen_days_between_doses_value = 0
    expected_regimen_multiple_doses_per_day_value = 2

    # Create a dictionary from nodes for feature lookup
    cost_nodes_dict = {c.feature: c.value for c in cost_nodes}
    risk_nodes_dict = {r.feature: r.value for r in risk_nodes}

    assert (
               len(cost_nodes),
               len(risk_nodes),
               expected_regimen_doses_per_day_value,
               expected_regimen_days_between_doses_value,
               expected_regimen_multiple_doses_per_day_value,
               expected_regimen_doses_per_day_value,
               expected_regimen_days_between_doses_value,
               expected_regimen_multiple_doses_per_day_value,
           ) == (
               expected_cost_nodes_count,
               expected_risk_nodes_count,
               cost_nodes_dict["regimen=doses_per_day"],
               cost_nodes_dict["regimen=days_between_doses"],
               cost_nodes_dict["regimen=multiple_doses_per_day"],
               risk_nodes_dict["regimen=doses_per_day"],
               risk_nodes_dict["regimen=days_between_doses"],
               risk_nodes_dict["regimen=multiple_doses_per_day"],
           )
