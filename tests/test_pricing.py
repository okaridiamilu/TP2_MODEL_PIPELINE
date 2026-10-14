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


# --- apply_promo_code : cas normaux ---

from datetime import date  # noqa: E402

from src.pricing import PROMO_CODES, apply_promo_code  # noqa: E402

VALID_CODES = [
    {"code": "P20", "type": "percentage", "value": 20, "minOrder": 15, "expiresAt": "2099-12-31"},
    {"code": "F5", "type": "fixed", "value": 5, "minOrder": 20, "expiresAt": "2099-12-31"},
    {"code": "P100", "type": "percentage", "value": 100, "minOrder": 0, "expiresAt": "2099-12-31"},
    {"code": "F10", "type": "fixed", "value": 10, "minOrder": 0, "expiresAt": "2099-12-31"},
    {"code": "OLD", "type": "percentage", "value": 10, "minOrder": 0, "expiresAt": "2020-01-01"},
    {
        "code": "TODAY",
        "type": "percentage",
        "value": 50,
        "minOrder": 0,
        "expiresAt": date.today().isoformat(),
    },
]


def test_promo_code_should_apply_percentage_discount() -> None:
    result = apply_promo_code(50, "P20", VALID_CODES)

    assert result == {"discount": 10, "total": 40}


def test_promo_code_should_apply_fixed_discount() -> None:
    result = apply_promo_code(30, "F5", VALID_CODES)

    assert result == {"discount": 5, "total": 25}


def test_promo_code_should_accept_order_at_min_order() -> None:
    # subtotal = minOrder pile : le minimum est respecte
    result = apply_promo_code(15, "P20", VALID_CODES)

    assert result["total"] == 12


def test_promo_code_should_accept_code_expiring_today() -> None:
    # choix de design : la date d'expiration est inclusive
    result = apply_promo_code(10, "TODAY", VALID_CODES)

    assert result == {"discount": 5, "total": 5}


# --- apply_promo_code : refus et erreurs ---


def test_promo_code_should_raise_when_unknown_code() -> None:
    with pytest.raises(ValueError, match="inconnu"):
        apply_promo_code(50, "INEXISTANT", VALID_CODES)


def test_promo_code_should_raise_when_expired_code() -> None:
    with pytest.raises(ValueError, match="expire"):
        apply_promo_code(50, "OLD", VALID_CODES)


def test_promo_code_should_raise_when_order_below_min_order() -> None:
    with pytest.raises(ValueError, match="minimum"):
        apply_promo_code(10, "P20", VALID_CODES)


def test_promo_code_should_raise_when_negative_subtotal() -> None:
    with pytest.raises(ValueError, match="negatif"):
        apply_promo_code(-5, None, VALID_CODES)


# --- apply_promo_code : cas limites dangereux ---


def test_promo_code_should_never_go_below_zero_with_fixed_discount() -> None:
    # fixed 10 EUR sur une commande de 5 EUR : total 0, pas negatif
    result = apply_promo_code(5, "F10", VALID_CODES)

    assert result == {"discount": 5, "total": 0}


def test_promo_code_should_allow_full_percentage_discount() -> None:
    # 100% de reduction : total 0
    result = apply_promo_code(50, "P100", VALID_CODES)

    assert result == {"discount": 50, "total": 0}


def test_promo_code_should_handle_zero_subtotal() -> None:
    # subtotal 0 avec un code sans minimum : discount 0, total 0
    result = apply_promo_code(0, "P100", VALID_CODES)

    assert result == {"discount": 0, "total": 0}


def test_promo_code_should_apply_no_discount_when_code_is_none() -> None:
    result = apply_promo_code(42, None, VALID_CODES)

    assert result == {"discount": 0, "total": 42}


def test_promo_code_should_apply_no_discount_when_code_is_empty() -> None:
    result = apply_promo_code(42, "", VALID_CODES)

    assert result == {"discount": 0, "total": 42}


def test_promo_code_should_work_with_module_promo_codes() -> None:
    # les vrais codes promo de l'application
    result = apply_promo_code(50, "BIENVENUE20", PROMO_CODES)

    assert result == {"discount": 10, "total": 40}
