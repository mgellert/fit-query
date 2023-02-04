import hashlib
from pathlib import Path
from typing import List, Optional, Tuple, Any, Dict, Set

import click
import pytz
from fitparse import FitFile

from fit_query.database import Activity

ALLOWED_EXTENSIONS = ['.fit']


def parse_workouts(workout_dir: Path, already_saved: Set[str]) -> List[Dict[str, Any]]:
    files: List[Path] = [file for file in _collect_files(workout_dir) if file.suffix in ALLOWED_EXTENSIONS]
    files = [file for file in files if _get_md5sum(file) not in already_saved]

    len_files = len(files)
    if len_files == 0:
        click.echo("No unparsed file found.")

    return [_parse_file(file, len_files, i + 1) for (i, file) in enumerate(files)]


def _parse_file(file: Path, len_files: int, i: int) -> Dict[str, Any]:
    md5sum = _get_md5sum(file)
    fit_file = FitFile(str(file))
    session = fit_file.get_messages(name="session", as_dict=True)
    fields = {field["name"]: field["value"] for field in next(session)["fields"] if
              field["name"] in vars(Activity)}

    fields["start_time"] = pytz.utc.localize(fields["start_time"])

    fields["md5sum"] = md5sum
    fields["filename"] = file.name

    lat, long = _get_starting_lat_lon(fit_file)
    fields["start_position_lat"] = lat
    fields["start_position_long"] = long

    click.echo(f"Parsed {i}/{len_files}.")
    return fields


def _collect_files(path):
    for p in path.iterdir():
        if p.is_dir():
            yield from _collect_files(p)
            continue
        yield p.resolve()


def _get_md5sum(path: Path) -> str:
    with open(path, "rb") as file:
        return hashlib.md5(file.read()).hexdigest()


def _convert_semicircles(semicircles: int) -> float:
    return semicircles * (180 / 2 ** 31)


def _get_starting_lat_lon(fit_file: FitFile) -> Tuple[Optional[float], Optional[float]]:
    records = fit_file.get_messages(name="record", as_dict=True)
    # select first record that has geo data
    try:
        geo_record = next(r["fields"] for r in records if any(y["name"] == "position_lat" for y in r["fields"]))
    except StopIteration:
        return None, None

    fields = {field['name']: field['value'] for field in geo_record}
    return _convert_semicircles(fields['position_lat']), _convert_semicircles(fields['position_long'])
