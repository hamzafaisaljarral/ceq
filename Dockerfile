FROM python:3.9

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN  pip install -r requirements.txt


COPY . .

EXPOSE 5000


ENV DEBUG=0
ENV UNOC_MONGO_DB=ceq
ENV UNOC_MONGO_HOST="mongodb://localhost:27017/"

CMD ["python", "app.py"]