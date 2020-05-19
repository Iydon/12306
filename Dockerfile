from python:3

MAINTAINER liangiydon@gmail.com

COPY . /app
WORKDIR /app

RUN pip install pipenv \
    && pipenv install --system --deploy

CMD ["python", "app.py"]
