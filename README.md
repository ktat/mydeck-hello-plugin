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

```
pip install .            # from this directory
# or
pip install git+https://github.com/<your-fork>/mydeck-hello-plugin.git
```

This installs `mydeck_hello` into the same environment as `mydeck`, which is what the dotted-path loader needs.

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
