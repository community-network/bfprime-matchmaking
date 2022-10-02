FROM python:3

WORKDIR /usr/src/app

ENV token default_token_value
ENV mongo default_mongo_value

COPY ./requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

HEALTHCHECK CMD discordhealthcheck || exit 1

CMD [ "python", "./bot.py" ]
