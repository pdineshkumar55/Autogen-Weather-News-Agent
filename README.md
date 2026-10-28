# AutoGen Weather News Agent

An AutoGen agent with a tool. It asks the user for a city, searches the web with the free, keyless DuckDuckGo search package (`ddgs`), and replies in exactly 3 short lines.

In AutoGen a tool is just a Python function. The agent reads the function's **name, type hints and docstring** to decide when and how to call it.

## Features

- An `AssistantAgent` with a web search tool passed in `tools=[...]`
- `reflect_on_tool_use=True`, so the agent writes an answer from the search results instead of dumping raw output
- Searches both **news** and **web** results with `ddgs` (no API key needed)
- Asks for the city with `input()`
- Replies in exactly 3 lines: current conditions, latest news or alert, short-term outlook
- Search errors (such as rate limits) come back as text, so the script doesn't crash
- The model client is closed in a `finally` block
- The OpenAI API key is read from a `.env` file and never hard-coded

## Tech Stack

- Python 3.10+
- [AutoGen](https://github.com/microsoft/autogen) (`autogen-agentchat`, `autogen-ext[openai]`)
- [`ddgs`](https://pypi.org/project/ddgs/): DuckDuckGo search
- `python-dotenv`
- OpenAI `gpt-4o-mini`

## Project Structure

```
Autogen-Weather-News-Agent/
├── .venv/              # virtual environment (not committed)
├── .env                # API key (not committed)
├── .gitignore
├── requirements.txt
├── weather_news.py     # agent + search tool
└── README.md
```

## Setup

1. **Open the project folder in VS Code.**

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   ```

   - Windows (PowerShell): `.venv\Scripts\Activate.ps1`
   - macOS/Linux: `source .venv/bin/activate`

   Select the interpreter: `Ctrl+Shift+P` → **Python: Select Interpreter** → `.venv`

3. **Install the dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   `requirements.txt`:

   ```
   autogen-agentchat
   autogen-ext[openai]
   ddgs
   python-dotenv
   ```

4. **Add your API key** to a `.env` file in the project folder:

   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

5. **Keep secrets out of Git** with this `.gitignore`:

   ```
   .env
   .venv/
   __pycache__/
   ```

## Run

```bash
python weather_news.py
```

Enter a city when asked, for example `Coimbatore`.

## Sample Output

```
Enter a city name: Coimbatore
---------- TextMessage (user) ----------
Give me the latest weather news for Coimbatore.
---------- ToolCallRequestEvent (weather_news_agent) ----------
[FunctionCall(... name='search_weather_news', arguments='{"city":"Coimbatore"}')]
---------- ToolCallExecutionEvent (weather_news_agent) ----------
[FunctionExecutionResult(content='- [NEWS ...] ... - [WEB] ...')]
---------- TextMessage (weather_news_agent) ----------
<current conditions>
<latest weather news or alert>
<short-term outlook>
```

## How It Works

1. `load_dotenv()` loads `OPENAI_API_KEY` from `.env`.
2. The user enters a city with `input()`.
3. `search_weather_news(city)` is the tool:
   - `DDGS().news()` fetches recent weather headlines
   - `DDGS().text()` fetches current-weather snippets
   - The results are combined into one text block with titles, snippets and links
4. The `AssistantAgent` gets the tool through `tools=[search_weather_news]`. AutoGen builds the tool schema from the function's type hints and docstring.
5. The model decides to call the tool. Then, because of `reflect_on_tool_use=True`, it makes a second model call that turns the raw results into a 3-line answer.
6. `Console` streams every step: the user message, the tool call request, the tool result, and the final answer.
7. `model_client.close()` runs in `finally` so the script exits cleanly.

## Key Concepts

| Concept | Purpose |
|---|---|
| `tools=[...]` | Gives the agent Python functions it can call |
| Type hints + docstring | Tell the model what the tool does and what arguments it takes |
| `reflect_on_tool_use=True` | The agent summarizes tool output instead of returning it raw |
| `system_message` | Sets the 3-line format and tells the agent to use real facts from the results |

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Activate the venv and select it as the interpreter in VS Code |
| `OPENAI_API_KEY not found` | Check that the file is named exactly `.env` (not `.env.txt`) and is in the project folder |
| `Search failed: ... Ratelimit` | DuckDuckGo throttled the request. Wait a minute and retry |
| Vague answer ("check AccuWeather…") | The search returned site descriptions with no data. Try again, or use a more specific city name |
| PowerShell blocks `Activate.ps1` | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once |

## Possible Improvements

- Add a real weather API (for example Open-Meteo, also free and keyless) as a second tool for exact temperatures
- Loop so the user can ask about several cities in one run
- Add a second agent to fact-check the summary