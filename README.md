# Create-X-App
Templated application creation system. Just choose a template and provide values for its variables and have a working system
running immediately. 

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

-   Run `pipenv run python cxa.py main -g https://github.com/MikeDombo/CXAPythonCLI.git -o ../CXATest -f ../template.json`
