#!/usr/bin/env python3
"""
Web Intelligence Gatherer - Main Entry Point
Automated multi-source web search tool for OSINT and research
Usage: python main.py --keyword "search term" --sources wikipedia github
"""

import argparse
import json
import csv
import sys
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote

import config
from config import Colors

# ============================================================================
# SEARCHER CLASSES - Each source has its own searcher
# ============================================================================

class BaseSearcher:
    """Base class for all search sources"""
    
    def __init__(self, keyword: str, max_results: int = 5):
        self.keyword = keyword
        self.max_results = min(max_results, config.MAX_RESULTS_LIMIT)
        self.results = []
        self.source_name = "base"
    
    def search(self) -> List[Dict[str, Any]]:
        """Override in subclasses"""
        raise NotImplementedError
    
    def _safe_request(self, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling"""
        headers = kwargs.get('headers', {})
        headers['User-Agent'] = config.USER_AGENT
        kwargs['headers'] = headers
        
        for attempt in range(config.REQUEST_RETRIES):
            try:
                response = requests.get(url, timeout=config.TIMEOUT, **kwargs)
                response.raise_for_status()
                return response
            except Exception as e:
                if attempt == config.REQUEST_RETRIES - 1:
                    raise
                time.sleep(1)
        return None


class WikipediaSearcher(BaseSearcher):
    """Search Wikipedia for keyword"""
    
    def __init__(self, keyword: str, max_results: int = 5):
        super().__init__(keyword, max_results)
        self.source_name = "wikipedia"
    
    def search(self) -> List[Dict[str, Any]]:
        try:
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': self.keyword,
                'srlimit': self.max_results
            }
            response = self._safe_request(config.WIKIPEDIA_API, params=params)
            data = response.json()
            
            for item in data.get('query', {}).get('search', []):
                self.results.append({
                    'source': self.source_name,
                    'title': item.get('title', ''),
                    'description': item.get('snippet', '').replace('<span class=\'searchmatch\'>', '').replace('</span>', ''),
                    'url': f"https://en.wikipedia.org/wiki/{item.get('title', '').replace(' ', '_')}",
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            print(f"{Colors.YELLOW}[!] Wikipedia search failed: {str(e)}{Colors.ENDC}")
        
        return self.results[:self.max_results]


class GitHubSearcher(BaseSearcher):
    """Search GitHub repositories"""
    
    def __init__(self, keyword: str, max_results: int = 5):
        super().__init__(keyword, max_results)
        self.source_name = "github"
    
    def search(self) -> List[Dict[str, Any]]:
        try:
            params = {
                'q': self.keyword,
                'sort': 'stars',
                'order': 'desc',
                'per_page': self.max_results
            }
            response = self._safe_request(config.GITHUB_API, params=params)
            data = response.json()
            
            for item in data.get('items', []):
                self.results.append({
                    'source': self.source_name,
                    'title': item.get('name', ''),
                    'description': item.get('description', 'No description provided'),
                    'url': item.get('html_url', ''),
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            print(f"{Colors.YELLOW}[!] GitHub search failed: {str(e)}{Colors.ENDC}")
        
        return self.results[:self.max_results]


class StackOverflowSearcher(BaseSearcher):
    """Search Stack Overflow questions"""
    
    def __init__(self, keyword: str, max_results: int = 5):
        super().__init__(keyword, max_results)
        self.source_name = "stackoverflow"
    
    def search(self) -> List[Dict[str, Any]]:
        try:
            params = {
                'intitle': self.keyword,
                'sort': 'relevance',
                'order': 'desc',
                'pagesize': self.max_results,
                'site': 'stackoverflow.com'
            }
            response = self._safe_request(config.STACKOVERFLOW_API, params=params)
            data = response.json()
            
            for item in data.get('items', []):
                self.results.append({
                    'source': self.source_name,
                    'title': item.get('title', '').replace('&quot;', '"').replace('&amp;', '&'),
                    'description': f"Score: {item.get('score', 0)}, Tags: {', '.join(item.get('tags', []))}",
                    'url': item.get('link', ''),
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            print(f"{Colors.YELLOW}[!] Stack Overflow search failed: {str(e)}{Colors.ENDC}")
        
        return self.results[:self.max_results]


class HackerNewsSearcher(BaseSearcher):
    """Search Hacker News"""
    
    def __init__(self, keyword: str, max_results: int = 5):
        super().__init__(keyword, max_results)
        self.source_name = "hackernews"
    
    def search(self) -> List[Dict[str, Any]]:
        try:
            params = {
                'query': self.keyword,
                'hitsPerPage': self.max_results,
                'tags': 'story'
            }
            response = self._safe_request(config.HACKERNEWS_API, params=params)
            data = response.json()
            
            for item in data.get('hits', []):
                self.results.append({
                    'source': self.source_name,
                    'title': item.get('title', ''),
                    'description': f"Points: {item.get('points', 0)}, Comments: {item.get('num_comments', 0)}",
                    'url': item.get('url', '') or f"https://news.ycombinator.com/item?id={item.get('objectID', '')}",
                    'timestamp': datetime.now().isoformat()
                })
        except Exception as e:
            print(f"{Colors.YELLOW}[!] Hacker News search failed: {str(e)}{Colors.ENDC}")
        
        return self.results[:self.max_results]


class GoogleNewsSearcher(BaseSearcher):
    """Search Google News (basic HTML parsing)"""
    
    def __init__(self, keyword: str, max_results: int = 5):
        super().__init__(keyword, max_results)
        self.source_name = "googlenews"
    
    def search(self) -> List[Dict[str, Any]]:
        try:
            url = f"{config.GOOGLE_NEWS_URL}?q={quote(self.keyword)}"
            response = self._safe_request(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all('article', limit=self.max_results)
            
            for article in articles:
                try:
                    title_elem = article.find('h3')
                    link_elem = article.find('a')
                    desc_elem = article.find('p')
                    
                    if title_elem and link_elem:
                        self.results.append({
                            'source': self.source_name,
                            'title': title_elem.get_text(strip=True),
                            'description': desc_elem.get_text(strip=True) if desc_elem else "News article",
                            'url': link_elem.get('href', ''),
                            'timestamp': datetime.now().isoformat()
                        })
                except:
                    continue
        except Exception as e:
            print(f"{Colors.YELLOW}[!] Google News search failed: {str(e)}{Colors.ENDC}")
        
        return self.results[:self.max_results]


# ============================================================================
# REPORT GENERATOR
# ============================================================================

class ReportGenerator:
    """Generate reports in various formats"""
    
    @staticmethod
    def to_json(all_results: List[Dict], keyword: str, search_time: float, sources: List[str]) -> str:
        """Generate JSON report"""
        report = {
            'search': {
                'keyword': keyword,
                'timestamp': datetime.now().isoformat(),
                'sources': sources,
                'total_results': len(all_results),
                'search_time_seconds': round(search_time, 2)
            },
            'results': all_results
        }
        return json.dumps(report, indent=2, ensure_ascii=False)
    
    @staticmethod
    def to_csv(all_results: List[Dict]) -> str:
        """Generate CSV report"""
        if not all_results:
            return "No results found"
        
        output = "source,title,description,url,timestamp\n"
        for result in all_results:
            row = [
                result.get('source', ''),
                f'"{result.get("title", "").replace(chr(34), chr(34)+chr(34))}"',
                f'"{result.get("description", "").replace(chr(34), chr(34)+chr(34))}"',
                result.get('url', ''),
                result.get('timestamp', '')
            ]
            output += ','.join(row) + '\n'
        
        return output


# ============================================================================
# MAIN SEARCH ORCHESTRATOR
# ============================================================================

class WebIntelligenceGatherer:
    """Main orchestrator for web intelligence gathering"""
    
    def __init__(self, keyword: str, sources: List[str], max_results: int):
        self.keyword = keyword
        self.sources = sources
        self.max_results = max_results
        self.all_results = []
        self.search_time = 0
        
        # Validate keyword
        if not keyword or len(keyword) < config.MIN_KEYWORD_LENGTH:
            raise ValueError(f"Keyword must be at least {config.MIN_KEYWORD_LENGTH} characters")
        
        if len(keyword) > config.MAX_KEYWORD_LENGTH:
            raise ValueError(f"Keyword must be less than {config.MAX_KEYWORD_LENGTH} characters")
        
        # Validate sources
        invalid_sources = set(sources) - set(config.AVAILABLE_SOURCES)
        if invalid_sources:
            raise ValueError(f"Invalid sources: {invalid_sources}")
    
    def _get_searcher(self, source: str) -> BaseSearcher:
        """Get appropriate searcher for source"""
        searchers = {
            'wikipedia': WikipediaSearcher,
            'github': GitHubSearcher,
            'stackoverflow': StackOverflowSearcher,
            'hackernews': HackerNewsSearcher,
            'googlenews': GoogleNewsSearcher
        }
        
        searcher_class = searchers.get(source)
        if not searcher_class:
            return None
        
        return searcher_class(self.keyword, self.max_results)
    
    def search(self) -> List[Dict]:
        """Execute multi-source search with threading"""
        start_time = time.time()
        
        print(f"\n{Colors.HEADER}{Colors.BOLD}🔍 Starting Web Intelligence Search{Colors.ENDC}")
        print(f"{Colors.CYAN}Keyword: {Colors.BOLD}{self.keyword}{Colors.ENDC}")
        print(f"{Colors.CYAN}Sources: {Colors.BOLD}{', '.join(self.sources)}{Colors.ENDC}")
        print(f"{Colors.CYAN}Max results per source: {Colors.BOLD}{self.max_results}{Colors.ENDC}\n")
        
        # Execute searches in parallel
        with ThreadPoolExecutor(max_workers=config.MAX_THREADS) as executor:
            futures = {}
            
            for source in self.sources:
                searcher = self._get_searcher(source)
                if searcher:
                    future = executor.submit(searcher.search)
                    futures[future] = source
            
            # Collect results as they complete
            for future in as_completed(futures):
                source = futures[future]
                try:
                    results = future.result()
                    self.all_results.extend(results)
                    print(f"{Colors.GREEN}✓{Colors.ENDC} {source.upper()}: Found {len(results)} results")
                except Exception as e:
                    print(f"{Colors.RED}✗{Colors.ENDC} {source.upper()}: Error - {str(e)}")
        
        self.search_time = time.time() - start_time
        
        # Deduplicate results
        unique_results = []
        seen_urls = set()
        
        for result in self.all_results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                unique_results.append(result)
                seen_urls.add(url)
        
        self.all_results = unique_results
        
        return self.all_results
    
    def print_results(self):
        """Print formatted results to console"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}📊 Search Results{Colors.ENDC}")
        print(f"{Colors.CYAN}Total results: {Colors.BOLD}{len(self.all_results)}{Colors.ENDC}")
        print(f"{Colors.CYAN}Search time: {Colors.BOLD}{self.search_time:.2f}s{Colors.ENDC}\n")
        
        if not self.all_results:
            print(f"{Colors.YELLOW}No results found for '{self.keyword}'{Colors.ENDC}")
            return
        
        # Group by source
        by_source = {}
        for result in self.all_results:
            source = result.get('source', 'unknown')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(result)
        
        # Print results by source
        for source, results in by_source.items():
            print(f"{Colors.BOLD}{source.upper()}{Colors.ENDC} ({len(results)} results):")
            print("─" * 80)
            
            for i, result in enumerate(results, 1):
                print(f"{Colors.BLUE}{i}. {result.get('title', 'N/A')}{Colors.ENDC}")
                print(f"   {result.get('description', 'No description')[:100]}...")
                print(f"   🔗 {result.get('url', 'N/A')[:70]}...")
                print()


# ============================================================================
# CLI ARGUMENT PARSER
# ============================================================================

def create_parser():
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description='Web Intelligence Gatherer - Automated multi-source web search tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --keyword "cybersecurity" --sources wikipedia github
  python main.py --keyword "python projects" --max-results 10 --format json --output results.json
  python main.py --keyword "data breach" --sources all --format csv --output report.csv
        """
    )
    
    parser.add_argument(
        '--keyword', '-k',
        required=True,
        help='Search keyword or phrase (required)'
    )
    
    parser.add_argument(
        '--sources', '-s',
        nargs='+',
        default=config.DEFAULT_SOURCES,
        help=f'Search sources {config.AVAILABLE_SOURCES} or "all" (default: {config.DEFAULT_SOURCES})'
    )
    
    parser.add_argument(
        '--max-results', '-m',
        type=int,
        default=config.MAX_RESULTS_DEFAULT,
        help=f'Maximum results per source (default: {config.MAX_RESULTS_DEFAULT}, max: {config.MAX_RESULTS_LIMIT})'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=config.VALID_FORMATS,
        default=config.OUTPUT_FORMAT_JSON,
        help='Output format (default: json)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file path (if not specified, prints to console)'
    )
    
    return parser


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main entry point"""
    try:
        parser = create_parser()
        args = parser.parse_args()
        
        # Process sources
        sources = args.sources
        if sources == ['all']:
            sources = config.AVAILABLE_SOURCES
        
        # Validate sources
        invalid = set(sources) - set(config.AVAILABLE_SOURCES)
        if invalid:
            print(f"{Colors.RED}Error: Invalid sources {invalid}{Colors.ENDC}")
            print(f"Valid sources: {config.AVAILABLE_SOURCES}")
            sys.exit(1)
        
        # Create gatherer and search
        gatherer = WebIntelligenceGatherer(args.keyword, sources, args.max_results)
        gatherer.search()
        gatherer.print_results()
        
        # Generate report
        if args.output:
            if args.format == config.OUTPUT_FORMAT_JSON:
                report = ReportGenerator.to_json(gatherer.all_results, args.keyword, gatherer.search_time, sources)
            else:  # CSV
                report = ReportGenerator.to_csv(gatherer.all_results)
            
            # Write to file
            output_path = config.OUTPUT_DIR / args.output
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"\n{Colors.GREEN}✓{Colors.ENDC} Report saved: {Colors.BOLD}{output_path}{Colors.ENDC}")
    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Search interrupted by user{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}Error: {str(e)}{Colors.ENDC}")
        sys.exit(1)


if __name__ == '__main__':
    main()
