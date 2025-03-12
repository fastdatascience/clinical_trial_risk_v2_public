from clinicaltrials.schemas import CTNode
from clinicaltrials.transform import get_total_cost_or_risk_per_participant


def test_get_total_cost_or_risk_per_participant_3_nodes() -> None:
    """
    Test get total cost or risk per participant from 3 nodes.
    """

    cost_nodes: list[CTNode] = [
        CTNode.create_node(
            feature="constant",
            description="",
            value=1,
            weight=27530,
        ),
        CTNode.create_node(
            feature="num_drugs",
            description="",
            value=7,
            weight=0,
        ),
        CTNode.create_node(
            feature="num_interventions_total",
            description="",
            value=110,
            weight=38,
        ),
    ]

    total_cost = get_total_cost_or_risk_per_participant(
        ct_nodes=cost_nodes,
        ignore_features=(),
    )

    # Sum of all cost node scores
    expected_total_cost = 31710

    assert expected_total_cost == total_cost


def test_get_total_cost_or_risk_per_participant_with_ignored_node() -> None:
    """
    Test get total cost or risk per participant with a node ignored.
    """

    cost_nodes: list[CTNode] = [
        CTNode.create_node(
            feature="constant",
            description="",
            value=1,
            weight=27530,
        ),
        CTNode.create_node(
            feature="num_drugs",
            description="",
            value=7,
            weight=0,
        ),
        CTNode.create_node(
            feature="num_interventions_total",
            description="",
            value=110,
            weight=38,
        ),
    ]

    total_cost = get_total_cost_or_risk_per_participant(
        ct_nodes=cost_nodes,
        ignore_features=("num_interventions_total",),
    )

    # Sum of all cost node scores, except the node to ignore
    expected_total_cost = 27530

    assert expected_total_cost == total_cost


def test_get_total_cost_or_risk_per_participant_empty_list() -> None:
    """
    Test get total cost or risk per participant with an empty nodes list.
    """

    total_cost = get_total_cost_or_risk_per_participant(
        ct_nodes=[],
        ignore_features=(),
    )

    # Sum of all cost node scores
    expected_total_cost = 0

    assert expected_total_cost == total_cost
