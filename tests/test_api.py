"""Tests d'integration de l'API (src/app.py).

Contrairement aux tests unitaires, on teste la route COMPLETE :
requete HTTP -> route -> logique metier -> reponse JSON.
Flask test_client() envoie les requetes en memoire, sans port.
"""

from src.app import create_app, reset_orders

VALID_ORDER = {
    "items": [{"name": "Pizza", "price": 12.50, "quantity": 2}],
    "distance": 5,
    "weight": 2,
    "hour": 15,
    "dayOfWeek": "tuesday",
}


def setup_function() -> None:
    # reinitialise les commandes AVANT chaque test pour qu'ils soient
    # independants les uns des autres
    reset_orders()


def client():
    return create_app().test_client()


# --- POST /orders/simulate : 7 tests ---


def test_simulate_should_return_price_detail_for_valid_order() -> None:
    response = client().post("/orders/simulate", json=VALID_ORDER)

    assert response.status_code == 200
    assert response.json == {
        "subtotal": 25.00,
        "discount": 0,
        "deliveryFee": 3.00,
        "surge": 1.0,
        "total": 28.00,
    }


def test_simulate_should_apply_valid_promo_code() -> None:
    response = client().post(
        "/orders/simulate", json={**VALID_ORDER, "promoCode": "BIENVENUE20"}
    )

    assert response.status_code == 200
    assert response.json["discount"] == 5.00
    assert response.json["total"] == 23.00


def test_simulate_should_reject_expired_promo_code() -> None:
    response = client().post(
        "/orders/simulate", json={**VALID_ORDER, "promoCode": "EXPIRE10"}
    )

    assert response.status_code == 400
    assert "expire" in response.json["error"]


def test_simulate_should_reject_empty_cart() -> None:
    response = client().post("/orders/simulate", json={**VALID_ORDER, "items": []})

    assert response.status_code == 400
    assert "vide" in response.json["error"]


def test_simulate_should_reject_out_of_zone_distance() -> None:
    response = client().post("/orders/simulate", json={**VALID_ORDER, "distance": 15})

    assert response.status_code == 400
    assert "10 km" in response.json["error"]


def test_simulate_should_reject_order_when_closed() -> None:
    response = client().post("/orders/simulate", json={**VALID_ORDER, "hour": 23})

    assert response.status_code == 400
    assert "ferme" in response.json["error"]


def test_simulate_should_multiply_delivery_fee_on_friday_evening() -> None:
    response = client().post(
        "/orders/simulate", json={**VALID_ORDER, "hour": 20, "dayOfWeek": "friday"}
    )

    assert response.status_code == 200
    assert response.json["surge"] == 1.8
    assert response.json["deliveryFee"] == 5.40  # 3.00 * 1.8


# --- POST /orders : 5 tests ---


def test_create_order_should_return_201_with_id() -> None:
    response = client().post("/orders", json=VALID_ORDER)

    assert response.status_code == 201
    assert response.json["id"] == 1
    assert response.json["total"] == 28.00


def test_created_order_should_be_retrievable_by_id() -> None:
    post_response = client().post("/orders", json=VALID_ORDER)

    get_response = client().get(f"/orders/{post_response.json['id']}")

    assert get_response.status_code == 200
    assert get_response.json["items"] == VALID_ORDER["items"]


def test_two_orders_should_have_different_ids() -> None:
    first = client().post("/orders", json=VALID_ORDER)
    second = client().post("/orders", json=VALID_ORDER)

    assert first.json["id"] != second.json["id"]


def test_invalid_order_should_return_400() -> None:
    response = client().post("/orders", json={**VALID_ORDER, "items": []})

    assert response.status_code == 400


def test_invalid_order_should_not_be_stored() -> None:
    client().post("/orders", json={**VALID_ORDER, "items": []})

    # aucune commande n'a du etre enregistree : l'ID 1 n'existe pas
    assert client().get("/orders/1").status_code == 404


# --- GET /orders/:id : 3 tests ---


def test_get_order_should_return_complete_order() -> None:
    client().post("/orders", json=VALID_ORDER)

    response = client().get("/orders/1")

    assert response.status_code == 200
    assert response.json["id"] == 1
    assert response.json["subtotal"] == 25.00
    assert response.json["total"] == 28.00


def test_get_order_should_return_404_for_unknown_id() -> None:
    response = client().get("/orders/999")

    assert response.status_code == 404
    assert response.json == {"error": "Commande introuvable"}


def test_get_order_should_return_complete_structure() -> None:
    client().post("/orders", json=VALID_ORDER)

    order = client().get("/orders/1").json

    for key in ("id", "items", "distance", "weight", "subtotal", "discount", "deliveryFee", "surge", "total"):
        assert key in order


# --- POST /promo/validate : 5 tests ---


def test_promo_validate_should_confirm_valid_code() -> None:
    response = client().post(
        "/promo/validate", json={"code": "BIENVENUE20", "amount": 50}
    )

    assert response.status_code == 200
    assert response.json["valid"] is True
    assert response.json["discount"] == 10
    assert response.json["total"] == 40


def test_promo_validate_should_explain_expired_code() -> None:
    response = client().post(
        "/promo/validate", json={"code": "EXPIRE10", "amount": 50}
    )

    assert response.status_code == 400
    assert "expire" in response.json["error"]


def test_promo_validate_should_explain_order_below_minimum() -> None:
    # LIVRAISON5 exige 20 EUR minimum
    response = client().post(
        "/promo/validate", json={"code": "LIVRAISON5", "amount": 10}
    )

    assert response.status_code == 400
    assert "minimum" in response.json["error"]


def test_promo_validate_should_return_404_for_unknown_code() -> None:
    response = client().post(
        "/promo/validate", json={"code": "INEXISTANT", "amount": 50}
    )

    assert response.status_code == 404


def test_promo_validate_should_return_400_without_code() -> None:
    response = client().post("/promo/validate", json={"amount": 50})

    assert response.status_code == 400
    assert "code" in response.json["error"]
