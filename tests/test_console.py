import datetime
import textwrap
from pathlib import Path
from typing import List

import pytz
from click.testing import CliRunner

from fit_query import database
from fit_query.console import cli
from fit_query.database import Activity

TEST_DB = Path('/tmp/test.db')


def test_importing_files():
    runner = CliRunner(env={'DB_PATH': ':memory:'})
    result = runner.invoke(cli, ['import', './files/'], catch_exceptions=False)
    assert 'Saved 1/1.' in result.output


def test_querying_activities_defaults():
    runner = CliRunner(env={'DB_PATH': str(TEST_DB)})
    activities = [
        Activity(
            md5sum='a8ea8b7f501650fc836841db0cbdf3dd',
            filename='foo1.fit',
            start_time=datetime.datetime(2022, 6, 7, 8, 30, 0, tzinfo=pytz.UTC),
            sport='running',
            total_distance=9876,
        ),
        Activity(
            md5sum='a8ea8b7f501650fc836841db0cbdf3de',
            filename='foo2.fit',
            start_time=datetime.datetime(2022, 6, 8, 8, 30, 0, tzinfo=pytz.UTC),
            sport='running',
            total_distance=12345,
        )
    ]
    _prepare_test_db(activities)
    result = runner.invoke(cli, ['--show-sql', 'query'], catch_exceptions=False)
    expected = textwrap.dedent("""
        Start time           Sport      Dist. (km)
        -------------------  -------  ------------
        2022-06-08 10:30:00  running         12.35
        2022-06-07 10:30:00  running          9.88
    """).lstrip()
    assert result.output.endswith(expected)
    _cleanup_test_db()


def test_querying_with_filters():
    runner = CliRunner(env={'DB_PATH': str(TEST_DB)})
    activities = [
        Activity(
            md5sum='a8ea8b7f501650fc836841db0cbdf3dd',
            filename='foo1.fit',
            start_time=datetime.datetime(2022, 6, 7, 8, 30, 0, tzinfo=pytz.UTC),
            sport='running',
            total_distance=9876,
        ),
        Activity(
            md5sum='a8ea8b7f501650fc836841db0cbdf3de',
            filename='foo2.fit',
            start_time=datetime.datetime(2022, 6, 8, 8, 30, 0, tzinfo=pytz.UTC),
            sport='hiking',
            total_distance=12345,
        ),
        Activity(
            md5sum='b8ea8b7f501650fc836841db0cbdf3de',
            filename='foo3.fit',
            start_time=datetime.datetime(2022, 6, 9, 8, 30, 0, tzinfo=pytz.UTC),
            sport='running',
            total_distance=11987,
        )
    ]
    _prepare_test_db(activities)
    result = runner.invoke(cli, ['--show-sql', 'query', '--sport', 'running'], catch_exceptions=False)
    expected = textwrap.dedent("""
        Start time           Sport      Dist. (km)
        -------------------  -------  ------------
        2022-06-09 10:30:00  running         11.99
        2022-06-07 10:30:00  running          9.88
    """).lstrip()
    assert result.output.endswith(expected)
    _cleanup_test_db()


def _prepare_test_db(activities: List[Activity]):
    _cleanup_test_db()
    database.init_db(TEST_DB)
    [a.save() for a in activities]
    database.db.close()


def _cleanup_test_db():
    TEST_DB.unlink(missing_ok=True)
