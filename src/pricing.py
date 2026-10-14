"""Moteur de tarification d'une plateforme de livraison de repas.

Chaque fonction leve une ValueError avec un message clair quand les
entrees sont invalides : la couche API transformera ces erreurs en
reponses HTTP 400.
"""

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
