import argparse

try:
    from transformer import TemplateVariableValidation, getTemplateVariables, handleGit, run
except ModuleNotFoundError:
    from .transformer import TemplateVariableValidation, getTemplateVariables, handleGit, run


def getCommand():
    parser = argparse.ArgumentParser(description="Process template")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--directory", type=str, help="Directory containing manifest.cxa.yml")
    group.add_argument("-g", "--git", type=str, help="Github repository URL or URL to .git file for template source")
    parser.add_argument(
        "-o",
        "--output_directory",
        type=str,
        help="Output directory (will be a modified copy of the original directory)",
    )
    parser.add_argument("-f", "--file", type=str, help="JSON file containing template replacements")
    parser.add_argument("-D", nargs="*", action="append")

    return parser.parse_args()


def main():
    args = getCommand()
    template_variables = getTemplateVariables(args.file, args.D)

    if args.git:
        if args.git.lower().endswith(".git"):
            print("Cloning git repository")
            args.directory = handleGit(args.git, args.output_directory)
        else:
            raise Exception(
                "I'm not sure what to do with that -g argument yet. Make sure it is a URL ending with '.git'."
            )

    try:
        run(args.directory, args.output_directory, template_variables)
    except TemplateVariableValidation as e:
        print(str(e))
        for m in e.errors:
            print(m)


if __name__ == "__main__":
    main()
