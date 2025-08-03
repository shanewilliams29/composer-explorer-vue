from datetime import datetime, timedelta
from flask import session
from app.cron.logging_config import logger
from app.spotify import SpotifyAPI
from config import Config

RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"

sp = SpotifyAPI(Config.SPOTIFY_BACKGROUND_ID, Config.SPOTIFY_BACKGROUND_SECRET, Config.SPOTIFY_BACKGROUND_URL)


class Timer(object):

    def __init__(self, start_time):
        self.start_time = start_time
        self.elapsed = 0

    def set_loop_length(self, length):
        self.loop_length = length

    def print_status_update(self, count, errors):
        current_time = datetime.utcnow()
        elapsed_time = current_time - self.start_time
        self.elapsed = str(timedelta(seconds=round(elapsed_time.total_seconds())))

        completed = count
        remaining = self.loop_length - completed

        item_per_second = (completed / elapsed_time.total_seconds())
        try:
            remaining_time = remaining * (1 / item_per_second)
        except ZeroDivisionError:
            remaining_time = 0
        remaining = str(timedelta(seconds=round(remaining_time)))
        
        logger.debug(GREEN + f"Completed [ {count} ] of [ {self.loop_length} ]." + RESET + f" Time elapsed: [ {self.elapsed} ]. Remaining time: [ {remaining} ]. 429 errors: [ {errors.rate_error.count} ].\n")

    def print_status_update_one_line(self, count):
        current_time = datetime.utcnow()
        elapsed_time = current_time - self.start_time
        self.elapsed = str(timedelta(seconds=round(elapsed_time.total_seconds())))

        completed = count
        remaining = self.loop_length - completed

        item_per_second = (completed / elapsed_time.total_seconds())
        try:
            remaining_time = remaining * (1 / item_per_second)
        except ZeroDivisionError:
            remaining_time = 0
        remaining = str(timedelta(seconds=round(remaining_time)))
        
        logger.debug(GREEN + f"Completed [ {count} ] of [ {self.loop_length} ]." + RESET + f" Time elapsed: [ {self.elapsed} ]. Remaining time: [ {remaining} ]\n")

    def get_elapsed_time(self):
        return self.elapsed


class SpotifyToken(object):

    def __init__(self):
        if not session.get('app_token'):
            session['app_token'] = sp.client_authorize()
            session['app_token_expire_time'] = datetime.now() + timedelta(minutes=59)

    def refresh_token(self):
        if session['app_token_expire_time'] < datetime.now():
            session['app_token'] = sp.client_authorize()
            session['app_token_expire_time'] = datetime.now() + timedelta(minutes=59)


class Errors(object):

    class Error:
        def __init__(self, error_type):
            self.type = error_type
            self.found = False
            self.count = 0

    def __init__(self):
        self.rate_error = self.Error("rate_limit")
        self.misc_error = self.Error("misc_error")

    def register_rate_error(self):
        self.rate_error.found = True
        self.rate_error.count += 1

    def register_misc_error(self):
        self.misc_error.found = True
        self.misc_error.count += 1
