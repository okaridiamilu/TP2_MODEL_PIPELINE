"""Fonctions de validation des donnees utilisateur."""

import re

# Caracteres speciaux autorises pour les mots de passe
SPECIAL_CHARACTERS = "!@#$%^&*"


def is_valid_email(email: str | None) -> bool:
    """Retourne True si l'email a un format valide.

    Un email valide doit avoir une partie locale (au moins 1
    caractere), un @, un domaine et une extension separee par
    un point. None ou un type non-texte retournent False.
    """
    if not isinstance(email, str):
        return False
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) is not None


def is_valid_password(password: str | None) -> dict:
    """Verifie la robustesse d'un mot de passe.

    Regles : au moins 8 caracteres, une majuscule, une minuscule,
    un chiffre et un caractere special (!@#$%^&*).

    Retourne {"valid": bool, "errors": [liste des regles violees]} :
    on retourne TOUTES les erreurs, pas seulement la premiere,
    pour que l'utilisateur sache tout corriger d'un coup.
    """
    errors = []

    if not isinstance(password, str):
        return {"valid": False, "errors": ["Le mot de passe est requis"]}

    if len(password) < 8:
        errors.append("Au moins 8 caracteres")
    if not re.search(r"[A-Z]", password):
        errors.append("Au moins 1 majuscule")
    if not re.search(r"[a-z]", password):
        errors.append("Au moins 1 minuscule")
    if not re.search(r"[0-9]", password):
        errors.append("Au moins 1 chiffre")
    if not any(char in SPECIAL_CHARACTERS for char in password):
        errors.append("Au moins 1 caractere special")

    return {"valid": len(errors) == 0, "errors": errors}


def is_valid_age(age: object) -> bool:
    """Retourne True si l'age est un entier entre 0 et 150 inclus.

    Attention : en Python, True/False sont des sous-classes de int,
    donc isinstance(True, int) vaut True. On exclut les booleens
    explicitement, et on refuse les flottants (25.5) et les chaines
    ("25") : seul un vrai entier est accepte.
    """
    if isinstance(age, bool) or not isinstance(age, int):
        return False
    return 0 <= age <= 150
