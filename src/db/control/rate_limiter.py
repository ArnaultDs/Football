from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update, func
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime, timezone, timedelta

from db.control.models import RapidApiLimiterInstance
from common.postgres import SessionLocal


class QuotaExhausted(Exception): 
    ...


class RateLimiter: 
    API_RATE_LIMIT = 100

    def __init__(self, api_name: str, session: sessionmaker | None = None) -> None: 

        self._api_name = api_name
        self._Session = session or SessionLocal

    def _window_session_start(self) -> datetime: 
        """
        Function to return the current window session start 
        Retrieve the information from the db and check that
        the window needs to be reseted

        return: 
            the datetime of the current window session
        """

        stmt = (
            select(
                RapidApiLimiterInstance.window_start, 
                RapidApiLimiterInstance.window_reset_at)
            .where(RapidApiLimiterInstance.api_name == self._api_name)
            .order_by(RapidApiLimiterInstance.window_start.desc())
            .limit(1)
        )
        
        with self._Session.begin() as session: 
            result = session.execute(stmt).first()

        now = datetime.now(timezone.utc)

        if result is None or now >= result.window_reset_at: 
            return now 

        return result.window_start

    def _ensure_window_is_created(self, window_start: datetime) -> None: 
        """
        Method to verify that the window is created in db 
        If not than create it 

        Args: 
            window_start: datetime -> the cureent window start
        """

        stmt = (
            insert(RapidApiLimiterInstance)
            .values(
                api_name = self._api_name,
                window_start = window_start,
                window_reset_at = window_start + timedelta(days=1),
                limit_total = self.API_RATE_LIMIT, 
                reserved_count=0,
                confirmed_count=0,
            )
            .on_conflict_do_nothing(index_elements=["api_name", "window_start"])
        )

        with self._Session.begin() as session: 
            result = session.execute(stmt)


    def try_reserve(self) -> bool: 
        """
        Function that reserve a unique counter to target the api. 
        If remaining counts return True else False

        Return: 
            A boolean defining the status to target the api

        """

        window_start = self._window_session_start()
        self._ensure_window_is_created(window_start)

        stmt = (
            update(RapidApiLimiterInstance)
            .where(
                RapidApiLimiterInstance.api_name == self._api_name, 
                RapidApiLimiterInstance.window_start == window_start,
                RapidApiLimiterInstance.reserved_count < RapidApiLimiterInstance.limit_total
            )
            .values(reserved_count = RapidApiLimiterInstance.reserved_count + 1)
            .returning(RapidApiLimiterInstance.reserved_count)
        )

        with self._Session.begin() as session: 
            result = session.execute(stmt)

        return result.first() is not None

    def release(self) -> None: 
        ...

    def confirm(self, remaining: int, reset_seconds: int) -> None: 
        """
        Method that update the db with informations from api headers

        Args: 
            remaining_from_headers: int -> Number of remaining calls to api
            reset_seconds: int -> Number of seconds before new window
        """

        window_start = self._window_session_start()
        self._ensure_window_is_created(window_start)
        now = datetime.now(timezone.utc)

        stmt = (
            update(RapidApiLimiterInstance)
            .where(
                RapidApiLimiterInstance.api_name == self._api_name, 
                RapidApiLimiterInstance.window_start == window_start
            )
            .values(
                confirmed_count = RapidApiLimiterInstance.limit_total - remaining,
                reserved_count = RapidApiLimiterInstance.limit_total - remaining,
                window_reset_at = now + timedelta(seconds=reset_seconds),
                last_confirmed_at = now
            )
        )

        with self._Session.begin() as session: 
            result = session.execute(stmt)