# Dev container that mirrors Binder's environment.
#
# Built from Project Jupyter's curated scipy-notebook image — same Jupyter
# team that maintains the stack mybinder.org's repo2docker uses. JupyterLab,
# ipywidgets (federated extensions registered correctly), numpy/scipy/
# matplotlib/pandas, and Python 3.11 are all present and known to work
# together. What runs here runs on Binder.
#
# Build:  docker build -t ppm-dev -f dev/Dockerfile .
# Run:    docker run --rm -p 8888:8888 -p 8889:8889 ppm-dev
#         JupyterLab on http://localhost:8888  (matches Binder)
#         Voila      on http://localhost:8889  (matches Fly)

FROM quay.io/jupyter/scipy-notebook:python-3.11

USER root
WORKDIR /home/jovyan/work
COPY --chown=jovyan:users . /home/jovyan/work/

USER jovyan

# Install the same project deps mybinder.org installs from binder/, plus
# voila and pytest for the local dev workflow. Most numerical deps are
# already in the base image; this ensures versions match the Binder spec.
RUN pip install --no-cache-dir -r binder/requirements.txt voila pytest && \
    pip install --no-cache-dir --no-deps .

EXPOSE 8888 8889
CMD ["/home/jovyan/work/dev/start.sh"]
