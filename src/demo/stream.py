"""
concurrency

João Baptista <joao.baptista@devoteam.com> 2023-07-09
"""
import asyncio

from demo.concurrent import no_concurrency, concurrency_not_really, real_concurrency
from demo.service import Service
from demo.utils import TRIES, print_duration


@print_duration
def no_stream(service: Service):
    no_concurrency.__wrapped__(service)


@print_duration
async def stream_not_really(service: Service):
    await concurrency_not_really.__wrapped__(service)


@print_duration
async def another_fake_stream(service: Service):
    await real_concurrency.__wrapped__(service)


@print_duration
async def real_stream(service: Service):
    jobs = [asyncio.create_task(service.acall(i)) for i in range(TRIES)]
    while jobs:
        finished, jobs = await asyncio.wait(jobs, return_when=asyncio.FIRST_COMPLETED)
        for task in finished:
            result, duration = await task
            print(f"job {result} took {duration} seconds to finish")


if __name__ == "__main__":
    _service = Service(10, 1000)
    no_stream(_service)
    input()
    asyncio.run(stream_not_really(_service))
    input()
    asyncio.run(another_fake_stream(_service))
    input()
    asyncio.run(real_stream(_service))
