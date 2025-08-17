# main/management/commands/fetch_news.py - UPDATED
from django.core.management.base import BaseCommand
from django.conf import settings
from main.models import Post
from main.news_fetchers import NewsFetchManager
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetch news from various API and save to database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--categories',
            nargs='+',
            default=['general', 'technology', 'business'],
            help='Categories to fetch news for'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help="Number of articles per category",
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug output'
        )
        parser.add_argument(
            '--country',
            type=str,
            default=None,
            help='Country code for NewsAPI (e.g., "in" for India, "us" for USA). Default: None (global)'
        )

    def handle(self, *args, **options):
        debug = options.get('debug', False)
        country = options.get('country')
        
        self.stdout.write('Starting news fetch...')
        
        # Check API keys first
        if debug:
            news_key = getattr(settings, 'NEWS_API_KEY', None)
            google_key = getattr(settings, 'GOOGLE_NEWS_API_KEY', None)
            self.stdout.write(f'NEWS_API_KEY: {"Set" if news_key else "Missing"}')
            self.stdout.write(f'GOOGLE_NEWS_API_KEY: {"Set" if google_key else "Missing"}')
            self.stdout.write(f'Country filter: {country or "None (global)"}')
        
        try:
            manager = NewsFetchManager()
            
            if debug:
                self.stdout.write(f'Available fetchers: {list(manager.fetchers.keys())}')
            
            if not manager.fetchers:
                self.stdout.write(
                    self.style.ERROR("No fetchers available - check your API keys in settings")
                )
                return
            
            articles = manager.fetch_all_news(
                categories=options['categories'],
                limit=options['limit'],
                country=country
            )
            
            self.stdout.write(f'Retrieved {len(articles)} articles total')
            
            if debug and articles:
                self.stdout.write('Sample articles:')
                for i, article in enumerate(articles[:3]):
                    self.stdout.write(f'  {i+1}. {article["title"][:50]}...')
                    self.stdout.write(f'     URL: {article.get("url", "No URL")}')
                    self.stdout.write(f'     Source: {article.get("source", "No source")}')

            created_count = 0
            duplicate_count = 0
            error_count = 0
            
            for article in articles:
                try:
                    # Check for required fields
                    if not article.get('title') or not article.get('url'):
                        if debug:
                            self.stdout.write(f'Skipping article - missing title or URL')
                        error_count += 1
                        continue
                    
                    # Check for duplicates
                    if Post.objects.filter(original_url=article['url']).exists():
                        duplicate_count += 1
                        if debug:
                            self.stdout.write(f'Duplicate URL: {article["url"]}')
                        continue
                    
                    summary = self.generate_summary(article.get('description', ''))
                    
                    post = Post.objects.create(
                        title=article['title'],
                        content=summary,
                        original_url=article['url'],
                        image_url=article.get('image_url'),
                        category=article.get('category', 'general')
                    )
                    created_count += 1
                    
                    if debug:
                        self.stdout.write(f'Created: {post.title[:40]}...')
                
                except Exception as e:
                    logger.error(f"Error saving article: {e}")
                    if debug:
                        self.stdout.write(f'Error saving article: {e}')
                    error_count += 1
                    continue
            
            # Summary
            self.stdout.write(
                self.style.SUCCESS(f"Successfully created {created_count} new posts")
            )
            self.stdout.write(f"Duplicates skipped: {duplicate_count}")
            self.stdout.write(f"Errors encountered: {error_count}")
            
            if created_count == 0 and len(articles) > 0:
                self.stdout.write(
                    self.style.WARNING("No new posts created - all articles may be duplicates")
                )
            elif len(articles) == 0:
                self.stdout.write(
                    self.style.ERROR("No articles retrieved - try without country filter or check API keys")
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Command failed: {e}")
            )
            logger.error(f"fetch_news command failed: {e}")

    def generate_summary(self, description: str) -> str:
        """Generate a summary from the description"""
        if not description:
            return "No description available"
        if len(description) > 200:
            return description[:200] + "..."
        return description