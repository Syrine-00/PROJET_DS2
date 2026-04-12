class Critic:
    def validate(self, result):
        if result is None:
            return False

        if isinstance(result, dict) and "error" in result:
            return False

        return True
