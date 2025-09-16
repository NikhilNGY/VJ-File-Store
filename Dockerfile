FROM python:3.10.8-slim-bullseye

RUN apt update && apt upgrade -y
RUN apt install git -y

COPY requirements.txt /requirements.txt
RUN pip3 install --no-cache-dir -U pip && pip3 install --no-cache-dir -U -r /requirements.txt

RUN mkdir /VJ-File-Store
WORKDIR /VJ-File-Store
COPY . /VJ-File-Store

CMD ["python", "bot.py"]