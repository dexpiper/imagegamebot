FROM ubuntu:22.04 AS imagegamebot

RUN apt-get update && apt-get install -y -q \
        python3                             \
        python3-pip
ADD . imagegamebot
RUN cd imagegamebot && pip --no-cache-dir install -r requirements.txt
WORKDIR /imagegamebot
ENTRYPOINT python3 /imagegamebot/bot.py
