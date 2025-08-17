FROM python:3.13

WORKDIR /app

COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt

COPY ./ ./

CMD [ "python3", "main.py" ]
