# test_api_direct.py
import requests
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings

def test_newsapi_direct():
    """Test NewsAPI directly"""
    api_key = getattr(settings, 'NEWS_API_KEY', '')
    print(f"=== TESTING NEWSAPI DIRECTLY ===")
    print(f"API Key: {api_key[:10]}...{api_key[-5:]}")
    
    # Test 1: Top headlines for India
    print("\n1. Testing top headlines (India, Technology):")
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        'country': 'in',
        'category': 'technology',
        'pageSize': 5,
        'apiKey': api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            total_results = data.get('totalResults', 0)
            print(f"   ✅ Total Results: {total_results}")
            print(f"   ✅ Articles Returned: {len(articles)}")
            
            if articles:
                print("   Sample articles:")
                for i, article in enumerate(articles[:2]):
                    print(f"      {i+1}. {article.get('title', 'No title')[:60]}...")
                    print(f"         Source: {article.get('source', {}).get('name', 'Unknown')}")
                    print(f"         URL: {article.get('url', 'No URL')}")
            else:
                print("   ⚠️ No articles returned (but API call successful)")
                
        else:
            print(f"   ❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 2: Try without country filter
    print("\n2. Testing everything endpoint (Global Technology):")
    url2 = "https://newsapi.org/v2/everything"
    params2 = {
        'q': 'technology',
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': 5,
        'apiKey': api_key
    }
    
    try:
        response2 = requests.get(url2, params=params2, timeout=15)
        print(f"   Status Code: {response2.status_code}")
        
        if response2.status_code == 200:
            data2 = response2.json()
            articles2 = data2.get('articles', [])
            total_results2 = data2.get('totalResults', 0)
            print(f"   ✅ Total Results: {total_results2}")
            print(f"   ✅ Articles Returned: {len(articles2)}")
            
            if articles2:
                print("   Sample articles:")
                for i, article in enumerate(articles2[:2]):
                    print(f"      {i+1}. {article.get('title', 'No title')[:60]}...")
                    print(f"         Source: {article.get('source', {}).get('name', 'Unknown')}")
            else:
                print("   ⚠️ No articles returned")
        else:
            print(f"   ❌ Error {response2.status_code}: {response2.text}")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")

def test_django_fetcher():
    """Test the Django NewsAPIFetcher"""
    print(f"\n=== TESTING DJANGO NEWSAPI FETCHER ===")
    
    try:
        from main.news_fetchers import NewsAPIFetcher
        api_key = getattr(settings, 'NEWS_API_KEY', '')
        
        fetcher = NewsAPIFetcher(api_key)
        print("NewsAPIFetcher created successfully")
        
        # Test with country
        print("\n1. Testing with country='in':")
        articles1 = fetcher.fetch_news('technology', limit=5, country='in')
        print(f"   Returned {len(articles1)} articles")
        
        if articles1:
            print("   Sample article:")
            article = articles1[0]
            print(f"   Title: {article.get('title', 'No title')}")
            print(f"   Description: {article.get('description', 'No description')[:100]}...")
            print(f"   URL: {article.get('url', 'No URL')}")
            print(f"   Category: {article.get('category', 'No category')}")
        
        # Test without country
        print("\n2. Testing without country (global):")
        articles2 = fetcher.fetch_news('technology', limit=5, country=None)
        print(f"   Returned {len(articles2)} articles")
        
        return len(articles1) + len(articles2) > 0
        
    except Exception as e:
        print(f"❌ Django fetcher failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_serpapi():
    """Test SerpAPI (Google News)"""
    print(f"\n=== TESTING SERPAPI (GOOGLE NEWS) ===")
    
    api_key = getattr(settings, 'GOOGLE_NEWS_API_KEY', '')
    print(f"API Key: {api_key[:10]}...{api_key[-5:]}")
    
    url = "https://serpapi.com/search"
    params = {
        'engine': 'google_news',
        'q': 'technology',
        'api_key': api_key,
        'hl': 'en',
        'gl': 'us',
        'num': 5
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            news_results = data.get('news_results', [])
            print(f"✅ Articles Returned: {len(news_results)}")
            
            if news_results:
                print("Sample articles:")
                for i, article in enumerate(news_results[:2]):
                    print(f"   {i+1}. {article.get('title', 'No title')[:60]}...")
                    print(f"      Source: {article.get('source', 'Unknown')}")
            else:
                print("⚠️ No articles returned")
                
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_newsapi_direct()
    
    django_works = test_django_fetcher()
    
    test_serpapi()
    
    print(f"\n=== SUMMARY ===")
    print(f"Django fetcher working: {'✅ Yes' if django_works else '❌ No'}")