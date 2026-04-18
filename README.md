# mydeck-hello-plugin

Sample external plugin for [mydeck](https://github.com/ktat/mydeck). Demonstrates how a third-party package can ship a mydeck app by using mydeck's dotted-path loader.

## What it does

`CpuPie` draws a live CPU-time pie chart on a STREAM DECK key, with the active-CPU percentage shown as the label. Segments are colored by category:

| Color | Category |
|---|---|
| green | user |
| light green | nice |
| red | system |
| amber | irq + softirq |
| orange | iowait |
| purple | steal / guest |
| dark gray | idle |

## Install

The plugin must land in the **same Python environment as `mydeck`**, because that's where the dotted-path loader will look for it.

### If you installed mydeck with `pip install`

```
pip install .            # from this directory
# or
pip install git+https://github.com/ktat/mydeck-hello-plugin.git
```

### If you installed mydeck with `uv tool install`

`uv tool install` puts `mydeck` in its own isolated venv, so a plain `pip install` won't make the plugin visible to it. Target the tool's Python explicitly:

```
uv pip install --python ~/.local/share/uv/tools/mydeck/bin/python3 \
  git+https://github.com/ktat/mydeck-hello-plugin.git
```

Or reinstall `mydeck` with the plugin included from the start:

```
uv tool install --reinstall --with git+https://github.com/ktat/mydeck-hello-plugin.git mydeck
```

After installing, restart mydeck (`mydeck --restart -d`) — Python reads `site-packages` only at interpreter startup, so a running process won't see the new plugin until it restarts.

## Use

Add it to your deck's YAML config (`~/.config/mydeck/<serial>.yml`):

```yaml
apps:
  - app: mydeck_hello.cpu_pie.CpuPie
    option:
      page_key:
        '@HOME': 5
      interval: 2        # seconds between samples; default 2
```

Restart `mydeck` (or just re-enter the page) and the key at position 5 on the home page will show the live pie chart.

## How the plugin mechanism works

`mydeck` parses `app:` values as follows:

- **Short name** (no dots) — resolved against the built-in `mydeck.app_*` modules. `app: Clock` → `mydeck.app_clock.AppClock`.
- **Dotted path** — imported verbatim. `app: mydeck_hello.cpu_pie.CpuPie` → `from mydeck_hello.cpu_pie import CpuPie`.

A plugin class just needs to subclass one of the mydeck base classes:

- `mydeck.ThreadAppBase` — runs `set_image_to_key` on a loop (this plugin uses it)
- `mydeck.BackgroundAppBase` — always-on, regardless of page
- `mydeck.HookAppBase` — runs on lifecycle hooks (e.g., `page_change`)
- `mydeck.TouchAppBase` — touchscreen interactions on Plus
- `mydeck.GameAppBase` — games on the `@GAME` page

See `docs/make_your_app.md` in the mydeck repo for the full contract.

## License

MIT
