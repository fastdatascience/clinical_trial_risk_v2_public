from clinicaltrials.core import Metadata
from clinicaltrials.schemas import WeightProfileBase
from clinicaltrials.transform import create_rac_nodes


def test_create_rac_nodes_has_num_drugs(
    weight_profile_base: WeightProfileBase,
    user_resource_usage: dict,
    metadata: list[Metadata],
) -> None:
    """
    Test create risk and cost nodes has num_drugs node.
    """

    cost_nodes, risk_nodes = create_rac_nodes(
        metadata=metadata,
        result=user_resource_usage,
        weight_profile_base=weight_profile_base,
        selected_param={},
    )

    # The user resource usage has drug, thus we expect the nodes to contain the feature num_drugs
    expected_cost_nodes_count = 1
    expected_risk_nodes_count = 1

    assert (
               len([x for x in cost_nodes if x.feature == "num_drugs"]),
               len([x for x in risk_nodes if x.feature == "num_drugs"])
           ) == (
               expected_cost_nodes_count,
               expected_risk_nodes_count
           )


def test_create_rac_nodes_has_multiple_drugs(
    weight_profile_base: WeightProfileBase,
    user_resource_usage: dict,
    metadata: list[Metadata],
) -> None:
    """
    Test create risk and cost nodes has multiple_drugs node.
    """

    cost_nodes, risk_nodes = create_rac_nodes(
        metadata=metadata,
        result=user_resource_usage,
        weight_profile_base=weight_profile_base,
        selected_param={},
    )

    # The user resource usage has drug, thus we expect the nodes to contain the feature multiple_drugs
    expected_cost_nodes_count = 1
    expected_risk_nodes_count = 1

    assert (
               len([x for x in cost_nodes if x.feature == "multiple_drugs"]),
               len([x for x in risk_nodes if x.feature == "multiple_drugs"])
           ) == (
               expected_cost_nodes_count,
               expected_risk_nodes_count,
           )


def test_create_rac_nodes_has_international(
    weight_profile_base: WeightProfileBase,
    user_resource_usage: dict,
    metadata: list[Metadata],
) -> None:
    """
    Test create risk and cost nodes has the node international.
    """

    cost_nodes, risk_nodes = create_rac_nodes(
        metadata=metadata,
        result=user_resource_usage,
        weight_profile_base=weight_profile_base,
        selected_param={},
    )

    # The user resource usage has country, thus we expect the nodes to contain the feature international
    expected_cost_nodes_count = 1
    expected_risk_nodes_count = 1

    assert (
               len([x for x in cost_nodes if x.feature == "international"]),
               len([x for x in risk_nodes if x.feature == "international"]),
           ) == (
               expected_cost_nodes_count,
               expected_risk_nodes_count
           )


def test_create_rac_nodes_has_lmic(
    weight_profile_base: WeightProfileBase,
    user_resource_usage: dict,
    metadata: list[Metadata],
) -> None:
    """
    Test create risk and cost nodes has the node lmic.
    """

    cost_nodes, risk_nodes = create_rac_nodes(
        metadata=metadata,
        result=user_resource_usage,
        weight_profile_base=weight_profile_base,
        selected_param={},
    )

    # The user resource usage has country, thus we expect the nodes to contain the feature lmic
    expected_cost_nodes_count = 1
    expected_risk_nodes_count = 1

    assert (
               len([x for x in cost_nodes if x.feature == "lmic"]),
               len([x for x in risk_nodes if x.feature == "lmic"]),
           ) == (
               expected_cost_nodes_count,
               expected_risk_nodes_count,
           )


def test_create_rac_nodes_has_constant(
    weight_profile_base: WeightProfileBase,
    user_resource_usage: dict,
    metadata: list[Metadata],
) -> None:
    """
    Test create risk and cost nodes has the node constant.
    """

    cost_nodes, risk_nodes = create_rac_nodes(
        metadata=metadata,
        result=user_resource_usage,
        weight_profile_base=weight_profile_base,
        selected_param={},
    )

    # The constant node should always be included in the nodes
    expected_cost_nodes_count = 1
    expected_risk_nodes_count = 1

    assert (
               bool([x for x in cost_nodes if x.feature == "constant"]),
               bool([x for x in risk_nodes if x.feature == "constant"])
           ) == (
               expected_cost_nodes_count,
               expected_risk_nodes_count
           )


def test_create_rac_nodes_has_condition_cost(
    weight_profile_base: WeightProfileBase,
    user_resource_usage: dict,
    metadata: list[Metadata],
) -> None:
    """
    Test create risk and cost nodes has the node condition cost.
    """

    cost_nodes, risk_nodes = create_rac_nodes(
        metadata=metadata,
        result=user_resource_usage,
        weight_profile_base=weight_profile_base,
        selected_param={},
    )

    # The condition_cost node should always be included in the nodes
    expected_cost_nodes_count = 1
    expected_risk_nodes_count = 0

    assert (
               len([x for x in cost_nodes if x.feature == "condition_cost"]),
               len([x for x in risk_nodes if x.feature == "condition_cost"]),
           ) == (
               expected_cost_nodes_count,
               expected_risk_nodes_count,
           )


def test_create_rac_nodes_has_trial_size(
    weight_profile_base: WeightProfileBase,
    user_resource_usage: dict,
    metadata: list[Metadata],
) -> None:
    """
    Test create risk and cost nodes has the node trial_size.
    """

    cost_nodes, risk_nodes = create_rac_nodes(
        metadata=metadata,
        result=user_resource_usage,
        weight_profile_base=weight_profile_base,
        selected_param={},
    )

    # The cost nodes should never include the trial_size node
    expected_cost_nodes_count = 0

    # The user resource usage has condition, phase and sample_size, thus we expect the trial_size node to be included
    # in the risk nodes.
    expected_risk_nodes_count = 1

    assert (
               len([x for x in cost_nodes if x.feature == "trial_size"]),
               len([x for x in risk_nodes if x.feature == "trial_size"])
           ) == (
               expected_cost_nodes_count,
               expected_risk_nodes_count
           )


def test_create_rac_nodes_has_tertiles(
    weight_profile_base: WeightProfileBase,
    user_resource_usage: dict,
    metadata: list[Metadata],
) -> None:
    """
    Test create risk and cost nodes has the tertile nodes.
    """

    cost_nodes, risk_nodes = create_rac_nodes(
        metadata=metadata,
        result=user_resource_usage,
        weight_profile_base=weight_profile_base,
        selected_param={},
    )

    # The user resource usage has 5 features that are tertiles, thus we expect there to be 5 tertile nodes in risk nodes
    expected_tertile_risk_nodes_count = 5

    assert len([x for x in risk_nodes if x.feature.endswith("_tertile")]) == expected_tertile_risk_nodes_count


def test_create_rac_nodes_has_multiple_regimen(
    weight_profile_base: WeightProfileBase,
    user_resource_usage: dict,
    metadata: list[Metadata],
) -> None:
    """
    Test create risk and cost nodes has multiple nodes for regimen.
    """

    cost_nodes, risk_nodes = create_rac_nodes(
        metadata=metadata,
        result=user_resource_usage,
        weight_profile_base=weight_profile_base,
        selected_param={},
    )

    # The user resource usage has the feature regimen, thus these features are expected to be included in the nodes
    expected_node_features = {
        "regimen=doses_per_day",
        "regimen=days_between_doses",
        "regimen=multiple_doses_per_day"
    }

    # There should be 3 regimen nodes
    expected_regimen_cost_nodes_count = len(expected_node_features)
    expected_regimen_risk_nodes_count = len(expected_node_features)

    assert (
               len([x.feature for x in cost_nodes if x.feature in expected_node_features]),
               len([x.feature for x in risk_nodes if x.feature in expected_node_features])
           ) == (
               expected_regimen_cost_nodes_count,
               expected_regimen_risk_nodes_count
           )
