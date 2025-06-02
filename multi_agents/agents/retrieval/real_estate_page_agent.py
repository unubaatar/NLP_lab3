import logging
from typing import AsyncGenerator, Sequence
from typing_extensions import override
import copy
import json

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.genai.types import Content, Part
from google.genai import types
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

import requests
import urllib.request
from bs4 import BeautifulSoup

def findFeature(li_list, header):
  ret = 'NA'
  for li in li_list:
    text = li.text.strip()
    if text.startswith(header):
      return text[len(header) + 1:]
  return ret

class RealEstatePageRetriever(BaseAgent):
    model_config = {"arbitrary_types_allowed": True}

    def __init__(self, name: str):
        super().__init__(name=name)

    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        url_text = ctx.session.events[0].content.parts[0].text
        for event in ctx.session.events:
            print("Event ", event)
            if hasattr(event.content.parts[0], "text"):
                print("event text: ", )
        print("event text: ", ctx.session.events[0])
        url = url_text

        response = requests.get(url)
        if response.status_code != 200:
            print(response.status_code)
            print('error ',url)
        else:
            soup = BeautifulSoup(response.text,"html.parser")
            title = soup.find("h1", {"class": "title-announcement"}).text.strip()
            price = soup.find("div", {"class": "announcement-price__cost"}).text.replace('үнэ тохирно','').strip()
            li_class = soup.find_all("li")
            location = soup.find("span", {"itemprop": "address"}).text.strip()
            space = findFeature(li_class,'Талбай:')
            print("title ", title)
            print("price", price)
            print("location",location)
            print("space", space)

        yield Event(
            invocation_id=ctx.invocation_id,
            actions=EventActions(state_delta={"title": title, "price": price, "location": location, "space": space}),
            content=types.Content(parts=[types.Part(text="URL is loaded and extracted.")]),
            author=self.name,
            branch=ctx.branch
        )