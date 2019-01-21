import argparse
import os
import shutil
import sys
import pathlib
import yaml
import json
from typing import Dict
from jinja2 import Template
from distutils.dir_util import copy_tree
import re


def getCommand():
    parser = argparse.ArgumentParser(description="Process template")
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        help="Directory containing manifest.cxa.yml",
        required=True,
    )
    parser.add_argument(
        "-f", "--file", type=str, help="JSON file containing template replacements"
    )

    return parser.parse_args()


def main():
    args = getCommand()
    manifest_file = os.path.join(args.directory, "manifest.cxa.yml")
    if not os.path.exists(manifest_file):
        print("Check that the path contains the manifest.cxa.yml file")
        sys.exit(1)
    manifest = None
    with open(manifest_file, "r") as f:
        manifest = yaml.safe_load(f)

    template_variables = dict()
    if manifest.get("uses_template_variables", False):
        if args.file is None:
            print(
                "This template uses variables, please provide the template variable file"
            )
            sys.exit(1)
        elif not os.path.exists(args.file):
            print(
                "This template uses variables, the template file you provided doesn't exist"
            )
            sys.exit(1)
        else:
            with open(args.file, "r") as file:
                template_variables = json.load(file, encoding="utf-8")

    try:
        hadError = False
        for k, v in manifest["required_template_variables"].items():
            if k not in template_variables and not v["type"].startswith("opt("):
                print(f"{k} is missing from the template variable definition file")
                hadError = True
            if k in template_variables:
                if type(template_variables[k]) != typeMap(v["type"]):
                    print(
                        f"Type {v['type']} does not match provided type for template variable {k}"
                    )
                    hadError = True
                hadError |= not validateVariable(template_variables[k], v)
        if hadError:
            sys.exit(1)
    except KeyError:
        pass

    directory_path = pathlib.Path(args.directory).resolve()
    new_path = os.path.join(str(directory_path.parent), directory_path.name + "_COPY")

    copy_tree(directory_path, new_path)

    for dirname, dirnames, filenames in os.walk(new_path, followlinks=True):
        for dname in dirnames:
            if str(dname).startswith("$"):
                shutil.move(
                    os.path.join(dirname, dname),
                    os.path.join(dirname, replaceVariable(dname, template_variables)),
                )

        for filename in filenames:
            if str(filename).endswith(".jnj"):
                template = None
                with open(os.path.join(dirname, filename), "r") as file:
                    template = Template(file.read())
                with open(os.path.join(dirname, filename[:-4]), "w") as file:
                    file.write(template.render(**template_variables))
                os.remove(os.path.join(dirname, filename))


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
    if "validation" in definition:
        if definition["validation"].startswith("regexNoMatch"):
            rule = definition["validation"]
            rule = re.fullmatch(r"regexNoMatch\((.*)\)", rule).group(1)
            if re.search(r"\s", toValidate) is not None:
                print(f"{toValidate} failed to validate with rule: {rule}")
                return False

    return True


if __name__ == "__main__":
    main()
