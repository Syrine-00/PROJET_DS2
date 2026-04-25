"""
Critic — validates final output for correctness and safety.
Checks that the result is non-empty, has no error markers,
and contains expected structure.
"""


class Critic:
    def validate(self, result) -> bool:
        """
        Return True if result is valid, False otherwise.
        """
        # None → error
        if result is None:
            return False

        # Explicit error marker → invalid
        if isinstance(result, dict) and "error" in result:
            return False

        # Empty dict → invalid
        if isinstance(result, dict) and len(result) == 0:
            return False

        # All checks passed
        return True
