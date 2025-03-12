from clinicaltrials.schemas import WeightProfileBase, CTNode
from clinicaltrials.transform import add_condition_cost_node


def test_add_condition_cost_node_hiv(weight_profile_base: WeightProfileBase) -> None:
    """
    Test add condition cost node when condition is HIV.
    """

    cost_nodes: list[CTNode] = [
        CTNode.create_node(
            feature="condition",
            description="HIV",
            value=1,
            weight=0,
        )
    ]

    cost_nodes = add_condition_cost_node(
        cost_nodes=cost_nodes,
        weight_profile_base=weight_profile_base,
    )

    # Only 1 node should be added to cost nodes, thus we expect the condition node + the condition cost node
    expected_cost_nodes_count = 2

    expected_score = 5016.014796040056  # 1 * condition=HIV cost weight

    assert (len(cost_nodes), cost_nodes[1].score) == (expected_cost_nodes_count, expected_score)


def test_add_condition_cost_node_cancer(weight_profile_base: WeightProfileBase) -> None:
    """
    Test add condition cost node when condition is CANCER.
    """

    cost_nodes: list[CTNode] = [
        CTNode.create_node(
            feature="condition",
            description="CANCER",
            value=1,
            weight=0,
        )
    ]

    cost_nodes = add_condition_cost_node(
        cost_nodes=cost_nodes,
        weight_profile_base=weight_profile_base,
    )

    # Only 1 node should be added to cost nodes, thus we expect the condition node + the condition cost node
    expected_cost_nodes_count = 2

    # The current weight profile does not include condition=CANCER, thus the expected score is 0
    expected_score = 0

    assert (len(cost_nodes), cost_nodes[1].score) == (expected_cost_nodes_count, expected_score)


def test_add_condition_cost_node_no_condition(weight_profile_base: WeightProfileBase) -> None:
    """
    Test add condition cost node when there is no condition node.
    """

    cost_nodes = add_condition_cost_node(
        cost_nodes=[],
        weight_profile_base=weight_profile_base,
    )

    # Only 1 node should be added to cost nodes
    expected_cost_nodes_count = 1

    # There is no condition node, thus we expect the score to be 0
    expected_score = 0

    assert (len(cost_nodes), cost_nodes[0].score) == (expected_cost_nodes_count, expected_score)
