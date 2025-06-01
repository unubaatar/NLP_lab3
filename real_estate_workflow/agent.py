# Full runnable code for the RealEstateAgent
import logging
from typing import AsyncGenerator, Sequence
from typing_extensions import override
import copy
import json
import os
import re
import urllib.parse

from google.adk.agents import LlmAgent, BaseAgent, LoopAgent, SequentialAgent, ParallelAgent
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types
from google.genai.types import Content, HttpOptions, Part
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.events import Event, EventActions
from pydantic import BaseModel, Field
from google import genai


from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.documents import Document
from langchain_together import ChatTogether

from multi_agents.agents.retrieval.real_estate_page_agent import RealEstatePageRetriever
from multi_agents.agents.research.district_analysis import DistrictAnalysisAgent

# --- Model ---
LLM_Model = "gemini-1.5-pro"

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm = ChatTogether(
    together_api_key="abeb6dac65702ac49f10790d3182b32707afa1d9fe64eea4bb88fffdc7051049",
    model="meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
)

search_tool = TavilySearchResults(max_results=5, search_depth="advanced", include_answer=True)

page_retriever = RealEstatePageRetriever(name="real_esate_page_retriever")
district_analysis = DistrictAnalysisAgent(name="district_analysis", llm_model=llm)



#Extractor Workflow
parallel_retrieval_agent = ParallelAgent(
    name="ParallelRetrievalSubworkflow",
    sub_agents=[page_retriever]
)

#Analysis Workflow
parallel_analysis_agent = ParallelAgent(
    name="ParallelAnalysisSubWorkflow",
    sub_agents=[district_analysis]
)

#Writer agent
root_agent = SequentialAgent(
    name="real_estate_workflow",
    sub_agents=[parallel_retrieval_agent, parallel_analysis_agent]
)

