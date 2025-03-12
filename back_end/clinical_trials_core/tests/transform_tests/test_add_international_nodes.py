from clinicaltrials.schemas import WeightProfileBase
from clinicaltrials.transform import add_international_nodes


# Note: A node value of 0 means that it is not international, a node value of 1 means that it is international.

def test_add_international_nodes_empty_list(weight_profile_base: WeightProfileBase) -> None:
    """
    Test add international nodes when prediction is an empty list.
    """

    prediction = []

    cost_nodes, risk_nodes = add_international_nodes(
        cost_nodes=[],
        risk_nodes=[],
        weight_profile_base=weight_profile_base,
        prediction=prediction,
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


def test_add_international_nodes_1_country(weight_profile_base: WeightProfileBase) -> None:
    """
    Test add international nodes when there's only 1 country in prediction.
    """

    prediction = ["Country1"]

    cost_nodes, risk_nodes = add_international_nodes(
        cost_nodes=[],
        risk_nodes=[],
        weight_profile_base=weight_profile_base,
        prediction=prediction,
        result={},
    )

    # Only 1 node should be added to cost nodes and risk nodes
    expected_cost_nodes_count = 1
    expected_risk_nodes_count = 1

    # There's 1 country, thus we expect the node value to be 0
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


def test_add_international_nodes_3_countries(weight_profile_base: WeightProfileBase) -> None:
    """
    Test add international nodes when there's more than 1 country in prediction.
    """

    prediction = ["Country1", "Country2", "Country3"]

    cost_nodes, risk_nodes = add_international_nodes(
        cost_nodes=[],
        risk_nodes=[],
        weight_profile_base=weight_profile_base,
        prediction=prediction,
        result={},
    )

    # Only 1 node should be added to cost nodes and risk nodes
    expected_cost_nodes_count = 1
    expected_risk_nodes_count = 1

    # There are 3 countries, thus we expect the node value to be 1
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
