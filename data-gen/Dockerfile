FROM python:3.6

ENV SERV_DIR /app

COPY requirements.txt $SERV_DIR/requirements.txt

RUN pip3 install -r $SERV_DIR/requirements.txt

COPY . $SERV_DIR

WORKDIR $SERV_DIR

CMD ["python3", "run.py"]
