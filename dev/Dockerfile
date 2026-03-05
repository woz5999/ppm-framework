FROM python:3.11-slim

COPY requirements.txt dev/requirements-dev.txt ./
RUN pip install -r requirements-dev.txt

WORKDIR /workspace
EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser", "--NotebookApp.token=''", "--allow-root"]
