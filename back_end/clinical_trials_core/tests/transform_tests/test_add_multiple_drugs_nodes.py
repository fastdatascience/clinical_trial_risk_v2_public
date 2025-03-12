from clinicaltrials.schemas import WeightProfileBase
from clinicaltrials.transform import add_multiple_drugs_nodes


# Note: A multiple_drugs node value of 1 means that there are more than 1 drug, a node value of 0 means there's 1
# drug or less.

def test_add_multiple_drugs_nodes_empty_list(weight_profile_base: WeightProfileBase) -> None:
    """
    Test add multiple_drugs nodes with empty list.
    """

    cost_nodes, risk_nodes = add_multiple_drugs_nodes(
        cost_nodes=[],
        risk_nodes=[],
        weight_profile_base=weight_profile_base,
        prediction=[],
        description="",
    )

    # Only 1 node should be added to cost nodes and risk nodes
    expected_cost_nodes_count = 1
    expected_risk_nodes_count = 1

    # Prediction has 0 drugs, so we expect the node value to be 0
    expected_multiple_drugs_cost_node_value = 0
    expected_multiple_drugs_risk_node_value = 0

    assert (
               len(cost_nodes),
               len(risk_nodes),
               cost_nodes[0].value,
               risk_nodes[0].value,
           ) == (
               expected_cost_nodes_count,
               expected_risk_nodes_count,
               expected_multiple_drugs_cost_node_value,
               expected_multiple_drugs_risk_node_value
           )


def test_add_multiple_drugs_nodes_3(weight_profile_base: WeightProfileBase) -> None:
    """
    Test add multiple_drugs nodes with prediction containing 3 drugs.
    """

    prediction = ["drug1", "drug2", "drug3"]

    cost_nodes, risk_nodes = add_multiple_drugs_nodes(
        cost_nodes=[],
        risk_nodes=[],
        weight_profile_base=weight_profile_base,
        prediction=prediction,
        description="",
    )

    # Only 1 node should be added to cost nodes and risk nodes
    expected_cost_nodes_count = 1
    expected_risk_nodes_count = 1

    # Prediction has 3 drugs, so we expect the node value to be 1
    expected_cost_node_value = 1
    expected_risk_node_value = 1

    assert (
               len(cost_nodes),
               len(risk_nodes),
               cost_nodes[0].value,
               risk_nodes[0].value,
           ) == (
               expected_cost_nodes_count,
               expected_risk_nodes_count,
               expected_cost_node_value,
               expected_risk_node_value
           )
