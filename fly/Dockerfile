FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    numpy~=2.0 \
    scipy~=1.13 \
    matplotlib~=3.9 \
    ipywidgets~=8.0 \
    voila~=0.5 \
    ipykernel

RUN python -m ipykernel install --sys-prefix

# Copy and install the ppm package
COPY ppm/ ./ppm/
COPY pyproject.toml ./
RUN pip install --no-deps .

# Copy notebooks
COPY notebooks/ ./notebooks/

EXPOSE 8889

CMD ["voila", "/app/notebooks/", \
     "--port=8889", \
     "--no-browser", \
     "--Voila.ip=0.0.0.0", \
     "--strip_sources=True"]
