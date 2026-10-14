"""Tests unitaires de src/validators.py."""

from src.validators import is_valid_age, is_valid_email, is_valid_password


# --- is_valid_email : 7 cas ---


def test_email_should_be_valid_when_classic_format() -> None:
    assert is_valid_email("user@example.com") is True


def test_email_should_be_valid_when_plus_tag_and_dots() -> None:
    assert is_valid_email("user.name+tag@domain.co") is True


def test_email_should_be_invalid_when_no_at_sign() -> None:
    assert is_valid_email("invalid") is False


def test_email_should_be_invalid_when_no_local_part() -> None:
    assert is_valid_email("@domain.com") is False


def test_email_should_be_invalid_when_no_domain() -> None:
    assert is_valid_email("user@") is False


def test_email_should_be_invalid_when_empty_string() -> None:
    assert is_valid_email("") is False


def test_email_should_be_invalid_when_none() -> None:
    assert is_valid_email(None) is False


# --- is_valid_password : 8 cas ---


def test_password_should_be_valid_when_all_rules_respected() -> None:
    result = is_valid_password("Passw0rd!")

    assert result == {"valid": True, "errors": []}


def test_password_should_list_every_error_when_too_short() -> None:
    # "short" viole 4 regles : longueur, majuscule, chiffre, special
    result = is_valid_password("short")

    assert result["valid"] is False
    assert "Au moins 8 caracteres" in result["errors"]
    assert "Au moins 1 majuscule" in result["errors"]
    assert "Au moins 1 chiffre" in result["errors"]
    assert "Au moins 1 caractere special" in result["errors"]


def test_password_should_report_missing_uppercase() -> None:
    result = is_valid_password("alllowercase1!")

    assert result["valid"] is False
    assert "Au moins 1 majuscule" in result["errors"]
    assert "Au moins 1 minuscule" not in result["errors"]


def test_password_should_report_missing_lowercase() -> None:
    result = is_valid_password("ALLUPPERCASE1!")

    assert result["valid"] is False
    assert "Au moins 1 minuscule" in result["errors"]


def test_password_should_report_missing_digit() -> None:
    result = is_valid_password("NoDigits!here")

    assert result["valid"] is False
    assert "Au moins 1 chiffre" in result["errors"]


def test_password_should_report_missing_special_character() -> None:
    result = is_valid_password("NoSpecial1here")

    assert result["valid"] is False
    assert "Au moins 1 caractere special" in result["errors"]


def test_password_should_be_invalid_when_empty_string() -> None:
    result = is_valid_password("")

    assert result["valid"] is False
    assert len(result["errors"]) > 0


def test_password_should_be_invalid_when_none() -> None:
    result = is_valid_password(None)

    assert result["valid"] is False
    assert len(result["errors"]) > 0


# --- is_valid_age : 8 cas ---


def test_age_should_be_valid_when_classic_age() -> None:
    assert is_valid_age(25) is True


def test_age_should_be_valid_when_zero() -> None:
    assert is_valid_age(0) is True


def test_age_should_be_valid_when_150() -> None:
    assert is_valid_age(150) is True


def test_age_should_be_invalid_when_negative() -> None:
    assert is_valid_age(-1) is False


def test_age_should_be_invalid_when_above_150() -> None:
    assert is_valid_age(151) is False


def test_age_should_be_invalid_when_float() -> None:
    assert is_valid_age(25.5) is False


def test_age_should_be_invalid_when_string() -> None:
    assert is_valid_age("25") is False


def test_age_should_be_invalid_when_none() -> None:
    assert is_valid_age(None) is False
