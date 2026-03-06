# Fly.io Deployment

Serves the notebook as a Voilà app (widgets only, no code visible) with scale-to-zero.
The machine sleeps when idle and wakes in ~10-15s on first request.

## One-time setup

```bash
# Install flyctl
brew install flyctl          # Mac
curl -L https://fly.io/install.sh | sh   # Linux/WSL

fly auth login
fly apps create <your-app-name>   # must be globally unique on Fly.io
```

Update `app = "..."` in `fly.toml` to match the name you created.

## Deploy

```bash
fly deploy --no-cache
```

`--no-cache` forces Fly to pull the latest GHCR image fresh. Always use it.

## Redeploy after changes

Push to main → GitHub Action rebuilds and pushes `latest` to GHCR → then:

```bash
fly deploy --no-cache
```

## Notes

- `--strip_sources=True` in `fly.toml` hides notebook code from viewers. Remove it to show code.
- Machine size is `shared-cpu-1x` / 512MB RAM.
- To keep one machine always warm (no cold starts), set `min_machines_running = 1` (~$2-4/month).
