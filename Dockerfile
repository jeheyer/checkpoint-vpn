FROM python:3.11-slim-bullseye
WORKDIR /tmp
COPY ./requirements.txt ./
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
ENV PORT=8000
ENV APP_DIR=/opt
ENV APP_APP=app:app
COPY app.py $APP_DIR
COPY main.py $APP_DIR
COPY settings.yaml $APP_DIR
ENTRYPOINT hypercorn --reload -b 0.0.0.0:$PORT -w 1 --chdir=$APP_DIR --access-logfile '-' $APP_APP
EXPOSE $PORT