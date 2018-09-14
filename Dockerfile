FROM python:3.7-slim

RUN mkdir /app
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .
RUN pip install --editable .

LABEL maintainer="Tomasz Naskręt <tomasz.naskret@pwr.edu.pl>"

CMD gunicorn -c "python:config.gunicorn" "text_geocoder.app:create_app()"
