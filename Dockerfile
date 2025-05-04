FROM python:3.12-slim

WORKDIR /main

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

ENV PYTHONPATH=/main/src

EXPOSE 8501

ENTRYPOINT ["run", "src/app.py"]
