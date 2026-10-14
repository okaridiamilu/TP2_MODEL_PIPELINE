"""Tests unitaires du moteur de tarification (src/pricing.py)."""

import pytest

from src.pricing import calculate_delivery_fee


# --- calculate_delivery_fee : cas normaux ---


def test_delivery_fee_should_be_base_price_when_short_distance() -> None:
    # 2 km, 1 kg : inclus dans la base
    assert calculate_delivery_fee(2, 1) == 2.00


def test_delivery_fee_should_add_per_km_beyond_3_km() -> None:
    # 7 km : 2.00 + (7-3) * 0.50 = 4.00
    assert calculate_delivery_fee(7, 3) == 4.00


def test_delivery_fee_should_add_heavy_surcharge() -> None:
    # 5 km, 8 kg : 2.00 + 2 * 0.50 + 1.50 = 4.50
    assert calculate_delivery_fee(5, 8) == 4.50


def test_delivery_fee_should_calculate_6km_2kg_as_3_50() -> None:
    # verifie a la main : 2.00 + (6-3) * 0.50 = 3.50
    assert calculate_delivery_fee(6, 2) == 3.50


def test_delivery_fee_should_calculate_10km_6kg_as_7_00() -> None:
    # verifie a la main : 2.00 + 7 * 0.50 + 1.50 = 7.00
    assert calculate_delivery_fee(10, 6) == 7.00


# --- calculate_delivery_fee : cas limites ---


def test_delivery_fee_should_charge_base_when_exactly_3_km() -> None:
    # 3 km pile : encore inclus dans la base
    assert calculate_delivery_fee(3, 2) == 2.00


def test_delivery_fee_should_accept_exactly_10_km() -> None:
    # 10 km pile : accepte (10 inclus), 2.00 + 7 * 0.50 = 5.50
    assert calculate_delivery_fee(10, 2) == 5.50


def test_delivery_fee_should_not_surcharge_when_exactly_5_kg() -> None:
    # 5 kg pile : pas de supplement (strictement superieur a 5 seulement)
    assert calculate_delivery_fee(2, 5) == 2.00


def test_delivery_fee_should_be_valid_when_distance_is_zero() -> None:
    # distance 0 : commande sur place, base quand meme
    assert calculate_delivery_fee(0, 1) == 2.00


# --- calculate_delivery_fee : cas d'erreur ---


def test_delivery_fee_should_raise_when_distance_over_10_km() -> None:
    with pytest.raises(ValueError, match="distance superieure"):
        calculate_delivery_fee(15, 1)


def test_delivery_fee_should_raise_when_negative_distance() -> None:
    with pytest.raises(ValueError, match="negatifs"):
        calculate_delivery_fee(-1, 2)


def test_delivery_fee_should_raise_when_negative_weight() -> None:
    with pytest.raises(ValueError, match="negatifs"):
        calculate_delivery_fee(2, -1)
