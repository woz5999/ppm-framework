FROM python:3.11-slim

RUN pip install jupyterlab

COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /workspace
EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser", "--NotebookApp.token=''", "--allow-root"]
