# SecRAG - SEC Filings Analysis with RAG

A powerful multi-agent AI system built with [crewAI](https://crewai.com) that automatically fetches, processes, and analyzes SEC filings using Retrieval Augmented Generation (RAG) technology. SecRAG combines automated data collection, intelligent parsing, and AI-powered analysis to provide comprehensive insights into insider trading activities and corporate filings.

## 🌟 Features

- **Automated SEC Filing Collection**: Fetches recent Form 4 filings from SEC RSS feeds
- **Intelligent Parsing**: Extracts structured data from XML-based SEC filings
- **RAG-Powered Analysis**: Uses FAISS vector stores and local embeddings for intelligent document retrieval
- **Multi-Agent Workflow**: Employs specialized AI agents for different aspects of analysis
- **Comprehensive Reports**: Generates detailed markdown reports with insights and visualizations
- **Local LLM Support**: Compatible with local models (Ollama/Llama3) and cloud APIs (Gemini)

## 🏗️ Architecture

SecRAG uses a flow-based architecture with three main components:

1. **Data Collection**: RSS fetcher and SEC filing parser
2. **RAG Builder**: Creates searchable knowledge base from filings
3. **Analysis Crew**: Multi-agent system for comprehensive analysis

### Agent Roles

- **Financial Researcher**: Deep analysis of SEC filings with automated tools
- **Report Analyst**: Summarizes findings and highlights key insights
- **Data Ingestor**: Processes filings into RAG-compatible format

## 🛠️ Installation

### Prerequisites

- Python >=3.10 <3.14
- [UV](https://docs.astral.sh/uv/) for dependency management

### Setup

1. Install UV if you haven't already:
```bash
pip install uv
```

2. Navigate to your project directory and install dependencies:
```bash
crewai install
```

3. Set up environment variables in `.env`:
```env
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### Local LLM Setup (Optional)

For local processing with Ollama:

1. Install [Ollama](https://ollama.ai/)
2. Download the Llama3 model:
```bash
ollama pull llama3
```

## 📊 Dependencies

- **crewAI**: Multi-agent orchestration framework
- **FAISS**: Vector similarity search for RAG
- **LangChain**: Document processing and retrieval chains
- **Sentence Transformers**: Local embeddings generation
- **HuggingFace**: Pre-trained models for embeddings
- **FeedParser**: RSS feed processing
- **BeautifulSoup**: HTML parsing for SEC links

## 🚀 Usage

### Basic Execution

Run the complete SecRAG pipeline:

```bash
crewai run
```

This will:
1. Fetch recent SEC Form 4 filings from RSS feeds
2. Parse and structure the filing data
3. Build a FAISS vector store for RAG
4. Generate comprehensive analysis reports

### Individual Components

You can also run specific components:

```python
from secrag.rss import RSSFetcher
from secrag.parse_sec_filings import SECFilingParser
from secrag.crews.ragbuildercrew.ragbuildercrew import RAGBuilderCrew

# Fetch recent filings
fetcher = RSSFetcher(
    base_url="https://www.sec.gov/cgi-bin/browse-edgar",
    headers={"User-Agent": "YourApp contact@email.com"}
)
feed_entries = fetcher.main()

# Parse filings
parser = SECFilingParser()
filings = parser.process_filings(feed_entries)

# Build RAG system
rag_crew = RAGBuilderCrew(filings)
rag_crew.kickoff()
```

### Testing RAG Queries

Test the built knowledge base:

```python
from secrag.main import test_rag_query

# Query the knowledge base
test_rag_query("What transactions were reported by Scott Farquhar?")
```

## 📁 Project Structure

```
secrag/
├── src/secrag/
│   ├── main.py                    # Main flow orchestration
│   ├── rss.py                     # RSS feed fetcher
│   ├── parse_sec_filings.py       # SEC filing parser
│   ├── crews/
│   │   ├── poem_crew/             # Financial analysis crew
│   │   │   ├── FinancialFilingsCrew.py
│   │   │   └── config/
│   │   │       ├── agents.yaml    # Agent configurations
│   │   │       └── tasks.yaml     # Task definitions
│   │   └── ragbuildercrew/        # RAG building crew
│   │       ├── ragbuildercrew.py
│   │       └── config/
│   └── tools/
│       └── RAGTool.py             # Custom RAG building tool
├── sec_filings_report.md          # Generated analysis report
├── summary.md                     # Generated summary
└── faiss_vector_store/            # Generated RAG knowledge base
```

## 📝 Configuration

### Agent Configuration (`config/agents.yaml`)

Customize agent roles, goals, and backstories:

```yaml
financial_researcher:
  role: 'Senior Financial Researcher'
  goal: 'Analyze SEC filings to provide deep, elucidative insights'
  backstory: 'Expert financial researcher with automated tools expertise'

report_analyst:
  role: 'Financial Report Analyst' 
  goal: 'Review analysis and highlight critical key points'
  backstory: 'Meticulous analyst known for distilling complex data'
```

### Task Configuration (`config/tasks.yaml`)

Define specific tasks and expected outputs:

```yaml
analyze_filings_task:
  description: 'Perform deep analysis of each filing'
  expected_output: 'Comprehensive markdown document with detailed analysis'

summarize_filings_task:
  description: 'Review analysis and append overall summarization'
  expected_output: 'Concise professional markdown report'
```

## 🔧 Customization

### Adding New Analysis Types

1. Create new agent configurations in `config/agents.yaml`
2. Define corresponding tasks in `config/tasks.yaml`
3. Implement custom tools in `tools/` directory
4. Update the main flow in `main.py`

### Custom Data Sources

Extend the RSS fetcher or add new data sources:

```python
class CustomDataFetcher:
    def fetch_data(self):
        # Your custom data fetching logic
        pass
```

### Enhanced Analysis

Add custom analysis tools or integrate with external APIs:

```python
from crewai.tools import BaseTool

class CustomAnalysisTool(BaseTool):
    name: str = "Custom Analysis Tool"
    description: str = "Performs specialized financial analysis"
    
    def _run(self, data) -> str:
        # Your analysis logic
        return "Analysis results"
```

## 📈 Output Examples

SecRAG generates comprehensive reports including:

- **Executive Summaries**: High-level findings and implications
- **Transaction Analysis**: Detailed breakdown of insider transactions
- **Footnote Analysis**: Important context from SEC filing footnotes
- **Compliance Assessment**: Rule 10b5-1 plans and regulatory compliance
- **Key Takeaways**: Bulleted insights for quick reference

## 🔍 Advanced Features

### RAG Integration

- Local embeddings using Sentence Transformers
- FAISS vector store for fast similarity search
- Persistent storage for knowledge base reuse
- Query interface for interactive analysis

### Multi-LLM Support

- **Local**: Ollama with Llama3
- **Cloud**: Google Gemini, OpenAI GPT models
- **Hybrid**: Mix local and cloud models for cost optimization

## 🚨 Important Notes

### SEC Compliance

- Always include proper User-Agent headers when accessing SEC data
- Respect SEC's fair access policy and rate limits
- Use for informational purposes only, not as financial advice

### Data Privacy

- All processing happens locally by default
- Vector stores are saved locally for privacy
- No sensitive data transmitted to external services (when using local LLMs)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, questions, or feedback:

- Visit [crewAI documentation](https://docs.crewai.com)
- Check the [crewAI GitHub repository](https://github.com/joaomdmoura/crewai)
- Join the [crewAI Discord](https://discord.com/invite/X4JWnZnxPb)

## 🚀 Getting Started

1. Clone this repository
2. Install dependencies with `crewai install`
3. Set up your `.env` file with API keys
4. Run `crewai run` to start the analysis pipeline
5. Check the generated reports in `sec_filings_report.md` and `summary.md`

---

**Disclaimer**: This tool is for informational purposes only and does not constitute financial advice. Always consult with qualified professionals for investment decision
