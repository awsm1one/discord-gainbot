FROM python:3.8.4
LABEL org.opencontainers.image.source https://github.com/awsm1one/discord-gainbot

COPY requirements.txt /

RUN pip install -r requirements.txt

COPY main.py /
COPY utils /utils

CMD [ "python", "./main.py" ]
