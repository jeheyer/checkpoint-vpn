FROM python:3.11
WORKDIR /tmp
COPY ./requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ENV PORT=8080
ENV APP_DIR=/opt
#ENV APP_APP=app:app
ENV APP_APP=wsgi:app
COPY app.py $APP_DIR
COPY wsgi.py $APP_DIR
COPY main.py $APP_DIR
COPY settings.yaml $APP_DIR
COPY templates $APP_DIR/templates
#ENTRYPOINT cd $APP_DIR && hypercorn -b 0.0.0.0:$PORT -w 1 --access-logfile '-' $APP_APP
ENTRYPOINT cd $APP_DIR && gunicorn -b 0.0.0.0:$PORT -w 1 --access-logfile '-' $APP_APP
EXPOSE $PORT
