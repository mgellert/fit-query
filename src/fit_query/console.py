import pathlib

import click

import src.fit_query.parser as parser
from fit_query import database


@click.group()
def cli():
    db = database.create_db()
    db.connect()
    db.create_tables([database.Activity])


@click.command(name='import')
@click.argument('workout_dir', type=click.Path(exists=True, file_okay=False, path_type=pathlib.Path))
def import_files(workout_dir: pathlib.Path):
    parsed = parser.parse_workouts(workout_dir)
    total = len(parsed)
    for i, fields in enumerate(parsed):
        database.save(fields)
        click.echo(f"Saved {i + 1}/{total}.")


@click.command()
def query():
    pass


cli.add_command(import_files)
cli.add_command(query)



if __name__ == '__main__':
    cli()
