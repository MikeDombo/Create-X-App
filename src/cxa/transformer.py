import json
import os
import pathlib
import re
import shutil
from distutils.util import strtobool
from typing import Dict

import git
import yaml
from jinja2 import Template


def run(directory, output_directory, template_variables):
    manifest = getManifest(directory)
    if manifest.get("uses_template_variables", False) and not template_variables.keys():
        raise Exception("This template uses variables, but none were provided")
    validateTemplateVariables(manifest, template_variables)
    doTemplateReplacement(setupPaths(directory, output_directory), template_variables)


def handleGit(gitURL, outputDirectory):
    git.Repo.clone_from(gitURL, outputDirectory)
    return outputDirectory


def setupPaths(directory, output_directory):
    directory_path = pathlib.Path(directory).resolve()
    output_directory_path = pathlib.Path(output_directory).resolve()
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
        errors = []
        for k, v in manifest["required_template_variables"].items():
            if k not in template_variables and not v["type"].startswith("opt("):
                errors.append(f"{k} is missing from the template variable definition file")
            if k in template_variables:
                if type(template_variables[k]) != typeMap(v["type"]):
                    errors.append(f"Type {v['type']} does not match provided type for template variable {k}")
                invalid = validateVariable(template_variables[k], v)
                if invalid:
                    errors.append(invalid)
        if errors:
            raise TemplateVariableValidation("Template variable validation exception", errors)
    except KeyError:
        pass


class TemplateVariableValidation(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors


def getManifest(directory):
    manifest_file = os.path.join(directory, "manifest.cxa.yml")
    if not os.path.exists(manifest_file):
        print("Check that the path contains the manifest.cxa.yml file")
        raise FileNotFoundError(f"{manifest_file} not found")
    with open(manifest_file, "r") as f:
        return yaml.safe_load(f)


def getTemplateVariables(filename, variables):
    template_variables = dict()
    if filename is not None:
        if not os.path.exists(filename):
            print("This template uses variables, the template file you provided doesn't exist")
            raise FileNotFoundError(f"{filename} doesn't exist")
        else:
            with open(filename, "r") as file:
                template_variables = json.load(file, encoding="utf-8")
    elif variables:
        template_variables = {
            str(x[0]).split("=")[0]: convertType("=".join(str(x[0]).split("=")[1:])) for x in variables
        }
    return template_variables


def convertType(val):
    constructors = [strtobool, int, float, str]
    for c in constructors:
        try:
            return c(val)
        except ValueError:
            pass


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
            if isinstance(definition["validation"], str):
                if definition["validation"].startswith(k):
                    rule = definition["validation"]
                    rule = re.fullmatch(k + r"\((.*)\)", rule).group(1)
                    if (re.search(rule, toValidate) is None) == v:
                        return f"{toValidate} failed to validate with rule: {rule}"
        if isinstance(definition["validation"], dict):
            if "min" in definition["validation"]:
                if toValidate < definition["validation"]["min"]:
                    return f"{toValidate} must be greater than or equal to {definition['validation']['min']}"
            if "max" in definition["validation"]:
                if toValidate >= definition["validation"]["max"]:
                    return f"{toValidate} must be less than {definition['validation']['max']}"

    return None
