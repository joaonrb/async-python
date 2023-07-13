"""
rick_and_morty

João Baptista <joao.baptista@devoteam.com> 2023-07-12
"""
import asyncio

import aiohttp
import pydantic
import requests

from demo.utils import print_duration


class Object(pydantic.BaseModel):
    id: int


class URL(pydantic.BaseModel):
    url: str


class Character(pydantic.BaseModel):
    id: int
    name: str
    location: URL

    def location_id(self) -> int:
        return int(self.location.url.removeprefix("https://rickandmortyapi.com/api/location/"))


class Location(pydantic.BaseModel):
    id: int
    name: str


class Episode(pydantic.BaseModel):
    id: int
    name: str
    characters: list[str]

    def character_ids(self) -> list[int]:
        return [int(url.removeprefix("https://rickandmortyapi.com/api/character/")) for url in self.characters]


class PageInfo(pydantic.BaseModel):
    count: int
    pages: int
    next: str | None
    prev: str | None


class Page(pydantic.BaseModel):
    info: PageInfo
    results: list[Object]


class RickAndMortyAPI:

    def __init__(self):
        self.host = "https://rickandmortyapi.com"

    def episode_base_url(self) -> str:
        return f"{self.host}/api/episode"

    def episode_url(self, episode_url: int) -> str:
        return f"{self.episode_base_url()}/{episode_url}"

    def character_url(self, character_id: int) -> str:
        return f"{self.host}/api/character/{character_id}"

    def location_url(self, location_id):
        return f"{self.host}/api/location/{location_id}"

    def get(self, url: str, model: pydantic.BaseModel) -> pydantic.BaseModel:
        response = requests.get(url)
        return model.model_validate(response.json())

    async def aget(self, url: str, model: pydantic.BaseModel) -> pydantic.BaseModel:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=False) as response:
                return model.model_validate(await response.json())

    def list_episode(self, page: int) -> Page:
        return self.get(f"{self.episode_base_url()}?page={page}", Page)

    async def alist_episode(self, page: int) -> Page:
        return await self.aget(f"{self.episode_base_url()}?page={page}", Page)

    def episode(self, episode_id: int) -> Episode:
        return self.get(self.episode_url(episode_id), Episode)

    async def aepisode(self, episode_id: int) -> Episode:
        return await self.aget(self.episode_url(episode_id), Episode)

    def character(self, character_id: int) -> Character:
        return self.get(self.character_url(character_id), Character)

    async def acharacter(self, character_id: int) -> Character:
        return await self.aget(self.character_url(character_id), Character)

    def location(self, location_id: int) -> Location:
        return self.get(self.location_url(location_id), Location)

    async def alocation(self, location_id: int) -> Location:
        return await self.aget(self.location_url(location_id), Location)


api = RickAndMortyAPI()


def get_episode(ep: int) -> dict:
    episode = api.episode(ep)
    result = {
        "id": ep,
        "name": episode.name,
        "last_location": []
    }
    for character_id in episode.character_ids():
        character = api.character(character_id)
        if character.location.url:
            location = api.location(character.location_id())
            result["last_location"].append({"name": character.name, "location": location.name})
        else:
            result["last_location"].append({"name": character.name, "location": "unknown"})
    return result


async def aget_episode(ep: int, max_: int | float) -> dict:
    episode = await api.aepisode(ep)
    result = {
        "id": ep,
        "name": episode.name,
        "last_location": []
    }
    jobs = set()
    waiting = []
    for character_id in episode.character_ids():
        jobs.add(asyncio.create_task(aget_location(character_id)))
        if len(jobs) >= max_:
            done, jobs = await asyncio.wait(jobs, return_when=asyncio.FIRST_COMPLETED)
            waiting += done
    if jobs:
        done, _ = await asyncio.wait(jobs, return_when=asyncio.FIRST_COMPLETED)
        waiting += done
    result["last_location"] = [await r for r in waiting]
    return result


async def aget_location(character_id: int) -> dict:
    character = await api.acharacter(character_id)
    if character.location.url:
        location = await api.alocation(character.location_id())
        return {"name": character.name, "location": location.name}
    return {"name": character.name, "location": "unknown"}


@print_duration
def load_locations():
    page_number = 1
    page = api.list_episode(page_number)
    result = []
    while True:
        for ep in page.results:
            result.append(get_episode(ep.id))
        page_number += 1
        if page_number > page.info.pages:
            return result
        page = api.list_episode(page_number)


@print_duration
async def aload_locations():
    page_number = 1
    page = await api.alist_episode(page_number)
    result = []
    while True:
        for ep in page.results:
            result.append(aget_episode(ep.id, float("+inf")))
        page_number += 1
        if page_number > page.info.pages:
            return [r for r in await asyncio.gather(*result)]
        page = api.list_episode(page_number)


@print_duration
async def aload_locations2(max_: int):
    page_number = 1
    page = await api.alist_episode(page_number)
    working = set()
    result = []
    while True:
        for ep in page.results:
            working.add(asyncio.create_task(aget_episode(ep.id, max_)))
            if len(working) >= max_:
                done, working = await asyncio.wait(working, return_when=asyncio.FIRST_COMPLETED)
                result += done
        page_number += 1
        if page_number > page.info.pages:
            if working:
                done, _ = await asyncio.wait(working)
                result += done
            return list(sorted([await r for r in result], key=lambda e: e["id"]))
        page = api.list_episode(page_number)


if __name__ == "__main__":
    # load_locations()
    # asyncio.run(aload_locations())
    asyncio.run(aload_locations2(1))
    asyncio.run(aload_locations2(2))
    asyncio.run(aload_locations2(5))
    asyncio.run(aload_locations2(10))
    asyncio.run(aload_locations2(15))
    asyncio.run(aload_locations2(25))
    asyncio.run(aload_locations2(50))

