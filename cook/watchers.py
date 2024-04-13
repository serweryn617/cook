import invoke


class RichPrinter(invoke.watchers.StreamWatcher):
    def __init__(self, logger):
        super().__init__()
        self.index = 0
        self.logger = logger

    def submit(self, stream):
        new = stream[self.index:]
        self.index += len(new)

        self.logger.rich(new)

        return tuple()
