"""
parallelism

João Baptista <joao.baptista@devoteam.com> 2023-07-09
"""
import asyncio

from demo.service import Service
from demo.utils import TRIES, print_duration


@print_duration
def no_concurrency(service: Service):
    for i in range(TRIES):
        result, duration = service.call(i)
        print(f"job {result} took {duration} seconds to finish")


@print_duration
async def concurrency_not_really(service: Service):
    for i in range(TRIES):
        result, duration = await service.acall(i)
        print(f"job {result} took {duration} seconds to finish")


@print_duration
async def real_concurrency(service: Service):
    jobs = [service.acall(i) for i in range(TRIES)]
    for result, duration in await asyncio.gather(*jobs):
        print(f"job {result} took {duration} seconds to finish")


@print_duration
async def another_real_concurrency(service: Service):
    jobs = [asyncio.create_task(service.acall(i)) for i in range(TRIES)]
    for job in jobs:
        result, duration = await job
        print(f"job {result} took {duration} seconds to finish")


if __name__ == "__main__":
    _service = Service(100, 100)
    no_concurrency(_service)
    input()
    asyncio.run(concurrency_not_really(_service))
    input()
    asyncio.run(real_concurrency(_service))
    input()
    asyncio.run(another_real_concurrency(_service))
