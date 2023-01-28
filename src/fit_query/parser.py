import hashlib
from pathlib import Path
from typing import List, Optional, Tuple, Any, Dict

import pytz
from fitparse import FitFile

from fit_query.database import Activity


def parse_workouts(workout_dir: Path) -> List[Dict[str, Any]]:
    files: List[Path] = list(_collect_files(workout_dir))
    parsed = list()

    for file in files:
        fit_file = FitFile(str(file))
        session = fit_file.get_messages(name="session", as_dict=True)
        fields = {field["name"]: field["value"] for field in next(session)["fields"] if
                  field["name"] in vars(Activity)}

        fields["start_time"] = pytz.utc.localize(fields["start_time"])

        fields["md5sum"] = _get_md5sum(file)
        fields["filename"] = file.name

        lat, long = _get_starting_lat_lon(fit_file)
        fields["start_position_lat"] = lat
        fields["start_position_long"] = long

        parsed.append(fields)

    return parsed


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
