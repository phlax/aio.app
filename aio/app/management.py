import sys

from aio.app import runner


def main():
    runner.runner(sys.argv[1:], search_for_config=True)

if __name__ == "__main__":
    main()
