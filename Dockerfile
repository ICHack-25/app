FROM python:3.9
RUN pip install pipenv
WORKDIR /app
COPY ./flask .
RUN ls -l /app
RUN pipenv install --system
CMD gunicorn app:app -b 0.0.0.0:8080