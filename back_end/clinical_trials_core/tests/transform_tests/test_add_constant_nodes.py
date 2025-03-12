from clinicaltrials.schemas import WeightProfileBase
from clinicaltrials.transform import add_constant_nodes


def test_add_constant_nodes(weight_profile_base: WeightProfileBase) -> None:
    """
    Test add constant nodes.
    """

    cost_nodes, risk_nodes = add_constant_nodes(
        cost_nodes=[],
        risk_nodes=[],
        weight_profile_base=weight_profile_base
    )

    # Only 1 node should be added to cost nodes and risk nodes
    expected_cost_nodes_count = 1
    expected_risk_nodes_count = 1

    expected_cost_node_score = 27530.38952250608  # 1 * constant cost weight
    expected_risk_node_score = -5.55555555555555  # 1 * constant risk weight

    assert (
               len(cost_nodes),
               len(risk_nodes),
               cost_nodes[0].score,
               risk_nodes[0].score
           ) == (
               expected_cost_nodes_count,
               expected_risk_nodes_count,
               expected_cost_node_score,
               expected_risk_node_score
           )
