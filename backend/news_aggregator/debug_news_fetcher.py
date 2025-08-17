# debug_news_fetcher.py
# Run this script to debug why news fetching returns 0 posts

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from main.news_fetchers import NewsFetchManager
from django.conf import settings

def debug_news_fetching():
    print("=== DEBUGGING NEWS FETCHER ===\n")
    
    # Check API keys
    print("1. Checking API Keys:")
    news_api_key = getattr(settings, 'NEWS_API_KEY', None)
    google_api_key = getattr(settings, 'GOOGLE_NEWS_API_KEY', None)
    
    print(f"   NEWS_API_KEY: {'✓ Set' if news_api_key else '✗ Missing'}")
    print(f"   GOOGLE_NEWS_API_KEY: {'✓ Set' if google_api_key else '✗ Missing'}")
    
    if not news_api_key:
        print("   WARNING: NEWS_API_KEY is missing. Get it from https://newsapi.org/")
    if not google_api_key:
        print("   WARNING: GOOGLE_NEWS_API_KEY is missing. Get it from https://serpapi.com/")
    
    print("\n2. Testing News Fetchers:")
    
    try:
        manager = NewsFetchManager()
        print(f"   Available fetchers: {list(manager.fetchers.keys())}")
        
        # Test each fetcher individually
        for fetcher_name, fetcher in manager.fetchers.items():
            print(f"\n   Testing {fetcher_name} fetcher:")
            
            try:
                if fetcher_name == 'newsapi':
                    articles = fetcher.fetch_news('technology', limit=2, country='in')
                else:
                    articles = fetcher.fetch_news('technology', limit=2)
                
                print(f"   ✓ {fetcher_name}: Got {len(articles)} articles")
                
                if articles:
                    print(f"   Sample article: {articles[0]['title'][:50]}...")
                else:
                    print(f"   No articles returned from {fetcher_name}")
                    
            except Exception as e:
                print(f"   ✗ {fetcher_name} failed: {e}")
        
        # Test the manager
        print(f"\n3. Testing NewsFetchManager:")
        categories = ['technology', 'business']
        all_articles = manager.fetch_all_news(categories, limit=3)
        
        print(f"   Total articles from all fetchers: {len(all_articles)}")
        
        if all_articles:
            print("   Sample articles:")
            for i, article in enumerate(all_articles[:3]):
                print(f"   {i+1}. {article['title'][:60]}...")
                print(f"      URL: {article.get('url', 'No URL')}")
                print(f"      Category: {article.get('category', 'No category')}")
        else:
            print("   No articles retrieved from any fetcher!")
            
    except Exception as e:
        print(f"   Error creating NewsFetchManager: {e}")
    
    print("\n4. Checking for duplicate URLs in database:")
    from main.models import Post
    
    total_posts = Post.objects.count()
    print(f"   Total posts in database: {total_posts}")
    
    if total_posts > 0:
        recent_urls = list(Post.objects.values_list('original_url', flat=True)[:5])
        print(f"   Recent URLs in database:")
        for url in recent_urls:
            print(f"   - {url}")

if __name__ == "__main__":
    debug_news_fetching()