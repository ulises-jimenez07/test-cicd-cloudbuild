FROM python:3.12-slim
RUN apt-get update

WORKDIR /app
COPY . ./

ENV PORT 8000
RUN pip3 install --no-cache-dir -r requirements.txt
EXPOSE 8000 
CMD exec uvicorn main:app --host 0.0.0.0 --port 8000