"""API REST du moteur de tarification.

Ce fichier ne fait QUE configurer l'application (factory pattern) :
aucun demarrage de serveur ici. Le demarrage est dans server.py.
"""

from flask import Flask, jsonify, request

from src.pricing import PROMO_CODES, apply_promo_code, calculate_order_total

# Commandes enregistrees en memoire : {id: commande}
orders: dict[int, dict] = {}
_next_order_id = 1


def reset_orders() -> None:
    """Vide les commandes en memoire (utilise par les tests)."""
    orders.clear()
    globals()["_next_order_id"] = 1


def _get_order_payload() -> tuple[dict, dict | None]:
    """Extrait et valide le corps commun aux routes de commandes.

    Retourne (donnees, reponse d'erreur). L'erreur est None si le
    corps est un objet JSON exploitable.
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return {}, ({"error": "Le corps de la requete doit etre un objet JSON"}, 400)
    return data, None


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def home() -> dict[str, str]:
        return {"message": "Moteur de tarification de livraison"}

    # Simule le prix d'une commande SANS l'enregistrer
    @app.post("/orders/simulate")
    def simulate_order():
        data, error = _get_order_payload()
        if error:
            return error
        try:
            detail = calculate_order_total(
                data.get("items"),
                data.get("distance"),
                data.get("weight"),
                data.get("promoCode"),
                data.get("hour"),
                data.get("dayOfWeek"),
            )
        except ValueError as exc:
            return {"error": str(exc)}, 400
        return detail, 200

    # Enregistre une commande en memoire avec un ID unique
    @app.post("/orders")
    def create_order():
        data, error = _get_order_payload()
        if error:
            return error
        try:
            detail = calculate_order_total(
                data.get("items"),
                data.get("distance"),
                data.get("weight"),
                data.get("promoCode"),
                data.get("hour"),
                data.get("dayOfWeek"),
            )
        except ValueError as exc:
            return {"error": str(exc)}, 400

        order = {
            "id": globals()["_next_order_id"],
            "items": data.get("items"),
            "distance": data.get("distance"),
            "weight": data.get("weight"),
            "promoCode": data.get("promoCode"),
            **detail,
        }
        globals()["_next_order_id"] += 1
        orders[order["id"]] = order
        return jsonify(order), 201

    @app.get("/orders/<order_id>")
    def get_order(order_id: str):
        if not order_id.isdigit():
            return {"error": "L'identifiant doit etre un nombre"}, 400
        order = orders.get(int(order_id))
        if order is None:
            return {"error": "Commande introuvable"}, 404
        return jsonify(order), 200

    # Valide un code promo SANS modifier quoi que ce soit
    @app.post("/promo/validate")
    def validate_promo():
        data, error = _get_order_payload()
        if error:
            return error

        code = data.get("code")
        amount = data.get("amount")
        if not code:
            return {"error": "Le parametre code est obligatoire"}, 400
        try:
            result = apply_promo_code(amount, code, PROMO_CODES)
        except ValueError as exc:
            # un code inconnu merite un 404, les autres refus un 400
            status = 404 if "inconnu" in str(exc) else 400
            return {"error": str(exc)}, status
        return {"valid": True, **result}, 200

    return app
