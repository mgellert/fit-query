import logging
import os
from datetime import datetime
from pathlib import Path

import click
from tabulate import tabulate, SEPARATING_LINE

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
@click.option('--since', type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option('--until', type=click.DateTime(formats=["%Y-%m-%d"]))
@click.option('--sport', type=str)
@click.option('--year', type=int)
@click.option('--month', type=click.IntRange(min=1, max=12))
@click.option('--limit', type=int)
@click.option('--reverse', type=bool, default=False, is_flag=True)
@click.option('--summary/--no-summary', type=bool, default=True)
def query(since: datetime, until: datetime, sport: str, year: int, month: int, limit: int, reverse: bool,
          summary: bool):
    activities = database.find(since, until, sport, year, month, limit)
    data = []
    for a in activities:
        data.append([
            datetime.strptime(a.start_time, '%Y-%m-%d %H:%M:%S%z').astimezone().strftime('%Y-%m-%d %H:%M:%S'),
            a.sport,
            f"{a.total_distance_km():.2f}"
        ])

    if reverse:
        data.reverse()

    if summary:
        different_sports = len({activity.sport for activity in activities})
        sum_distance_km = sum([activity.total_distance_km() for activity in activities])
        summary = [
            f"Count: {len(data)}",
            f"Sports: {different_sports}",
            sum_distance_km
        ]
        data.append(SEPARATING_LINE)
        data.append(summary)

    table = tabulate(data, headers=["Start time", "Sport", "Dist. (km)"], floatfmt=".2f")
    click.echo(table)


cli.add_command(import_files)
cli.add_command(query)

if __name__ == '__main__':
    cli()
