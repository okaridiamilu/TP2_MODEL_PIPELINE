"""Tests TDD de sort_students (src/utils.py).

Ecrits UN PAR UN selon le cycle Red -> Green -> Refactor :
chaque test a ete ecrit AVANT le code qui le fait passer.
"""

from src.utils import sort_students

STUDENTS = [
    {"name": "Charlie", "grade": 8, "age": 20},
    {"name": "Alice", "grade": 15, "age": 22},
    {"name": "Bob", "grade": 12, "age": 19},
]


# RED : ecrit en premier, il echoue car sort_students n'existe pas encore
def test_sort_students_should_sort_by_grade_ascending() -> None:
    result = sort_students(STUDENTS, "grade")

    assert [student["name"] for student in result] == ["Charlie", "Bob", "Alice"]


def test_sort_students_should_sort_by_grade_descending() -> None:
    result = sort_students(STUDENTS, "grade", "desc")

    assert [student["name"] for student in result] == ["Alice", "Bob", "Charlie"]


def test_sort_students_should_sort_by_name_ascending() -> None:
    result = sort_students(STUDENTS, "name")

    assert [student["name"] for student in result] == ["Alice", "Bob", "Charlie"]


def test_sort_students_should_sort_by_age_ascending() -> None:
    result = sort_students(STUDENTS, "age")

    assert [student["name"] for student in result] == ["Bob", "Charlie", "Alice"]


def test_sort_students_should_return_empty_list_when_input_is_none() -> None:
    assert sort_students(None, "grade") == []


def test_sort_students_should_return_empty_list_when_input_is_empty() -> None:
    assert sort_students([], "grade") == []


def test_sort_students_should_not_modify_the_original_array() -> None:
    original = [dict(student) for student in STUDENTS]

    sort_students(STUDENTS, "grade", "desc")

    assert STUDENTS == original


def test_sort_students_should_default_to_ascending_order() -> None:
    without_order = sort_students(STUDENTS, "grade")
    with_explicit_asc = sort_students(STUDENTS, "grade", "asc")

    assert without_order == with_explicit_asc
