# Create-X-App

## Installation

-   Install Pipenv
-   Clone this repository
-   Run `pipenv install`

## Test Run

-   Create a `template.json` file such as:

```
{
    "project_name": "TestProject",
    "project_human_name": "Test Project 1",
    "author": "Michael Dombrowski",
    "max_line_length": 120
}
```

-   Run `pipenv run python ./src/cxa/main.py -g https://github.com/MikeDombo/CXAPythonCLI.git -o ../CXATest -f ../template.json`
