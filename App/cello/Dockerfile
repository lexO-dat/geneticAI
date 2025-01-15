FROM openjdk:11-jre-slim as java-base
FROM python:3.11-slim-buster
COPY --from=java-base /usr/local/openjdk-11 /usr/local/openjdk-11
ENV PATH="/usr/local/openjdk-11/bin:${PATH}"
RUN apt update && apt install -y build-essential yosys && apt clean
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "run.py"]