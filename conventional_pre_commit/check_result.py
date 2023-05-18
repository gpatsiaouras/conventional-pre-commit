from typing import Optional, Match, AnyStr, List


class SingleCheckResult:
    """Holds the result of a single regex check"""

    def __init__(self, regex_result: Optional[Match[AnyStr]], potential_reason: Optional[str]):
        self.regex_result = bool(regex_result)
        if not self.regex_result and potential_reason is not None:
            self.failure_reason = potential_reason

    def __bool__(self):
        return self.regex_result


class ConventionalCommitCheckResult:
    """Holds multiples single check results, provides function for str and bool"""

    def __init__(self):
        self.results: List[SingleCheckResult] = []

    def add(self, regex_result: Optional[Match[AnyStr]], potential_reason: Optional[str]):
        """Appends a result to the list."""
        self.results.append(SingleCheckResult(regex_result, potential_reason))

    def __bool__(self):
        """Returns True if all the individual regex results are True"""
        return all([result.regex_result for result in self.results])

    def __str__(self):
        """Concatenates the failure reasons of all the check results if the result is failure"""
        reasons = []
        for result in self.results:
            if not result.regex_result:
                reasons.append(str(result.failure_reason))
        return ", ".join(reasons)
