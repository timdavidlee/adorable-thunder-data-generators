import asyncio
import logging

import typer

from adorable_thunder.scrutinize.agent.agent_definition import scrutinize

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)

app = typer.Typer()


@app.command()
def main(
    flow: str = typer.Argument(help="Enterprise flow name, e.g. procure-to-pay, order-to-cash"),
):
    report = asyncio.run(scrutinize(flow))
    typer.echo(report.model_dump_json(indent=2))


if __name__ == "__main__":
    app()
