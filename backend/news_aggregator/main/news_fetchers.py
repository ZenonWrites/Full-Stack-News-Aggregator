# news_fetchers.py - UPDATED VERSION
import requests
import logging
from django.conf import settings
from typing import List, Dict
from newsapi import NewsApiClient

logger = logging.getLogger(__name__)

class BaseFetcher:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_news(self, category: str = 'general', limit: int = 10) -> List[Dict]:
        raise NotImplementedError   

class NewsAPIFetcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = NewsApiClient(api_key=api_key)

    def fetch_news(self, category: str = 'general', limit: int = 10, country: str = None) -> List[Dict]:
        try:
            # Try country-specific first, then fall back to global
            articles = []
            
            if country:
                # Try country-specific headlines
                response = self.client.get_top_headlines(
                    category=category if category != 'general' else None,
                    language='en',
                    page_size=limit,
                    country=country
                )
                
                country_articles = response.get('articles', [])
                logger.info(f"NewsAPI: Got {len(country_articles)} articles for country={country}, category={category}")
                
                # If we got articles, use them
                if country_articles:
                    articles.extend(country_articles)
                else:
                    # No country-specific articles, fall back to global search
                    logger.info(f"No articles for country={country}, trying global search")
                    response = self.client.get_everything(
                        q=f"{category}" if category != 'general' else 'news',
                        language='en',
                        sort_by='publishedAt',
                        page_size=limit
                    )
                    articles.extend(response.get('articles', []))
            else:
                # Use global search directly
                response = self.client.get_everything(
                    q=f"{category}" if category != 'general' else 'news',
                    language='en',
                    sort_by='publishedAt',
                    page_size=limit
                )
                articles.extend(response.get('articles', []))

            # Process articles
            processed_articles = []
            for article in articles:
                if article.get('title') and article.get('description'):
                    processed_articles.append({
                        'title': article['title'],
                        'description': article['description'],
                        'url': article['url'],
                        'image_url': article.get('urlToImage'),
                        'published_at': article.get('publishedAt'),
                        'source': article.get('source', {}).get('name', ''),
                        'category': category
                    })

            logger.info(f"NewsAPI: Returning {len(processed_articles)} processed articles")
            return processed_articles

        except Exception as e:
            logger.error(f"NewsAPI SDK fetch error: {e}")
            return []

class GoogleNewsAPIFetcher(BaseFetcher):
    BASE_URL = "https://serpapi.com/search"

    def fetch_news(self, category='general', limit: int = 10) -> List[Dict]:
        try:
            params = {
                'engine': 'google_news',
                'q': category if category != 'general' else 'latest news',
                'api_key': self.api_key,
                'hl': 'en',
                'gl': 'us',
                'num': min(limit, 100)  # SerpAPI max is 100
            }

            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            news_results = data.get('news_results', [])
            articles = []

            for article in news_results[:limit]:  # Limit the results
                if article.get('title') and article.get('snippet'):
                    # Handle source properly - it can be a dict or string
                    source_name = article.get('source', '')
                    if isinstance(source_name, dict):
                        source_name = source_name.get('name', '')
                    
                    articles.append({
                        'title': article['title'],
                        'description': article['snippet'],
                        'url': article.get('link'),
                        'image_url': article.get('thumbnail'),
                        'published_at': article.get('date'),
                        'source': source_name,
                        'category': category
                    })

            logger.info(f"GoogleNews: Returning {len(articles)} articles")
            return articles

        except Exception as e:
            logger.error(f"SerpApi Google News fetch error: {e}")
            return []

class NewsFetchManager:
    def __init__(self):
        self.fetchers = {}
        
        # Only add fetchers if API keys are available
        news_api_key = getattr(settings, 'NEWS_API_KEY', '')
        google_api_key = getattr(settings, 'GOOGLE_NEWS_API_KEY', '')
        
        if news_api_key:
            self.fetchers['newsapi'] = NewsAPIFetcher(news_api_key)
            logger.info("NewsAPI fetcher initialized")
        else:
            logger.warning("NEWS_API_KEY not found, skipping NewsAPI fetcher")
            
        if google_api_key:
            self.fetchers['google'] = GoogleNewsAPIFetcher(google_api_key)
            logger.info("Google News fetcher initialized")
        else:
            logger.warning("GOOGLE_NEWS_API_KEY not found, skipping Google News fetcher")

    def fetch_all_news(
        self, 
        categories: List[str] = None, 
        limit: int = 10, 
        country: str = None  # Changed default from 'in' to None
    ) -> List[Dict]:
        if not categories:
            categories = ['general', 'technology', 'business', 'sports', 'health']

        if not self.fetchers:
            logger.error("No fetchers available - check API keys")
            return []

        all_articles = []
        for fetcher_name, fetcher in self.fetchers.items():
            for category in categories:
                try:
                    logger.info(f"Fetching from {fetcher_name} for category: {category}")
                    
                    # Only pass country parameter to NewsAPIFetcher
                    if isinstance(fetcher, NewsAPIFetcher):
                        articles = fetcher.fetch_news(category, limit, country)
                    else:
                        # Other fetchers (e.g. SerpApi) don't support country filter
                        articles = fetcher.fetch_news(category, limit)
                    
                    logger.info(f"Got {len(articles)} articles from {fetcher_name} for {category}")
                    all_articles.extend(articles)
                    
                except Exception as e:
                    logger.error(f"Fetcher '{fetcher_name}' failed for category '{category}': {e}")

        logger.info(f"Total articles collected: {len(all_articles)}")
        return all_articles