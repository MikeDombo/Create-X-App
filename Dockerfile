FROM python:3.7-alpine
RUN apk update && apk add --virtual git
RUN pip install --no-cache-dir --trusted-host pypi.python.org pipenv
COPY . .
RUN pipenv install --system --deploy
RUN pipenv install gunicorn

EXPOSE 8000
ENTRYPOINT [ "pipenv", "run", "gunicorn", "--bind", "0.0.0.0:8000", "src.cxa.server:api" ]
