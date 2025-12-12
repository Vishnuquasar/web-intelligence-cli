# Web Intelligence Gatherer - Automatic Web Search Tool
# Goal : Like Mr. Robot's Elliot searching for intelligence, but ethical & practical
# This tool automates multi-source web searches for OSINT and research

## Project Overview

**Web Intelligence Gatherer** is a Python-based CLI tool that:
- Automatically searches across **multiple sources** (Wikipedia, Stack Overflow, GitHub, Google News, Hacker News)
- Aggregates and deduplicates results
- Exports findings to **JSON & CSV reports**
- Provides **statistics and analysis**
- Uses **multi-threading for fast searches**
- Ethical & responsible design (respects robots.txt, rate limiting)

Perfect for:
- **OSINT (Open Source Intelligence) research**
- **Security research and threat intelligence**
- **Technology news aggregation**
- **Portfolio project for cybersecurity roles**

---

## Quick Start

### [1] Installation

```bash
# Clone the repository
git clone https://github.com/Vishnuquasar/web-intelligence-cli.git
cd web-intelligence-cli

# Install dependencies
pip install -r requirements.txt
```

### [2] Basic Usage

```bash
# Simple search
python main.py --keyword "cybersecurity vulnerability"

# Search specific sources only
python main.py --keyword "python security" --sources wikipedia github stackoverflow

# Limit results and set output
python main.py --keyword "data breach" --max-results 10 --output report.json --format json

# Get help
python main.py --help
```

### [3] Example Commands

```bash
# Search for security tools
python main.py --keyword "ethical hacking tools" --max-results 20

# Search and export to CSV
python main.py --keyword "python projects" --format csv --output results.csv

# Search all sources, get 5 results per source
python main.py --keyword "cybersecurity" --max-results 5 --sources all
```

---

## Features

### Multi-Source Search
- **Wikipedia** - Encyclopedic information
- **Stack Overflow** - Programming Q&A
- **GitHub** - Open-source projects & discussions
- **Google News** - Latest news articles
- **Hacker News** - Tech & security news

### Data Processing
- Deduplication of results across sources
- Relevance ranking
- XSS/injection prevention in output
- Data cleaning and normalization

### Reporting
- **JSON export** - Complete structured data
- **CSV export** - Spreadsheet-friendly format
- **Console output** - Colorized results with statistics
- **Search statistics** - Time, count, source breakdown

### Performance
- Multi-threaded searches (parallel source querying)
- Configurable timeout and retry logic
- Rate limiting to be respectful to target sites
- Progress indicators for long searches

---

## Example Output

### JSON Report
```json
{
  "search": {
    "keyword": "cybersecurity python",
    "timestamp": "2025-12-11T21:30:45.123Z",
    "sources": ["wikipedia", "github", "stackoverflow"],
    "total_results": 15,
    "search_time_seconds": 3.45
  },
  "results": [
    {
      "source": "github",
      "title": "awesome-security",
      "description": "Curated list of awesome security resources",
      "url": "https://github.com/sbilly/awesome-security",
      "relevance_score": 0.95
    },
    {
      "source": "wikipedia",
      "title": "Cybersecurity",
      "description": "Cybersecurity is the practice of protecting systems...",
      "url": "https://en.wikipedia.org/wiki/Cybersecurity",
      "relevance_score": 0.92
    }
  ]
}
```

### CSV Report
```csv
source,title,description,url,relevance_score,timestamp
github,awesome-security,Curated list of awesome security resources,https://github.com/sbilly/awesome-security,0.95,2025-12-11T21:30:45
wikipedia,Cybersecurity,Cybersecurity is the practice of protecting systems...,https://en.wikipedia.org/wiki/Cybersecurity,0.92,2025-12-11T21:30:45
```

---

## Configuration

Edit `config.py` to customize:
- Request timeout values
- Rate limiting delays
- User-agent strings
- Output directory
- Default sources and max results

```python
# config.py
TIMEOUT = 10                    # Request timeout in seconds
RATE_LIMIT_DELAY = 1.0         # Delay between requests
MAX_RESULTS_DEFAULT = 5        # Default results per source
REQUEST_RETRIES = 2            # Number of retries on failure
DEFAULT_SOURCES = ["wikipedia", "github", "stackoverflow"]
```

---

## Ethical Guidelines

 **DO:**
- Respect `robots.txt` and `User-Agent` headers
- Use reasonable rate limiting
- Provide proper attribution in reports
- Follow each site's Terms of Service
- Use results only for authorized purposes

 **DON'T:**
- Scrape personal or sensitive data
- Bypass rate limiting intentionally
- Ignore terms of service
- Use for malicious purposes
- Sell scraped data

---

## Use Cases

### 1. **OSINT Research**
```bash
python main.py --keyword "breach:company-name" --sources all --max-results 20
```

### 2. **Technology Trend Analysis**
```bash
python main.py --keyword "artificial intelligence 2025" --format json
```

### 3. **Security Threat Intelligence**
```bash
python main.py --keyword "CVE-2025" --sources github hackernews
```

### 4. **Job Research**
```bash
python main.py --keyword "cybersecurity analyst skills" --output skills_report.csv --format csv
```

### Future Features to Implement
- [ ] Add Shodan integration for IP/port info
- [ ] Add Twitter/X search capabilities
- [ ] Add YouTube video search
- [ ] Add blockchain/crypto data sources
- [ ] Advanced filtering and regex support
- [ ] SQLite database storage option
- [ ] Web UI dashboard
- [ ] Scheduled periodic searches
- [ ] Email alert integration
- [ ] API server mode

---

## License

MIT License - Free to use for educational and authorized purposes

---

## Author

Built by a cybersecurity enthusiast from Tamil Nadu, India 🇮🇳

For ethical hacking & cybersecurity job seekers - make this your own, customize it, and showcase on GitHub!

---

## ⚠️ Disclaimer

This tool is for **educational and authorized research only**. Users are responsible for ensuring their use complies with:
- Local laws and regulations
- Terms of service of target websites
- Ethical hacking guidelines
- Data protection regulations (GDPR, CCPA, etc.)

The author assumes no liability for misuse or damage caused by this tool.

---

## 📞 Support & Feedback

Found a bug? Have suggestions? Open an issue on GitHub!

**Keywords for searchability:**
`cybersecurity`, `osint`, `web-scraping`, `automation`, `python`, `ethical-hacking`, `intelligence-gathering`, `security-research`, `automation-tool`
