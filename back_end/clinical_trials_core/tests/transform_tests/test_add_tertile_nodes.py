from clinicaltrials.schemas import WeightProfileBase
from clinicaltrials.transform import add_tertile_node_to_risk_nodes


def test_add_tertile_node_to_risk_nodes_value_less_than_lower(
    weight_profile_base: WeightProfileBase
) -> None:
    """
    Test add tertile node when prediction is less than lower tertile.
    """

    meta_id = "sample_size"
    condition = None
    prediction = 50
    phase = None

    risk_nodes = add_tertile_node_to_risk_nodes(
        risk_nodes=[],
        weight_profile_base=weight_profile_base,
        meta_id=meta_id,
        value=prediction,
        condition=condition,
        phase=phase,
    )

    # Only 1 node should be added to risk nodes
    expected_risk_nodes_count = 1

    expected_node_value = 0  # When prediction is less than lower tertile
    expected_node_score = 0  # The node value * the tertile risk weight

    assert (
               len(risk_nodes),
               risk_nodes[0].value,
               risk_nodes[0].score
           ) == (
               expected_risk_nodes_count,
               expected_node_value,
               expected_node_score
           )


def test_add_tertile_node_to_risk_nodes_value_between_lower_and_upper(
    weight_profile_base: WeightProfileBase
) -> None:
    """
    Test add tertile node when prediction is between lower tertile and upper tertile.
    """

    meta_id = "sample_size"
    condition = "HIV"
    prediction = 3001
    phase = 4

    risk_nodes = add_tertile_node_to_risk_nodes(
        risk_nodes=[],
        weight_profile_base=weight_profile_base,
        meta_id=meta_id,
        value=prediction,
        condition=condition,
        phase=phase,
    )

    # Only 1 node should be added to risk nodes
    expected_risk_nodes_count = 1

    expected_node_value = 1  # When prediction is between lower tertile and upper tertile
    expected_node_score = 4.3010752688172  # The node value * the tertile risk weight

    assert (
               len(risk_nodes),
               risk_nodes[0].value,
               risk_nodes[0].score
           ) == (
               expected_risk_nodes_count,
               expected_node_value,
               expected_node_score
           )


def test_add_tertile_node_to_risk_nodes_value_bigger_than_upper(
    weight_profile_base: WeightProfileBase
) -> None:
    """
    Test add tertile node when prediction is bigger than upper tertile.
    """

    meta_id = "sample_size"
    condition = "TB"
    prediction = 100
    phase = 0.5

    risk_nodes = add_tertile_node_to_risk_nodes(
        risk_nodes=[],
        weight_profile_base=weight_profile_base,
        meta_id=meta_id,
        value=prediction,
        condition=condition,
        phase=phase,
    )

    # Only 1 node should be added to risk nodes
    expected_risk_nodes_count = 1

    expected_node_value = 2  # When prediction is bigger than upper tertile
    expected_node_score = 8.6021505376344  # The node value * the tertile risk weight

    assert (
               len(risk_nodes),
               risk_nodes[0].value,
               risk_nodes[0].score
           ) == (
               expected_risk_nodes_count,
               expected_node_value,
               expected_node_score
           )
