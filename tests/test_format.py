import re

import pytest

from conventional_pre_commit import format

CUSTOM_TYPES = ["one", "two"]


def test_r_types():
    result = format.r_types(CUSTOM_TYPES)
    regex = re.compile(result)

    assert regex.match("one")
    assert regex.match("two")


def test_r_refs():
    result = format.r_refs()
    regex = re.compile(result)

    assert regex.search("Refs: CI-1234")


def test_r_refs__numbers_in_team():
    result = format.r_refs()
    regex = re.compile(result)

    assert regex.search("Refs: SDP0123-1234")


def test_r_refs__refs_lowercase():
    result = format.r_refs()
    regex = re.compile(result)

    assert not regex.search("refs: CI-1234")


def test_r_refs__refs_no_space():
    result = format.r_refs()
    regex = re.compile(result)

    assert not regex.search("refs:CI-1234")


def test_r_refs__letters_in_end():
    result = format.r_refs()
    regex = re.compile(result)

    assert not regex.search("Refs: CI-CI")


def test_r_refs__wrong_format():
    result = format.r_refs()
    regex = re.compile(result)

    assert not regex.search("Refs: #123")


def test_r_refs__multiple():
    result = format.r_refs()
    regex = re.compile(result)

    assert regex.search("Refs: CI-123,DEF-123")


def test_r_refs__multiple_w_space():
    result = format.r_refs()
    regex = re.compile(result)

    assert regex.search("Refs: CI-123, DEF-123")


def test_r_refs__multiple_error_first():
    result = format.r_refs()
    regex = re.compile(result)

    assert not regex.search("Refs: incorrect, CI-123")


def test_r_refs__multiple_error_last():
    result = format.r_refs()
    regex = re.compile(result)

    assert not regex.search("Refs: CI-123, incorrect")


def test_r_refs__spaces():
    result = format.r_refs()
    regex = re.compile(result)

    assert regex.search("Refs: CI-123        ")


def test_r_refs__new_line():
    result = format.r_refs()
    regex = re.compile(result)

    assert regex.search(
        """Refs: CI-123
    """
    )


def test_r_scope__optional():
    result = format.r_scope()
    regex = re.compile(result)

    assert regex.match("")


def test_r_scope__not_optional():
    result = format.r_scope(optional=False)
    regex = re.compile(result)

    # Assert not optional anymore
    assert not regex.match("")


def test_r_scope__parenthesis_required():
    result = format.r_scope()
    regex = re.compile(result)

    # without parens produces a match object with a 0 span
    # since the (scope) is optional
    without_parens = regex.match("something")
    assert without_parens.span() == (0, 0)

    # with parens produces a match object with a span
    # that covers the input string
    with_parens = regex.match("(something)")
    assert with_parens.span() == (0, 11)


def test_r_scope__alphanumeric():
    result = format.r_scope()
    regex = re.compile(result)

    assert regex.match("(50m3t41N6)")


def test_r_scope__special_chars():
    result = format.r_scope()
    regex = re.compile(result)

    assert regex.match("(some-thing)")
    assert regex.match("(some_thing)")
    assert regex.match("(some/thing)")
    assert regex.match("(some thing)")
    assert regex.match("(some:thing)")


def test_r_delim():
    result = format.r_delim()
    regex = re.compile(result)

    assert regex.match(":")


def test_r_delim__optional_breaking_indicator():
    result = format.r_delim()
    regex = re.compile(result)

    assert regex.match("!:")


def test_r_subject__starts_with_space():
    result = format.r_subject()
    regex = re.compile(result)

    assert not regex.match("something")
    assert regex.match(" something")


def test_r_subject__alphanumeric():
    result = format.r_subject()
    regex = re.compile(result)

    assert regex.match(" 50m3t41N6")


def test_r_subject__special_chars():
    result = format.r_subject()
    regex = re.compile(result)

    assert regex.match(" some-thing")
    assert regex.match(" some_thing")
    assert regex.match(" some/thing")
    assert regex.match(" some thing")


def test_conventional_types__default():
    result = format.conventional_types()

    assert result == format.CONVENTIONAL_TYPES


def test_conventional_types__custom():
    result = format.conventional_types(["custom"])

    assert set(["custom", *format.CONVENTIONAL_TYPES]) == set(result)


@pytest.mark.parametrize("type", format.DEFAULT_TYPES)
def test_is_conventional__default_type(type):
    input = f"{type}: message"

    assert format.is_conventional(input)


@pytest.mark.parametrize("type", format.CONVENTIONAL_TYPES)
def test_is_conventional__conventional_type(type):
    input = f"{type}: message"

    assert format.is_conventional(input)


@pytest.mark.parametrize("type", CUSTOM_TYPES)
def test_is_conventional__custom_type(type):
    input = f"{type}: message"

    assert format.is_conventional(input, CUSTOM_TYPES)


@pytest.mark.parametrize("type", format.CONVENTIONAL_TYPES)
def test_is_conventional__conventional_custom_type(type):
    input = f"{type}: message"

    assert format.is_conventional(input, CUSTOM_TYPES)


def test_is_conventional__breaking_change():
    input = "fix!: message"

    assert format.is_conventional(input)


def test_is_conventional__with_scope():
    input = "feat(scope): message"

    assert format.is_conventional(input)


def test_is_conventional__body_multiline():
    input = """feat(scope): message

    more message
    """

    assert format.is_conventional(input)


@pytest.mark.parametrize("char", ['"', "'", "`", "#", "&"])
def test_is_conventional__body_special_char(char):
    input = f"feat: message with {char}"

    assert format.is_conventional(input)


def test_is_conventional__wrong_type():
    input = "wrong: message"

    assert not format.is_conventional(input)


def test_is_conventional__scope_special_chars():
    input = "feat(%&*@()): message"

    assert not format.is_conventional(input)


def test_is_conventional__space_scope():
    input = "feat (scope): message"

    assert not format.is_conventional(input)


def test_is_conventional__scope_space():
    input = "feat(scope) : message"

    assert not format.is_conventional(input)


def test_is_conventional__scope_not_optional():
    input = "feat: message"

    assert not format.is_conventional(input, optional_scope=False)


def test_is_conventional__scope_not_optional_empty_parenthesis():
    input = "feat(): message"

    assert not format.is_conventional(input, optional_scope=False)


def test_is_conventional__missing_delimiter():
    input = "feat message"

    assert not format.is_conventional(input)


def test_is_conventional__correct_refs():
    input = """feat: message

    A random body

    Refs: CI-15624
    """

    assert format.is_conventional(input, force_refs=True)


def test_is_conventional__incorrect_refs():
    input = """feat: message
    Refs:CI-15624
    """

    assert not format.is_conventional(input, force_refs=True)


def test_is_conventional__with_git_comments():
    input = """feat(conventional-commit): Added force reps on check commit

Refs: DEF-1844

# Please enter the commit message for your changes. Lines starting
# with '#' will be ignored, and an empty message aborts the commit.
#
# On branch my_branch
# Your branch is ahead of 'origin/my_branch' by 1 commit.
#   (use "git push" to publish your local commits)
#
# Changes to be committed:
#	modified:   .pre-commit-config.yaml
#	modified:   folder/folder/pip_requirements.txt
#	modified:   script.sh
#
# Changes not staged for commit:
#	modified:   mypackage/package (modified content)
#
# Untracked files:
#	my-file.txt"""

    assert format.is_conventional(input, force_refs=True)
