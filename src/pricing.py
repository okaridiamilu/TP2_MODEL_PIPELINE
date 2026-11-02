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


WEEKDAYS = {"monday", "tuesday", "wednesday", "thursday"}
OPENING_HOUR = 10
CLOSING_HOUR = 22
LUNCH_START, LUNCH_END = 12, 13.5
DINNER_START, DINNER_END = 19, 21
WEEKEND_EVENING_START = 19


def calculate_surge(hour, day_of_week):
    """Retourne le multiplicateur de prix selon l'heure et le jour.

    Heures d'ouverture : de 10h (inclusive) a 22h (exclusive).
    En dehors : retourne 0 (restaurant ferme).

    Attention anti-flaky : l'heure et le jour sont des PARAMETRES.
    Cette fonction ne lit JAMAIS l'heure systeme, comme ca les tests
    sont deterministes quelle que soit l'heure reelle ou ils tournent.
    """
    day = day_of_week.lower() if isinstance(day_of_week, str) else ""
    if day not in WEEKDAYS | {"friday", "saturday", "sunday"}:
        raise ValueError("Jour de la semaine invalide")
    if not isinstance(hour, (int, float)) or isinstance(hour, bool):
        raise ValueError("L'heure doit etre un nombre")
    if not 0 <= hour <= 24:
        raise ValueError("L'heure doit etre entre 0 et 24")

    # en dehors des heures d'ouverture : ferme
    if hour < OPENING_HOUR or hour >= CLOSING_HOUR:
        return 0

    # dimanche : majoration toute la journee
    if day == "sunday":
        return 1.0

    # vendredi et samedi soir : grosse pointe
    if day in {"friday", "saturday"}:
        return 1.8 if hour >= WEEKEND_EVENING_START else 1.0

    # lundi a jeudi : dejeuner, diner, sinon normal
    if LUNCH_START <= hour < LUNCH_END:
        return 1.3
    if DINNER_START <= hour < DINNER_END:
        return 1.5
    return 1.0


def calculate_order_total(items, distance, weight, promo_code, hour, day_of_week):
    """Assemble tout le moteur : items + promo + livraison + surge.

    Ordre de calcul :
    1. sous-total = somme des prix * quantites
    2. reduction promo
    3. frais de livraison selon distance et poids
    4. le surge multiplie UNIQUEMENT les frais de livraison

    Retourne {subtotal, discount, deliveryFee, surge, total}, tous
    arrondis a 2 decimales. Le restaurant ferme (surge = 0) est une
    erreur : on refuse la commande.
    """
    if not items:
        raise ValueError("Le panier ne peut pas etre vide")

    subtotal = 0
    for item in items:
        if not isinstance(item, dict) or "price" not in item or "quantity" not in item:
            raise ValueError("Chaque item doit avoir un prix et une quantite")
        price, quantity = item["price"], item["quantity"]
        if not isinstance(price, (int, float)) or isinstance(price, bool) or price < 0:
            raise ValueError("Le prix d'un item doit etre un nombre positif")
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
            raise ValueError("La quantite doit etre un entier d'au moins 1")
        subtotal += price * quantity

    discount = apply_promo_code(subtotal, promo_code, PROMO_CODES)["discount"]
    delivery_fee = calculate_delivery_fee(distance, weight)
    surge = calculate_surge(hour, day_of_week)
    if surge == 0:
        raise ValueError("Restaurant ferme a cette heure")

    final_delivery = round(delivery_fee * surge, 2)
    total = round(subtotal - discount + final_delivery, 2)

    return {
        "subtotal": round(subtotal, 2),
        "discount": discount,
        "deliveryFee": final_delivery,
        "surge": surge,
        "total": total,
    }
