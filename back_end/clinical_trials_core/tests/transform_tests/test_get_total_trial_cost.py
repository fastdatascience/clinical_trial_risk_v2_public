from clinicaltrials.schemas import CTNode
from clinicaltrials.transform import get_total_trial_cost


def test_get_total_trial_cost_4_nodes() -> None:
    """
    Test get total trial cost from 4 nodes.
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
        CTNode.create_node(
            feature="sample_size",
            description="",
            value=215,
            weight=0,
        ),
    ]

    trial_cost, total_cost_per_participant = get_total_trial_cost(
        ct_nodes=cost_nodes
    )

    expected_trial_cost = 6817650  # Sum of all cost node scores * sample size
    expected_total_cost_per_participant = 31710  # Sum of all cost node scores

    assert (expected_trial_cost, total_cost_per_participant) == (trial_cost, expected_total_cost_per_participant)


def test_get_total_trial_cost_empty_list() -> None:
    """
    Test get total trial cost with an empty nodes list.
    """

    cost_nodes: list[CTNode] = [
        CTNode.create_node(
            feature="num_interventions_total",
            description="",
            value=110,
            weight=38,
        )
    ]

    # The sample_size node is required, should throw ValueError exception when it is not included
    value_error_exception_thrown = False

    try:
        get_total_trial_cost(ct_nodes=cost_nodes)
    except ValueError:
        value_error_exception_thrown = True

    assert value_error_exception_thrown == True
