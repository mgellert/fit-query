import logging
import os
from datetime import datetime
from pathlib import Path

import click
from tabulate import tabulate

import src.fit_query.parser as parser
from fit_query import database


@click.group()
@click.option('--show-sql', default=False, is_flag=True)
def cli(show_sql: bool):
    if show_sql:
        logger = logging.getLogger('peewee')
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)

    env_path = os.getenv('DB_PATH') and Path(os.getenv('DB_PATH'))
    home_path = Path.home() / '.fit-query' / 'fit-query.db'
    database.init_db(env_path or home_path)


@click.command(name='import')
@click.argument('workout_dir', type=click.Path(exists=True, file_okay=False, path_type=Path))
def import_files(workout_dir: Path):
    already_saved = database.all_hashes()
    parsed = parser.parse_workouts(workout_dir, already_saved)

    total = len(parsed)
    for i, fields in enumerate(parsed):
        database.save(fields)
        click.echo(f"Saved {i + 1}/{total}.")


@click.command()
@click.option('--since', default='1900-01-01', type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option('--until', default='2100-01-01', type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option('--limit', default=20, type=int)
def query(since, until, limit):
    activities = database.find(since, until, limit)
    data = []
    for a in activities:
        data.append([
            datetime.strptime(a.start_time, '%Y-%m-%d %H:%M:%S%z').astimezone().strftime('%Y-%m-%d %H:%M:%S'),
            a.sport,
            f"{a.total_distance_km():.2f}"
        ])
    table = tabulate(data, headers=["Start time", "Sport", "Dist. (km)"])
    click.echo(table)


cli.add_command(import_files)
cli.add_command(query)

if __name__ == '__main__':
    cli()
