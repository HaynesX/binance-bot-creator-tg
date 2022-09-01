FROM python:3.8

RUN mkdir -p /home/binance-bot-creator-tg
WORKDIR /home/binance-bot-creator-tg

COPY requirements.txt /home/binance-bot-creator-tg

RUN pip install -r /home/binance-bot-creator-tg/requirements.txt

COPY . /home/binance-bot-creator-tg