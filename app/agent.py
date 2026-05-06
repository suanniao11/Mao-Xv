"""LangChain ReAct agent for the AI Travel Assistant."""

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_openai import AzureChatOpenAI, ChatOpenAI

from app.config import settings
from app.tools.map_tool import DirectionsTool, MapTool
from app.tools.weather_tool import WeatherForecastTool, WeatherTool

# ---------------------------------------------------------------------------
# System prompt / ReAct template
# ---------------------------------------------------------------------------

TRAVEL_AGENT_PROMPT = PromptTemplate.from_template(
    """You are a knowledgeable and friendly AI Travel Assistant.
Your goal is to help users plan trips, explore destinations, understand local weather,
and navigate between places.

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""
)


# ---------------------------------------------------------------------------
# LLM factory
# ---------------------------------------------------------------------------

def _build_llm():
    provider = settings.llm_provider.lower()

    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required when LLM_PROVIDER=openai. "
                "Set it in your .env file."
            )
        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0,
        )

    if provider == "azure":
        if not settings.azure_openai_api_key or not settings.azure_openai_endpoint:
            raise ValueError(
                "AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT are required "
                "when LLM_PROVIDER=azure. Set them in your .env file."
            )
        return AzureChatOpenAI(
            azure_deployment=settings.azure_openai_deployment,
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            temperature=0,
        )

    if provider == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic. "
                "Set it in your .env file."
            )
        return ChatAnthropic(
            model=settings.anthropic_model,
            api_key=settings.anthropic_api_key,
            temperature=0,
        )

    raise ValueError(
        f"Unsupported LLM_PROVIDER '{provider}'. "
        "Choose one of: openai, azure, anthropic."
    )


# ---------------------------------------------------------------------------
# Agent factory
# ---------------------------------------------------------------------------

def build_agent_executor() -> AgentExecutor:
    """Build and return a LangChain ReAct AgentExecutor for travel assistance."""
    tools = [
        MapTool(),
        DirectionsTool(),
        WeatherTool(),
        WeatherForecastTool(),
    ]

    llm = _build_llm()
    agent = create_react_agent(llm=llm, tools=tools, prompt=TRAVEL_AGENT_PROMPT)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=settings.agent_verbose,
        max_iterations=settings.agent_max_iterations,
        handle_parsing_errors=True,
    )
