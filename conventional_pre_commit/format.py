import re

from conventional_pre_commit.check_result import ConventionalCommitCheckResult

CONVENTIONAL_TYPES = ["feat", "fix"]
DEFAULT_TYPES = [
    "build",
    "chore",
    "ci",
    "docs",
    "feat",
    "fix",
    "perf",
    "refactor",
    "revert",
    "style",
    "test",
]


def r_types(types):
    """Join types with pipe "|" to form regex ORs."""
    return "|".join(types)


def r_scope(optional=True):
    """Regex str for an optional (scope)."""
    if optional:
        return r"(\([\w \/:-]+\))?"
    else:
        return r"(\([\w \/:-]+\))"


def r_delim():
    """Regex str for optional breaking change indicator and colon delimiter."""
    return r"!?:"


def r_subject():
    """Regex str for subject line, body, footer."""
    return r" .+"


def r_refs():
    """Regex str for refs on footer."""
    return r"(?<=Refs: )([A-Z0-9]+-[0-9]+,? ?)+(\s?)+$"


def conventional_types(types=[]):
    """Return a list of Conventional Commits types merged with the given types."""
    if set(types) & set(CONVENTIONAL_TYPES) == set():
        return CONVENTIONAL_TYPES + types
    return types


def is_conventional(input, types=DEFAULT_TYPES, optional_scope=True, force_refs=False) -> ConventionalCommitCheckResult:
    """
    Returns True if input matches Conventional Commits formatting
    https://www.conventionalcommits.org

    Optionally provide a list of additional custom types.
    """
    types = conventional_types(types)
    pattern = f"^({r_types(types)}){r_scope(optional_scope)}{r_delim()}{r_subject()}$"
    regex = re.compile(pattern, re.DOTALL)
    regex_result = regex.match(input)
    result = ConventionalCommitCheckResult()
    result.add(regex_result, "Subject is incorrect")

    if force_refs:
        regex = re.compile(r_refs(), re.MULTILINE)
        result.add(regex.search(input), "Refs missing or not correct")

    return result
