FROM python:3-alpine

ENV BOT_TOKEN=''

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

#RUN #--mount=type=cache,id=custom-pip,target=/root/.cache/pip pip install -r req.txt

CMD ["python3", "main.py"]
