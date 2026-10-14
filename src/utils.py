"""Fonctions utilitaires generales de l'application."""

import re


def capitalize(text: str | None) -> str:
    """Met la premiere lettre en majuscule, le reste en minuscule.

    Les entrees invalides (None, vide, non-texte) retournent une
    chaine vide : on ne veut jamais lever d'exception pour du simple
    formatage d'affichage.
    """
    if not isinstance(text, str) or not text:
        return ""
    return text[0].upper() + text[1:].lower()


def calculate_average(numbers: list[float] | None) -> float:
    """Calcule la moyenne d'une liste de nombres, arrondie a 2 decimales.

    Une liste vide ou None retourne 0 : c'est un choix de design, on
    prefere une valeur neutre plutot qu'une exception pour une entree
    "aucune note" (ex: un etudiant sans notes a une moyenne de 0).
    """
    if not numbers:
        return 0
    return round(sum(numbers) / len(numbers), 2)


def slugify(text: str) -> str:
    """Transforme un texte en slug utilisable dans une URL.

    Etapes : minuscules -> suppression des caracteres non
    alphanumeriques (garde les espaces) -> espaces remplaces par
    des tirets. Les espaces de debut/fin sont retires pour eviter
    les tirets parasites.
    """
    lowered = text.lower()
    without_specials = re.sub(r"[^a-z0-9 ]", "", lowered)
    return re.sub(r"\s+", "-", without_specials.strip())


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Limite une valeur entre un minimum et un maximum.

    max(minimum, ...) force la valeur au-dessus du plancher,
    min(..., maximum) la force sous le plafond.
    """
    return max(minimum, min(value, maximum))
