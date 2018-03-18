
class Colors(object):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def bprint(s, m):
    _b = Colors()
    print(_b.BOLD + _b.OKBLUE + s + _b.ENDC, m)


def gprint(s, m):
    _b = Colors()
    print(_b.BOLD + _b.OKGREEN + s + _b.ENDC, m)


def rprint(s):
    _b = Colors()
    print(_b.BOLD + _b.FAIL + s + _b.ENDC)
