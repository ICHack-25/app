FROM python:3.9
WORKDIR /app
COPY ./flask .
RUN ls -l /app
RUN pip install --no-cache-dir -r requirements.txt
CMD gunicorn app:app -b 0.0.0.0:8080