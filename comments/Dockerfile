FROM python:3.10-slim

WORKDIR /usr/src/app

COPY ./app /usr/src/app

RUN pip install --no-cache-dir fastapi[all] motor pymongo

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]