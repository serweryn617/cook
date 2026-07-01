from collections.abc import Sequence

type Args = dict[str, str]
type Flags = list[str]


class Settings:
    def __init__(self) -> None:
        self.args: Args = {}
        self.flags: Flags = []

    @staticmethod
    def _parse_user_args(user_args: Sequence[str]) -> tuple[Args, Flags]:
        args: Args = {}
        flags: Flags = []

        for user_arg in user_args:
            if "=" in user_arg:
                key, value = user_arg.split("=")
                args[key] = value
            else:
                flags.append(user_arg)
        return args, flags

    def update_user_args(self, user_args: Sequence[str]) -> None:
        parsed_args, parsed_flags = self._parse_user_args(user_args)
        settings.args.update(parsed_args)
        settings.flags.extend(parsed_flags)


settings = Settings()
