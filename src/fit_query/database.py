import os
from datetime import datetime

from peewee import SqliteDatabase, Model, FloatField, CharField, DateTimeField, IntegerField, AutoField, TimestampField


def save(fields):
    Activity(**fields)


def create_db():
    is_test = os.getenv('TEST')
    if is_test:
        return SqliteDatabase(':memory:')
    else:
        raise Exception('Not yet implemented')


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
        return self.total_distance / 1000
