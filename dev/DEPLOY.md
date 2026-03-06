# Fly.io Deployment

Serves the notebook as a Voilà app (widgets only, no code visible) with scale-to-zero — the machine sleeps when idle and wakes in ~10-15s on first request.

## One-time setup

```bash
# Install flyctl
brew install flyctl          # Mac
curl -L https://fly.io/install.sh | sh   # Linux/WSL

fly auth login
```

## Deploy

App names are globally unique across all Fly.io users. Pick something like `ppm-voila` or `ppm-framework-jw`, update the `app =` line in `fly.toml`, then:

```bash
# From repo root
fly apps create <your-app-name>
fly deploy
```

Your app will be live at `https://<your-app-name>.fly.dev`.

## Redeploy after changes

The `fly/Dockerfile` pulls `ghcr.io/woz5999/ppm-framework:latest`. After pushing a new image via the GitHub Action, redeploy with:

```bash
fly deploy
```

## Notes

- `--strip_sources=True` in `fly/Dockerfile` hides notebook code from viewers. Remove it to show code.
- Machine size is `shared-cpu-1x` / 512MB — sufficient for a handful of concurrent users.
- To always keep one machine warm (no cold starts), set `min_machines_running = 1` in `fly.toml` (~$2-4/month).
