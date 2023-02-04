import logging
import operator
import os
from datetime import datetime, timedelta
from functools import reduce
from pathlib import Path
from typing import Set, List

from peewee import Model, FloatField, CharField, DateTimeField, IntegerField, AutoField, TimestampField, SqliteDatabase, \
    fn

db = SqliteDatabase(None)


class Activity(Model):
    id = AutoField()
    md5sum = CharField(null=False, unique=True)
    filename = CharField(null=False, unique=True)
    start_time = DateTimeField(null=False)
    sport = CharField(null=False)
    total_distance = FloatField(null=True)  # m
    avg_heart_rate = IntegerField(null=True)
    max_heart_rate = IntegerField(null=True)
    enhanced_avg_speed = FloatField(null=True)  # m/s
    enhanced_max_speed = FloatField(null=True)  # m/s
    total_calories = IntegerField(null=True)  # kcal
    total_timer_time = FloatField(null=True)  # s
    total_elapsed_time = FloatField(null=True)  # s
    total_ascent = IntegerField(null=True)  # m
    total_descent = IntegerField(null=True)  # m
    enhanced_max_altitude = FloatField(null=True)  # m
    enhanced_min_altitude = FloatField(null=True)  # m
    total_training_effect = FloatField(null=True)
    feeling = IntegerField(null=True)
    start_position_lat = FloatField(null=True)
    start_position_long = FloatField(null=True)
    created_at = TimestampField()

    def total_distance_km(self) -> float:
        if not self.total_distance:
            return 0.0
        return self.total_distance / 1000

    class Meta:
        database = db


def init_db(path: Path):
    path.parents[0].mkdir(exist_ok=True)
    db.init(str(path))
    db.connect()
    db.create_tables([Activity])


def save(fields):
    Activity(**fields).save()


def all_hashes() -> Set[str]:
    return {a.md5sum for a in Activity.select(Activity.md5sum)}


def find(since: datetime, until: datetime, sport: str, year: int, month: int, limit: int) -> List[Activity]:
    query = Activity.select()

    clauses = []
    if since:
        clauses.append(Activity.start_time >= since)
    if until:
        until = until + timedelta(hours=23, minutes=59, seconds=59)
        clauses.append(Activity.start_time <= until)
    if sport:
        clauses.append(Activity.sport == sport)
    if year:
        clauses.append(fn.strftime('%Y', Activity.start_time).cast('integer') == year)
    if month:
        clauses.append(fn.strftime('%m', Activity.start_time).cast('integer') == month)

    if len(clauses) > 0:
        query = query.where(reduce(operator.and_, clauses))

    query = query.order_by(Activity.start_time.desc())

    if limit:
        query = query.limit(limit)

    return list(query)
