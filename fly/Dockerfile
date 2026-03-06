# Pull the pre-built Binder image from GHCR and serve only Voilà.
# The repo content is at /home/jovyan/ inside the repo2docker image.
FROM ghcr.io/woz5999/ppm-framework:latest

EXPOSE 8889

CMD ["/srv/conda/envs/notebook/bin/voila", \
     "/home/jovyan/notebooks/constraint_sensitivity.ipynb", \
     "--port=8889", \
     "--no-browser", \
     "--Voila.ip=0.0.0.0", \
     "--strip_sources=True"]
