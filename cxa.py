import argparse
import subprocess
import sys


def get_commands():
    return [x for x, y in Commands.__dict__.items() if type(y) == staticmethod]


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=get_commands())
    return parser.parse_known_args()


def main():
    args = get_args()
    getattr(Commands, args[0].command)(sys.argv[2:])


class Commands:
    @staticmethod
    def build(*args, **kwargs):
        print("No building to be done for Python")

    @staticmethod
    def format(args):
        print("=" * 30)
        print("Running isort")
        call_command(
            "isort -rc --multi-line=3 --trailing-comma --force-grid-wrap=0 --use-parentheses --line-width=120 ./src "
            + " ".join(args)
        )
        print("=" * 30)

        print("Running Black")
        call_command("black ./src " + " ".join(args))
        print("=" * 30)

    @staticmethod
    def install(args):
        print("=" * 30)
        print("Installing Pipenv dependencies")
        call_command("pipenv install " + " ".join(args))
        print("=" * 30)

    @staticmethod
    def lint(args):
        print("=" * 30)
        print("Running isort")
        call_command(
            "isort -rc --diff --multi-line=3 --trailing-comma --force-grid-wrap=0 --use-parentheses --line-width=120 ./src "
            + " ".join(args)
        )
        print("=" * 30)

        print("Running Black")
        print("=" * 30)
        call_command("black ./src --check")
        print("=" * 30)

        print("Running Flake8")
        print("=" * 30)
        call_command("flake8 ./src")
        print("=" * 30)

    @staticmethod
    def run(args):
        call_command("python src/cxa/main.py " + " ".join(args))

    @staticmethod
    def list(args):
        print("Available Commands:")
        for command in get_commands():
            print(command)


def call_command(cmd):
    subprocess.run(cmd, stderr=sys.stderr, stdout=sys.stdout, stdin=sys.stdin)


if __name__ == "__main__":
    main()
