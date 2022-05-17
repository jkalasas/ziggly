FROM python:3

ENV APP_HOME=/usr/src/ziggly
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

COPY . $APP_HOME
RUN pip install -r requirements.txt

ENTRYPOINT ["sh", "entrypoint.sh"]