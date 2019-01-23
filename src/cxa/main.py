import argparse
import os
import shutil
import sys
import pathlib
import yaml
import json
from typing import Dict
from jinja2 import Template
import re
import git


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

    return parser.parse_args()


def main():
    args = getCommand()

    if args.git:
        if args.git.lower().endswith(".git"):
            print("Cloning git repository")
            args.directory = args.output_directory
            git.Repo().clone_from(args.git, args.output_directory)
        else:
            print("I'm not sure what to do with that -g argument yet. Make sure it is a URL ending with '.git'.")
            sys.exit(1)

    manifest = getManifest(args)
    template_variables = getTemplateVariables(args, manifest)
    validateTemplateVariables(manifest, template_variables)
    doTemplateReplacement(setupPaths(args), template_variables)


def setupPaths(args):
    directory_path = pathlib.Path(args.directory).resolve()
    output_directory_path = pathlib.Path(args.output_directory).resolve()
    if not os.path.exists(str(output_directory_path)):
        shutil.copytree(str(directory_path), str(output_directory_path))
    return output_directory_path


def doTemplateReplacement(output_directory_path, template_variables):
    for dirname, dirnames, filenames in os.walk(output_directory_path, followlinks=True):
        for dname in dirnames:
            if str(dname).startswith("$"):
                shutil.move(
                    os.path.join(dirname, dname), os.path.join(dirname, replaceVariable(dname, template_variables))
                )

        for filename in filenames:
            if str(filename).endswith(".jnj"):
                with open(os.path.join(dirname, filename), "r") as file:
                    template = Template(file.read())
                    with open(os.path.join(dirname, filename[:-4]), "w") as file:
                        file.write(template.render(**template_variables))
                os.remove(os.path.join(dirname, filename))


def validateTemplateVariables(manifest, template_variables):
    try:
        hadError = False
        for k, v in manifest["required_template_variables"].items():
            if k not in template_variables and not v["type"].startswith("opt("):
                print(f"{k} is missing from the template variable definition file")
                hadError = True
            if k in template_variables:
                if type(template_variables[k]) != typeMap(v["type"]):
                    print(f"Type {v['type']} does not match provided type for template variable {k}")
                    hadError = True
                hadError |= not validateVariable(template_variables[k], v)
        if hadError:
            sys.exit(1)
    except KeyError:
        pass


def getManifest(args):
    manifest_file = os.path.join(args.directory, "manifest.cxa.yml")
    if not os.path.exists(manifest_file):
        print("Check that the path contains the manifest.cxa.yml file")
        sys.exit(1)
    with open(manifest_file, "r") as f:
        return yaml.safe_load(f)


def getTemplateVariables(args, manifest):
    template_variables = dict()
    if manifest.get("uses_template_variables", False):
        if args.file is None:
            print("This template uses variables, please provide the template variable file")
            sys.exit(1)
        elif not os.path.exists(args.file):
            print("This template uses variables, the template file you provided doesn't exist")
            sys.exit(1)
        else:
            with open(args.file, "r") as file:
                template_variables = json.load(file, encoding="utf-8")
    return template_variables


def typeMap(t: str):
    t = t.lower()
    if t.startswith("opt(") and t.endswith(")"):
        t = t[4:-1]
    if t == "string":
        return str
    if t == "integer":
        return int
    if t == "number":
        return float
    if t == "boolean":
        return bool
    return None


def replaceVariable(toReplace: str, variables: Dict[str, str]):
    assert toReplace.startswith("$")
    return variables[toReplace[1:]]


def validateVariable(toValidate, definition):
    regexValidations = {"regexMatch": True, "regexNoMatch": False}
    if "validation" in definition:
        for k, v in regexValidations.items():
            if definition["validation"].startswith(k):
                rule = definition["validation"]
                rule = re.fullmatch(k + r"\((.*)\)", rule).group(1)
                if (re.search(r"\s", toValidate) is None) == v:
                    print(f"{toValidate} failed to validate with rule: {rule}")
                    return False

    return True


if __name__ == "__main__":
    main()
