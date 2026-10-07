from collections.abc import Sequence

from .context import RecipeContext
from .library.logger import log
from .library.selector import Selector


class Prompt:
    def __init__(
        self,
        message: str,
        choices: Sequence[str],
        *,
        default: str | None = None,
        store: str | None = None,
    ) -> None:
        self.message = message
        self.choices = tuple(choices)
        self.default = default
        self.store = store

    def select(self, context: RecipeContext | None = None) -> str:
        if self.store is not None and context is None:
            raise RuntimeError("A RecipeContext is required when using Prompt(store=...)")

        selected = Selector(
            self.choices,
            self.message,
            default=self.default,
        ).select()

        if self.store is not None:
            assert context is not None
            context[self.store] = selected

        log(f"Selected {self.message}: {selected}", "log")
        return selected

    def __call__(self, context: RecipeContext | None = None) -> str:
        return self.select(context)
