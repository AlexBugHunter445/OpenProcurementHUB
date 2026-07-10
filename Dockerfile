FROM python:3.13-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e packages/core -e packages/connector-sdk -e packages/connector-belgium -e packages/api -e packages/cli -e packages/sdk-python
EXPOSE 8000
CMD ["oph-api"]
