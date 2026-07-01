class Settings:
    def __init__(self):
        self.args = {}
        self.flags = []

    @staticmethod
    def _parse_user_args(user_args):
        args = {}
        flags = []

        for user_arg in user_args:
            if "=" in user_arg:
                key, value = user_arg.split("=")
                args[key] = value
            else:
                flags.append(user_arg)
        return args, flags

    def update_user_args(self, user_args):
        user_args, user_flags = self._parse_user_args(user_args)
        settings.args.update(user_args)
        settings.flags.extend(user_flags)


settings = Settings()
