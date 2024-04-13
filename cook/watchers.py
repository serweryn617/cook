import invoke


class RichPrinter(invoke.watchers.StreamWatcher):
    def __init__(self, logger):
        super().__init__()
        self.index = 0
        self.logger = logger

    def submit(self, stream):
        last_line = stream.rfind('\n')
        new = stream[self.index : last_line + 1]
        self.index += len(new)

        self.logger.rich(new)

        return tuple()
