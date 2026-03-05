#!/bin/bash
# Start Jupyter Lab and Voilà side by side.
# Jupyter Lab : port 8888  (full notebook interface, code visible)
# Voilà       : port 8889  (rendered app interface, code hidden)

jupyter lab \
  --ip=0.0.0.0 \
  --port=8888 \
  --no-browser \
  --NotebookApp.token='' \
  --allow-root &

voila \
  --port=8889 \
  --no-browser \
  --token='' \
  --Voila.ip=0.0.0.0 \
  /workspace/notebooks &

wait
