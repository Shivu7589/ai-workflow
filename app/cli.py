from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.src.models.chart_schemas import ChartConfig
from app.src.services import ai_config_generator, chart_renderer, datasource_loader

def _write_figure(fig, out: Path) -> None:
    if out.suffix.lower() == ".json":
        out.write_text(json.dumps(fig.to_plotly_json(), default=str), encoding="utf-8")
    else:
        out.write_text(fig.to_html(include_plotlyjs="cdn", full_html=True), encoding="utf-8")

def _cmd_render(args: argparse.Namespace) -> int:
    df, _ = datasource_loader.load_path(args.data)
    raw = json.loads(Path(args.config).read_text(encoding="utf-8"))
    cfg = ChartConfig(**raw)
    fig = chart_renderer.render(df, cfg)
    out = Path(args.out)
    _write_figure(fig, out)
    print(f"Wrote {out.resolve()}")
    return 0

def _cmd_ai_render(args: argparse.Namespace) -> int:
    df, _ = datasource_loader.load_path(args.data)
    cfg = ai_config_generator.generate_config(args.prompt, df)
    fig = chart_renderer.render(df, cfg)
    out = Path(args.out)
    _write_figure(fig, out)
    print(f"Wrote {out.resolve()} (chart_type={cfg.chart_type})")
    return 0

def _cmd_ai_config(args: argparse.Namespace) -> int:
    df, _ = datasource_loader.load_path(args.data)
    cfg = ai_config_generator.generate_config(args.prompt, df)
    payload = json.dumps(cfg.model_dump(), indent=2)
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
        print(f"Wrote {Path(args.out).resolve()}")
    else:
        print(payload)
    return 0

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lite-chart-studio")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("render", help="Render a chart from data + config files.")
    p.add_argument("--data", required=True)
    p.add_argument("--config", required=True)
    p.add_argument("--out", default="chart.html")
    p.set_defaults(func=_cmd_render)

    p = sub.add_parser("ai-render", help="Prompt -> LLM config -> rendered chart.")
    p.add_argument("--data", required=True)
    p.add_argument("--prompt", required=True)
    p.add_argument("--out", default="chart.html")
    p.set_defaults(func=_cmd_ai_render)    

    p = sub.add_parser("ai-config", help="Prompt -> LLM config -> printed or saved as JSON")
    p.add_argument("--data", required=True)
    p.add_argument("--prompt", required=True)
    p.add_argument("--out", default=None, help="Optional path to save the config JSON.")
    p.set_defaults(func=_cmd_ai_config)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())    