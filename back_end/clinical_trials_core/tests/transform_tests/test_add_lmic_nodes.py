from clinicaltrials.schemas import WeightProfileBase
from clinicaltrials.transform import add_lmic_nodes


# Note: A node value of 0 means that it is not lmic, a node value of 1 means that it is lmic.

def test_add_lmic_nodes_empty_list(weight_profile_base: WeightProfileBase) -> None:
    """
    Test add lmic nodes when prediction is an empty list.
    """

    cost_nodes, risk_nodes = add_lmic_nodes(
        cost_nodes=[],
        risk_nodes=[],
        weight_profile_base=weight_profile_base,
        prediction=[],
        result={},
    )

    # Only 1 node should be added to cost nodes and risk nodes
    expected_cost_nodes_count = 1
    expected_risk_nodes_count = 1

    # Prediction is an empty list, thus we expect the node value to be 0
    expected_node_value = 0

    assert (
               len(cost_nodes),
               len(risk_nodes),
               cost_nodes[0].value,
               risk_nodes[0].value
           ) == (
               expected_cost_nodes_count,
               expected_risk_nodes_count,
               expected_node_value,
               expected_node_value
           )


def test_add_lmic_nodes_1_lmic_country(weight_profile_base: WeightProfileBase) -> None:
    """
    Test add lmic nodes when 1 country in prediction is in lmic countries.
    """

    prediction = ["US", "VN"]

    cost_nodes, risk_nodes = add_lmic_nodes(
        cost_nodes=[],
        risk_nodes=[],
        weight_profile_base=weight_profile_base,
        prediction=prediction,
        result={},
    )

    # Only 1 node should be added to cost nodes and risk nodes
    expected_cost_nodes_count = 1
    expected_risk_nodes_count = 1

    # 1 country is found in lmic countries, thus we expect the node value to be 1
    expected_node_value = 1

    assert (
               len(cost_nodes),
               len(risk_nodes),
               cost_nodes[0].value,
               risk_nodes[0].value
           ) == (
               expected_cost_nodes_count,
               expected_risk_nodes_count,
               expected_node_value,
               expected_node_value
           )


def test_add_lmic_nodes_all_lmic_country(weight_profile_base: WeightProfileBase) -> None:
    """
    Test add lmic nodes when all countries in prediction are in lmic countries.
    """

    prediction = ["GH", "VN"]

    cost_nodes, risk_nodes = add_lmic_nodes(
        cost_nodes=[],
        risk_nodes=[],
        weight_profile_base=weight_profile_base,
        prediction=prediction,
        result={},
    )

    # Only 1 node should be added to cost nodes and risk nodes
    expected_cost_nodes_count = 1
    expected_risk_nodes_count = 1

    # All countries are lmic countries, thus we expect the node value to be 1
    expected_node_value = 1

    assert (
               len(cost_nodes),
               len(risk_nodes),
               cost_nodes[0].value,
               risk_nodes[0].value
           ) == (
               expected_cost_nodes_count,
               expected_risk_nodes_count,
               expected_node_value,
               expected_node_value
           )


def test_add_lmic_nodes_no_lmic_country(weight_profile_base: WeightProfileBase) -> None:
    """
    Test add lmic nodes when the countries in prediction are not lmic countries.
    """

    prediction = ["US", "NL"]

    cost_nodes, risk_nodes = add_lmic_nodes(
        cost_nodes=[],
        risk_nodes=[],
        weight_profile_base=weight_profile_base,
        prediction=prediction,
        result={},
    )

    # Only 1 node should be added to cost nodes and risk nodes
    expected_cost_nodes_count = 1
    expected_risk_nodes_count = 1

    # None of the countries intersect with lmic countries, thus we expect the node value to be 0
    expected_node_value = 0

    assert (
               len(cost_nodes),
               len(risk_nodes),
               cost_nodes[0].value,
               risk_nodes[0].value
           ) == (
               expected_cost_nodes_count,
               expected_risk_nodes_count,
               expected_node_value,
               expected_node_value
           )
