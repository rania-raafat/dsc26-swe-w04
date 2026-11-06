
import pytest

from nour_transfers.rules import (
    can_transfer,
    days_of_cover,
    priority,
)


# M01: The sender must keep at least the reserve.
def test_can_transfer_allows_exact_reserve_boundary():
    assert can_transfer(40, 30, 10) is True


def test_can_transfer_rejects_below_reserve():
    assert can_transfer(40, 31, 10) is False


# M02: Quantity must be at least one.
def test_can_transfer_rejects_zero_quantity():
    assert can_transfer(40, 0, 10) is False


def test_can_transfer_rejects_negative_quantity():
    assert can_transfer(40, -1, 10) is False


# M05: Zero sales means indefinite stock coverage.
@pytest.mark.parametrize("stock", [0, 12, 100])
def test_zero_sales_returns_none(stock):
    assert days_of_cover(stock, 0) is None


def test_days_of_cover_uses_true_division():
    result = days_of_cover(10, 4)
    assert result == 2.5
    assert isinstance(result, float)


def test_negative_stock_raises_value_error():
    with pytest.raises(ValueError):
        days_of_cover(-1, 1)


def test_negative_sales_raise_value_error():
    with pytest.raises(ValueError):
        days_of_cover(10, -1)


# M03: Only chronic items can be urgent.
def test_non_chronic_item_with_low_cover_is_high():
    assert priority(False, 2) == "high"


def test_chronic_item_below_three_days_is_urgent():
    assert priority(True, 2.99) == "urgent"


# M04: Exactly three days is NOT urgent.
def test_exactly_three_days_is_high():
    assert priority(True, 3) == "high"


def test_exactly_seven_days_is_normal():
    assert priority(False, 7) == "normal"


def test_none_cover_is_normal():
    assert priority(True, None) == "normal"
