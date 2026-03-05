FROM python:3.11-slim

COPY requirements.txt dev/requirements-dev.txt dev/start.sh ./
RUN pip install -r requirements-dev.txt && chmod +x start.sh

WORKDIR /workspace
EXPOSE 8888 8889

CMD ["/start.sh"]
