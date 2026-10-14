"""Tests unitaires de src/utils.py — structure AAA (Arrange, Act, Assert)."""

from src.utils import calculate_average, capitalize, clamp, slugify


# --- capitalize : 5 cas (3 normaux + 2 cas limites vide et None) ---


def test_capitalize_should_return_capitalized_word_when_lowercase() -> None:
    # Arrange
    text = "hello"
    # Act
    result = capitalize(text)
    # Assert
    assert result == "Hello"


def test_capitalize_should_lowercase_rest_when_uppercase_input() -> None:
    result = capitalize("WORLD")

    assert result == "World"


def test_capitalize_should_return_empty_string_when_input_is_empty() -> None:
    result = capitalize("")

    assert result == ""


def test_capitalize_should_return_empty_string_when_input_is_none() -> None:
    result = capitalize(None)

    assert result == ""


def test_capitalize_should_return_empty_string_when_input_is_not_a_string() -> None:
    result = capitalize(123)

    assert result == ""


# --- calculate_average : 5 cas (normaux + liste vide + None) ---


def test_calculate_average_should_return_12_when_10_12_14() -> None:
    result = calculate_average([10, 12, 14])

    assert result == 12


def test_calculate_average_should_return_same_value_when_single_item() -> None:
    result = calculate_average([15])

    assert result == 15


def test_calculate_average_should_return_0_when_empty_list() -> None:
    result = calculate_average([])

    assert result == 0


def test_calculate_average_should_return_11_when_10_11_12() -> None:
    result = calculate_average([10, 11, 12])

    assert result == 11


def test_calculate_average_should_return_0_when_none() -> None:
    result = calculate_average(None)

    assert result == 0


# --- slugify : 4 cas (normaux + caracteres speciaux + vide) ---


def test_slugify_should_replace_spaces_with_dashes() -> None:
    result = slugify("Hello World")

    assert result == "hello-world"


def test_slugify_should_trim_and_squash_spaces() -> None:
    result = slugify(" Spaces Everywhere ")

    assert result == "spaces-everywhere"


def test_slugify_should_remove_special_characters() -> None:
    result = slugify("C'est l'ete !")

    assert result == "cest-lete"


def test_slugify_should_return_empty_string_when_input_is_empty() -> None:
    result = slugify("")

    assert result == ""


# --- clamp : 4 cas (dans l'intervalle, sous le plancher, au-dessus du plafond, bornes egales) ---


def test_clamp_should_return_value_when_inside_bounds() -> None:
    result = clamp(5, 0, 10)

    assert result == 5


def test_clamp_should_return_minimum_when_value_below() -> None:
    result = clamp(-5, 0, 10)

    assert result == 0


def test_clamp_should_return_maximum_when_value_above() -> None:
    result = clamp(15, 0, 10)

    assert result == 10


def test_clamp_should_return_zero_when_all_bounds_are_zero() -> None:
    result = clamp(0, 0, 0)

    assert result == 0
