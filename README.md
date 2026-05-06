# AI Travel Agent 🌍✈️

A FastAPI service that exposes a conversational AI travel assistant powered by
the **LangChain ReAct** framework. The agent can answer natural-language travel
questions by automatically calling **Map** and **Weather** tools.

---

## Features

| Capability | Detail |
|---|---|
| LLM Providers | OpenAI, Azure OpenAI, Anthropic Claude |
| Map Tool | Place search and turn-by-turn directions (Google Maps API) |
| Weather Tool | Current conditions and 5-day forecast (OpenWeatherMap API) |
| API Framework | FastAPI with auto-generated OpenAPI docs |
| Deployment | Multi-stage Docker build, runs as non-root user |

---

## Project structure

```
.
├── app/
│   ├── main.py             # FastAPI app and middleware
│   ├── agent.py            # LangChain ReAct agent factory
│   ├── config.py           # Pydantic settings (reads .env)
│   ├── routers/
│   │   └── travel.py       # POST /travel/query endpoint
│   └── tools/
│       ├── map_tool.py     # MapTool and DirectionsTool
│       └── weather_tool.py # WeatherTool and WeatherForecastTool
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## Quick start

### 1. Clone and configure

```bash
git clone https://github.com/suanniao11/Mao-Xv.git
cd Mao-Xv
cp .env.example .env
```

Open `.env` and fill in at least one LLM provider key and (optionally) the
external API keys.

### 2. Run locally

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is now available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`.

### 3. Run with Docker

```bash
docker build -t ai-travel-agent .
docker run --env-file .env -p 8000:8000 ai-travel-agent
```

---

## Configuring the LLM provider

Set `LLM_PROVIDER` in your `.env` file to one of the supported values and
supply the corresponding credentials.

### OpenAI (default)

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o        # optional, defaults to gpt-4o
```

Get an API key at <https://platform.openai.com/api-keys>.

### Azure OpenAI

```env
LLM_PROVIDER=azure
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-01   # optional
```

Create a resource in the [Azure Portal](https://portal.azure.com/) under
*Azure OpenAI Service* and deploy a model.

### Anthropic Claude

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022   # optional
```

Get an API key at <https://console.anthropic.com/>.

---

## Configuring external tools

### Map API (Google Maps Platform)

```env
MAP_API_KEY=<your-google-maps-api-key>
MAP_API_BASE_URL=https://maps.googleapis.com/maps/api   # default
```

1. Go to <https://console.cloud.google.com/> and create or select a project.
2. Enable the **Places API** and the **Directions API**.
3. Create an API key and restrict it to those two APIs.

> **Tip:** If no key is set the tool returns a descriptive error message so the
> rest of the agent still works.

### Weather API (OpenWeatherMap)

```env
WEATHER_API_KEY=<your-openweathermap-api-key>
WEATHER_API_BASE_URL=https://api.openweathermap.org/data/2.5   # default
```

1. Register a free account at <https://home.openweathermap.org/>.
2. Copy the **Default** API key from the *API keys* tab.

---

## Example API call

```bash
curl -X POST http://localhost:8000/travel/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the weather in Paris and how do I get there from London?"}'
```

Response:

```json
{
  "answer": "Current weather in Paris, FR: Clear sky, 22°C ... Eurostar from London St Pancras takes about 2h20m ..."
}
```

---

## Agent tuning

| Variable | Default | Description |
|---|---|---|
| `AGENT_MAX_ITERATIONS` | `10` | Maximum ReAct reasoning steps |
| `AGENT_VERBOSE` | `true` | Print reasoning trace to stdout |

---

## About

Hi there, I'm Xv (Amanda) Mao 👋 — this project is part of my exploration of
LLM-powered agents and FastAPI.

---

## License

MIT
