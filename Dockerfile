from python:3

MAINTAINER liangiydon@gmail.com 82015697@qq.com

COPY . /app
WORKDIR /app

RUN pip install pipenv \
    && pipenv install --system --deploy \
    && export FLASK_APP=code

CMD ["flask", "run"]
