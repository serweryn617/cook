class RecipeContext:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    def __getitem__(self, key: str) -> str:
        return self.values[key]

    def __setitem__(self, key: str, value: str) -> None:
        self.values[key] = value

    def get(self, key: str, default: str | None = None) -> str | None:
        return self.values.get(key, default)
