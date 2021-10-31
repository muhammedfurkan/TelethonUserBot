FROM ubuntu:latest
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y unace unrar zip unzip p7zip-full p7zip-rar sharutils rar
RUN apt-get install -y ffmpeg
RUN apt-get install python3 git python3-pip -y
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2 \
    && rm -rf /root/.cache/pip/ \
    && find / -name '*.pyc' -delete \
    && find / -name '*__pycache__*' -delete
RUN pip3 install -U psycopg2-binary
RUN cd /
RUN git clone https://github.com/muhammedfurkan/TelethonUserBot.git
RUN cd TelethonUserBot
WORKDIR /TelethonUserBot
RUN pip3 install --no-cache-dir -r requirements.txt
CMD python3 -m userbot
