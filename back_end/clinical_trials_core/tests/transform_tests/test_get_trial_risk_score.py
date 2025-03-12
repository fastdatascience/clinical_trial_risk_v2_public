from clinicaltrials.schemas import WeightProfileBase, CTNode
from clinicaltrials.transform import get_trial_risk_score


def test_get_trial_risk_score_67_level_low(weight_profile_base: WeightProfileBase):
    """
    Test get trial risk score 67 and level LOW.
    """

    risk_nodes: list[CTNode] = [
        CTNode.create_node(
            feature="sap",
            description="",
            value=1,
            weight=11,
        ),
        CTNode.create_node(
            feature="simulation",
            description="",
            value=8,
            weight=6,
        ),
        CTNode.create_node(
            feature="sample_size",
            description="",
            value=215,
            weight=0,
        ),
        CTNode.create_node(
            feature="num_endpoints",
            description="",
            value=2,
            weight=4,
        ),
    ]

    risk_score, risk_level = get_trial_risk_score(
        ct_node=risk_nodes,
        weight_profile_base=weight_profile_base,
    )

    expected_risk_score = 67.0  # Sum of all risk node scores
    expected_risk_level = "LOW"  # When the score is between low threshold and 100

    assert (risk_score, risk_level) == (expected_risk_score, expected_risk_level)


def test_get_trial_risk_score_45_level_medium(weight_profile_base: WeightProfileBase):
    """
    Test get trial risk score 45 and level MEDIUM.
    """

    risk_nodes: list[CTNode] = [
        CTNode.create_node(
            feature="sap",
            description="",
            value=1,
            weight=10,
        ),
        CTNode.create_node(
            feature="simulation",
            description="",
            value=6,
            weight=5,
        ),
        CTNode.create_node(
            feature="sample_size",
            description="",
            value=215,
            weight=0,
        ),
        CTNode.create_node(
            feature="num_endpoints",
            description="",
            value=1,
            weight=5,
        ),
    ]

    risk_score, risk_level = get_trial_risk_score(
        ct_node=risk_nodes,
        weight_profile_base=weight_profile_base,
    )

    expected_risk_score = 45  # Sum of all risk node scores
    expected_risk_level = "MEDIUM"  # When the score is between high threshold and low threshold

    assert (risk_score, risk_level) == (expected_risk_score, expected_risk_level)


def test_get_trial_risk_score_19_level_high(weight_profile_base: WeightProfileBase):
    """
    Test get trial risk score 19 and level HIGH.
    """

    risk_nodes: list[CTNode] = [
        CTNode.create_node(
            feature="sap",
            description="",
            value=1,
            weight=11,
        ),
        CTNode.create_node(
            feature="simulation",
            description="",
            value=0,
            weight=6,
        ),
        CTNode.create_node(
            feature="sample_size",
            description="",
            value=215,
            weight=0,
        ),
        CTNode.create_node(
            feature="num_endpoints",
            description="",
            value=2,
            weight=4,
        ),
    ]

    risk_score, risk_level = get_trial_risk_score(
        ct_node=risk_nodes,
        weight_profile_base=weight_profile_base,
    )

    expected_risk_score = 19.0  # Sum of all risk node scores
    expected_risk_level = "HIGH"  # When the score is between 0 and high threshold

    assert (risk_score, risk_level) == (expected_risk_score, expected_risk_level)


def test_get_trial_risk_score_below_0(weight_profile_base: WeightProfileBase):
    """
    Test get trial risk score below 0.
    """

    risk_nodes: list[CTNode] = [
        CTNode.create_node(
            feature="sap",
            description="",
            value=-1000,  # This should cause the score to be < 0
            weight=11,
        ),
        CTNode.create_node(
            feature="simulation",
            description="",
            value=0,
            weight=6,
        ),
        CTNode.create_node(
            feature="sample_size",
            description="",
            value=215,
            weight=0,
        ),
        CTNode.create_node(
            feature="num_endpoints",
            description="",
            value=2,
            weight=4,
        ),
    ]

    risk_score, risk_level = get_trial_risk_score(
        ct_node=risk_nodes,
        weight_profile_base=weight_profile_base,
    )

    expected_risk_score = 0  # When the score calculation is below 0, the score should be capped at 0
    expected_risk_level = "HIGH"  # When the score is between 0 and high threshold

    assert (risk_score, risk_level) == (expected_risk_score, expected_risk_level)


def test_get_trial_risk_score_above_100(weight_profile_base: WeightProfileBase):
    """
    Test get trial risk score above 100.
    """

    risk_nodes: list[CTNode] = [
        CTNode.create_node(
            feature="sap",
            description="",
            value=1000,  # This should cause the score to be > 100
            weight=11,
        ),
        CTNode.create_node(
            feature="simulation",
            description="",
            value=0,
            weight=6,
        ),
        CTNode.create_node(
            feature="sample_size",
            description="",
            value=215,
            weight=0,
        ),
        CTNode.create_node(
            feature="num_endpoints",
            description="",
            value=2,
            weight=4,
        ),
    ]

    risk_score, risk_level = get_trial_risk_score(
        ct_node=risk_nodes,
        weight_profile_base=weight_profile_base,
    )

    expected_risk_score = 100  # When the score calculation is above 100, the score should be capped at 100
    expected_risk_level = "LOW" # When the score is between low threshold and 100

    assert (risk_score, risk_level) == (expected_risk_score, expected_risk_level)
