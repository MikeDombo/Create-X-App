from setuptools import setup
import sys

from pathlib import Path  # noqa E402

CURRENT_DIR = Path(__file__).parent


def get_long_description() -> str:
    readme_md = CURRENT_DIR / "README.md"
    with open(readme_md, encoding="utf8") as file:
        return file.read()


setup(
    name="Create X App",
    version=1,
    description="",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="",
    author_email="",
    url="",
    license="BSD 3-clause",
    python_requires=">=3.6",
    entry_points={"console_scripts": ["main=src.cxa.main:main"]},
)
