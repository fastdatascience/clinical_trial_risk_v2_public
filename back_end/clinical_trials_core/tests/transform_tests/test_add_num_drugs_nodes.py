from clinicaltrials.schemas import WeightProfileBase
from clinicaltrials.transform import add_num_drugs_nodes


# Note: A num_drugs node value of 3 means that there are 3 drugs

def test_add_num_drugs_nodes_empty_list(weight_profile_base: WeightProfileBase) -> None:
    """
    Test add num_drugs nodes with empty list.
    """

    cost_nodes, risk_nodes = add_num_drugs_nodes(
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
    expected_cost_node_value = 0
    expected_risk_node_value = 0

    assert (
               len(cost_nodes),
               len(risk_nodes),
               cost_nodes[0].value,
               risk_nodes[0].value
           ) == (
               expected_cost_nodes_count,
               expected_risk_nodes_count,
               expected_cost_node_value,
               expected_risk_node_value,
           )


def test_add_num_drugs_nodes_3(weight_profile_base: WeightProfileBase) -> None:
    """
    Test add num_drugs and multiple_drugs nodes with prediction containing 3 drugs.
    """

    prediction = ["drug1", "drug2", "drug3"]

    cost_nodes, risk_nodes = add_num_drugs_nodes(
        cost_nodes=[],
        risk_nodes=[],
        weight_profile_base=weight_profile_base,
        prediction=prediction,
        description="",
    )

    # Only 1 node should be added to cost nodes and risk nodes
    expected_cost_nodes_count = 1
    expected_risk_nodes_count = 1

    # Prediction has 3 drugs, so we expect the node value to be 3
    expected_cost_node_value = 3
    expected_risk_node_value = 3

    assert (
               len(cost_nodes),
               len(risk_nodes),
               cost_nodes[0].value,
               risk_nodes[0].value,
           ) == (
               expected_cost_nodes_count,
               expected_risk_nodes_count,
               expected_cost_node_value,
               expected_risk_node_value,
           )
