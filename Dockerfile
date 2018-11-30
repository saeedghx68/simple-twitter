FROM python:3.7
RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN pip install -r requirements.txt
CMD chmod +x ./wait-for-it.sh ; ./wait-for-it.sh db:5432 ; python -m sanic server.app --host=0.0.0.0 --port=2080 --workers=12