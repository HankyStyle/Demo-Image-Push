FROM python:3.6.9

WORKDIR /demo

ADD . /demo

RUN pip install -r requirements.txt

COPY . .

CMD uvicorn app:app --reload
