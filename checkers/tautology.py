from plugins import IChecker


class TautologyChecker(IChecker):

    def check(self, *reports):
        return True
