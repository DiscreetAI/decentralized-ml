import sys

from core.bootstrapper import bootstrap


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]
    bootstrap()

if __name__ == "__main__":
    main()
