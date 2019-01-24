FROM python:3.7-alpine
RUN apk update && apk add --virtual git
RUN pip install --no-cache-dir --trusted-host pypi.python.org pipenv
COPY Pipfile ./
COPY Pipfile.lock ./
RUN pipenv install --system --deploy
RUN pipenv install gunicorn
COPY cxa.py cxa.py
COPY src/ ./src

EXPOSE 8000
ENTRYPOINT [ "pipenv", "run", "gunicorn", "--bind", "0.0.0.0:8000", "src.cxa.server:api" ]