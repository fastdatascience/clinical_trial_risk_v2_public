from clinicaltrials.schemas import WeightProfileBase, CTNode
from clinicaltrials.transform import add_trial_size_node_to_risk_nodes


def test_add_trial_size_node_to_risk_nodes(weight_profile_base: WeightProfileBase) -> None:
    """
    Test add trial size node to risk nodes.
    """

    risk_nodes: list[CTNode] = [
        CTNode.create_node(
            feature="condition",
            description="HIV",
            value=1,
            weight=0,
        ),
        CTNode.create_node(
            feature="phase",
            description="",
            value=1,
            weight=4.3010752688172,
        ),
        CTNode.create_node(
            feature="sample_size",
            description="",
            value=155,
            weight=0,
        )
    ]

    risk_nodes = add_trial_size_node_to_risk_nodes(
        risk_nodes=risk_nodes,
        weight_profile_base=weight_profile_base,
    )

    # The tertile value by condition HIV and phase 1
    # The sample size is above upper tertile, thus we expect the value to be 2
    expected_value = 2

    # The risk weight of sample_size_tertile
    expected_weight = 4.3010752688172

    # value * weight
    expected_score = expected_value * expected_weight

    assert (
               risk_nodes[3].value,
               risk_nodes[3].weight,
               risk_nodes[3].score
           ) == (
               expected_value,
               expected_weight,
               expected_score
           )


def test_add_trial_size_node_to_risk_nodes_node_missing(weight_profile_base: WeightProfileBase) -> None:
    """
    Test add trial size node to risk nodes when a required node for the calculation is missing.
    """

    risk_nodes: list[CTNode] = [
        CTNode.create_node(
            feature="phase",
            description="",
            value=1,
            weight=4.3010752688172,
        ),
        CTNode.create_node(
            feature="sample_size",
            description="",
            value=155,
            weight=0,
        )
    ]

    risk_nodes = add_trial_size_node_to_risk_nodes(
        risk_nodes=risk_nodes,
        weight_profile_base=weight_profile_base,
    )

    # If a required node is missing, no new node should be added, the nodes in the list should remain the same
    expected_node_features = ["sample_size", "phase"]

    assert sorted([x.feature for x in risk_nodes]) == sorted(expected_node_features)
