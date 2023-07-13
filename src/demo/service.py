"""
service

João Baptista <joao.baptista@devoteam.com> 2023-07-09
"""
import random
import time
import asyncio
from typing import Any


class Service:

    def __init__(self, min_millis: int, max_millis: int):
        self.__min = min_millis
        self.__max = max_millis

    def call(self, parameter: Any) -> tuple[Any, float]:
        duration = self.execution_time()
        time.sleep(duration)
        return parameter, duration

    async def acall(self, parameter: Any) -> tuple[Any, float]:
        duration = self.execution_time()
        await asyncio.sleep(duration)
        return parameter, duration

    def execution_time(self):
        return random.randint(self.__min, self.__max) / 1000
