from clinicaltrials.schemas import WeightProfileBase
from clinicaltrials.transform import calculate_total_conditions_cost


def test_calculate_total_conditions_cost_cancer(weight_profile_base: WeightProfileBase) -> None:
    """
    Test calculate total conditions cost for CANCER.
    """

    conditions = ["CANCER"]

    total_cost = calculate_total_conditions_cost(
        weight_profile_base=weight_profile_base,
        conditions=conditions
    )

    # The current weight profile does not include condition=CANCER, thus the expected cost is 0
    expected_total_cost = 0

    assert expected_total_cost == total_cost


def test_calculate_total_conditions_cost_hiv(weight_profile_base: WeightProfileBase) -> None:
    """
    Test calculate total conditions cost for HIV.
    """

    conditions = ["HIV"]

    total_cost = calculate_total_conditions_cost(
        weight_profile_base=weight_profile_base,
        conditions=conditions
    )

    # HIV cost
    expected_total_cost = 5016.014796040056

    assert expected_total_cost == total_cost


def test_calculate_total_conditions_cost_hiv_covid(weight_profile_base: WeightProfileBase) -> None:
    """
    Test calculate total conditions cost for HIV and COVID.
    """

    conditions = ["HIV", "COVID"]

    total_cost = calculate_total_conditions_cost(
        weight_profile_base=weight_profile_base,
        conditions=conditions
    )

    # HIV cost + COVID cost
    expected_total_cost = 3851.696513376613

    assert expected_total_cost == total_cost


def test_calculate_total_conditions_cost_tb_pol_hiv(weight_profile_base: WeightProfileBase) -> None:
    """
    Test calculate total conditions cost for TB, POL and HIV.
    """

    conditions = ["TB", "POL", "HIV"]

    total_cost = calculate_total_conditions_cost(
        weight_profile_base=weight_profile_base,
        conditions=conditions
    )

    # TB cost + POL cost + HIV cost
    expected_total_cost = 80251.72583697918

    assert expected_total_cost == total_cost


def test_calculate_total_conditions_cost_empty_list(weight_profile_base: WeightProfileBase) -> None:
    """
    Test calculate total conditions cost with empty list.
    """

    conditions = []

    total_cost = calculate_total_conditions_cost(
        weight_profile_base=weight_profile_base,
        conditions=conditions
    )

    # No conditions to calculate total costs, thus the expected cost is 0
    expected_total_cost = 0

    assert expected_total_cost == total_cost
