FROM python:3.11

RUN apt update
RUN apt install -y python3-dev default-libmysqlclient-dev build-essential

RUN mkdir /root/prog
WORKDIR /root/prog

COPY ./ /root/prog
RUN pip install -r requirements.txt

CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:80", "--reload"]
