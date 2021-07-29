
# FROM debian:latest

# RUN apt update && apt upgrade -y
# RUN apt install python3 python3-dev python3.8-dev megatools git curl python3-pip ffmpeg -y
# RUN pip3 install -U pip

FROM ubuntu:latest
RUN apt-get -y update
RUN apt-get install python3 git python3-pip -y
RUN cd /
RUN git clone https://github.com/muhammedfurkan/TelethonUserBot.git
RUN cd TelethonUserBot
WORKDIR /TelethonUserBot
RUN pip3 install -U -r requirements.txt
CMD python3 -m userbot
