FROM python:3.11-slim

WORKDIR /app

ARG ILIVALIDATOR_VERSION=1.15.0
ENV ILIVALIDATOR_JAR=/opt/ilivalidator/ilivalidator.jar

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl default-jre-headless unzip \
    && curl -fsSL "https://downloads.interlis.ch/ilivalidator/ilivalidator-${ILIVALIDATOR_VERSION}.zip" -o /tmp/ilivalidator.zip \
    && mkdir -p /opt/ilivalidator \
    && unzip -q /tmp/ilivalidator.zip -d /opt/ilivalidator \
    && validator_jar="$(find /opt/ilivalidator -type f -name 'ilivalidator*.jar' | head -n 1)" \
    && test -n "$validator_jar" \
    && ln -sf "$validator_jar" /opt/ilivalidator/ilivalidator.jar \
    && test -f /opt/ilivalidator/ilivalidator.jar \
    && rm -rf /var/lib/apt/lists/* /tmp/ilivalidator.zip

COPY shared ./shared
COPY worker .

RUN pip install -r requirements.txt

CMD ["python", "worker.py"]
