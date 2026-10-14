"""Moteur de tarification d'une plateforme de livraison de repas.

Chaque fonction leve une ValueError avec un message clair quand les
entrees sont invalides : la couche API transformera ces erreurs en
reponses HTTP 400.
"""

from datetime import date

BASE_FEE = 2.00
PRICE_PER_KM = 0.50
MAX_DISTANCE = 10
FREE_DISTANCE = 3
HEAVY_WEIGHT = 5
HEAVY_SURCHARGE = 1.50


def calculate_delivery_fee(distance: float, weight: float) -> float | None:
    """Calcule les frais de livraison.

    Regles :
    - base 2.00 EUR pour toute livraison
    - jusqua 3 km inclus : aucun supplement
    - de 3 a 10 km inclus : +0.50 EUR par km au-dela de 3 km
    - au-dela de 10 km : livraison refusee (ValueError)
    - poids strictement superieur a 5 kg : supplement 1.50 EUR

    Retourne le montant arrondi a 2 decimales.
    """
    if not isinstance(distance, (int, float)) or not isinstance(weight, (int, float)):
        raise ValueError("Distance et poids doivent etre des nombres")
    if distance < 0 or weight < 0:
        raise ValueError("Distance et poids ne peuvent pas etre negatifs")
    if distance > MAX_DISTANCE:
        raise ValueError("Livraison refusee : distance superieure a 10 km")

    fee = BASE_FEE
    if distance > FREE_DISTANCE:
        fee += (distance - FREE_DISTANCE) * PRICE_PER_KM
    if weight > HEAVY_WEIGHT:
        fee += HEAVY_SURCHARGE
    return round(fee, 2)


# Codes promo disponibles, stockes en memoire
PROMO_CODES = [
    {
        "code": "BIENVENUE20",
        "type": "percentage",
        "value": 20,
        "minOrder": 15.00,
        "expiresAt": "2099-12-31",
    },
    {
        "code": "LIVRAISON5",
        "type": "fixed",
        "value": 5,
        "minOrder": 20.00,
        "expiresAt": "2099-12-31",
    },
    {
        "code": "EXPIRE10",
        "type": "percentage",
        "value": 10,
        "minOrder": 0,
        "expiresAt": "2020-01-01",
    },
]


def apply_promo_code(subtotal, promo_code, promo_codes):
    """Applique un code promo au sous-total d'une commande.

    Retourne {"discount": montant de la reduction, "total": nouveau prix}.
    Le total ne descend jamais sous 0.

    Regles de refus (ValueError) : code inconnu, code expire, ou
    commande sous le minimum d'achat (minOrder). Un code expire le
    jour MEME reste accepte : la date est inclusive.
    """
    if not isinstance(subtotal, (int, float)) or isinstance(subtotal, bool):
        raise ValueError("Le sous-total doit etre un nombre")
    if subtotal < 0:
        raise ValueError("Le sous-total ne peut pas etre negatif")

    # Pas de code fourni : aucune reduction, on retourne tel quel
    if not promo_code:
        return {"discount": 0, "total": round(subtotal, 2)}

    promo = next((p for p in promo_codes if p["code"] == promo_code), None)
    if promo is None:
        raise ValueError("Code promo inconnu")

    if date.today().isoformat() > promo["expiresAt"]:
        raise ValueError("Code promo expire")
    if subtotal < promo["minOrder"]:
        raise ValueError(f"Commande minimum de {promo['minOrder']} EUR requise")

    if promo["type"] == "percentage":
        discount = subtotal * promo["value"] / 100
    else:
        discount = promo["value"]

    # la reduction reelle est plafonnee au sous-total : on ne peut
    # pas afficher -10 EUR sur une commande de 5 EUR
    discount = min(discount, subtotal)

    return {
        "discount": round(discount, 2),
        "total": round(max(subtotal - discount, 0), 2),
    }
