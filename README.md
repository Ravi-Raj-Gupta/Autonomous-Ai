# AutonomousAgent

✅ **Project**: AutonomousAgent — a modular framework for building autonomous AI agents that can plan, research, execute, and review tasks collaboratively.

---

## 🔍 Project Description
AutonomousAgent is a small, opinionated micro-framework that coordinates multiple specialized agents (Planner, Researcher, Executor, Reviewer) to perform complex tasks end-to-end. It provides tools for managing tasks, memory, tooling integrations (code, file, web), and orchestrating agents into a crew that works together to solve user-defined objectives.

## 🧭 Key Features
- Modular agent types: Planner, Researcher, Executor, Reviewer
- Task orchestration and lifecycle management
- Pluggable tools for code, file, and web interactions
- Simple templated UI for review/output (Flask templates)
- Support for persistent outputs/memory

# **Tech Stack **

## **Core Framework & AI**
| Technology | Version | Purpose | Why We Chose It |
|------------|---------|---------|----------------|
| **CrewAI** | 0.1.32 | Multi-agent orchestration framework | Modern, specialized for agent collaboration, better than LangChain for multi-agent systems |
| **OpenAI API** | 0.28.1 | LLM backend (GPT-3.5/4) | Most reliable, best performance, easy integration |
| **Python** | 3.9+ | Primary programming language | Rich AI/ML ecosystem, easy to use |

## **Backend & Web Server**
| Technology | Version | Purpose | Why We Chose It |
|------------|---------|---------|----------------|
| **Flask** | 2.3.3 | Web framework | Lightweight, easy for hackathon, simple REST API |
| **Gunicorn** | (Production) | WSGI HTTP Server | Production deployment |
| **Python-dotenv** | 1.0.0 | Environment management | Secure API key management |

## **Tools & Utilities**
| Technology | Version | Purpose | Why We Chose It |
|------------|---------|---------|----------------|
| **DuckDuckGo Search** | 4.1.1 | Free web search | No API key needed, perfect for hackathon |
| **Requests** | 2.31.0 | HTTP client | Simple API calls |
| **BeautifulSoup4** | 4.12.2 | Web scraping | Extract content from websites |
| **Pandas** | 1.5.3 | Data analysis | CSV processing, data manipulation |
| **Python-pptx** | 0.6.23 | PowerPoint creation | Generate presentations |
| **Pydantic** | 1.10.12 | Data validation | Type checking for tool inputs |

## **Frontend**
| Technology | Version | Purpose | Why We Chose It |
|------------|---------|---------|----------------|
| **HTML5** | - | Structure | Standard web markup |
| **CSS3** | - | Styling | Visual presentation |
| **JavaScript** | ES6+ | Interactivity | Dynamic web interface |
| **Tailwind CSS** | CDN | CSS framework | Rapid UI development, responsive design |

## 📁 Repository Structure
```
AutonomousAgent/
├─ app.py                # Flask app entrypoint
├─ config.py             # Configuration and constants
├─ crew_orchestrator.py  # High level orchestration logic
├─ agents/               # Agent implementations
│  ├─ planner_agent.py
│  ├─ researcher_agent.py
│  ├─ executor_agent.py
│  └─ reviewer_agent.py
├─ tools/                # Tooling utilities
├─ tasks/                # Task definitions
├─ memory/               # Persistence helpers
├─ templates/            # Flask templates (UI)
└─ outputs/              # Generated outputs / artifacts
```

## 🚀 Quickstart
1. Create and activate a virtual environment (recommended):
   - python -m venv .venv
   - .\.venv\Scripts\Activate.ps1 (Windows PowerShell)
2. Install dependencies:
   - pip install -r requirements.txt
3. Run the app locally:
   - python app.py
4. Open the UI (if enabled) at: http://127.0.0.1:5000

> Tip: Use Python 3.10+ for best compatibility.

## ⚙️ Configuration
- Check `config.py` for configurable settings such as API keys, timeouts, and behavior toggles.
- Keep secrets out of source control — use environment variables or a .env file.



## **requirements.txt**
```txt
crewai==0.1.32
openai==0.28.1
flask==2.3.3
python-dotenv==1.0.0
requests==2.31.0
beautifulsoup4==4.12.2
duckduckgo-search==4.1.1
pandas==1.5.3
python-pptx==0.6.23
pydantic==1.10.12
```