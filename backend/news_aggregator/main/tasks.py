from celery import shared_task
from django.core.management import call_command
from .models import Post, User
from .news_fetchers import NewsFetcherManager
import logging

logger = logging.getLogger(__name__)

@shared_task
def fetch_news_task():
    """Periodic task to fetch news"""
    try:
        # Get all unique categories from users
        categories = set()
        for user in User.objects.all():
            if user.categories:
                categories.update(user.categories)
        
        if not categories:
            categories = ['general', 'technology', 'business', 'sports', 'health']
        
        # Fetch news
        manager = NewsFetcherManager()
        articles = manager.fetch_all_news(list(categories), limit=5)
        
        created_count = 0
        for article in articles:
            if not Post.objects.filter(original_url=article['url']).exists():
                # Simple summary for now
                summary = article['description'][:200] + "..." if len(article['description']) > 200 else article['description']
                
                Post.objects.create(
                    title=article['title'],
                    content=summary,
                    original_url=article['url'],
                    image_url=article.get('image_url'),
                    category=article.get('category', 'general')
                )
                created_count += 1
        
        logger.info(f"Fetched and created {created_count} new posts")
        return f"Created {created_count} new posts"
        
    except Exception as e:
        logger.error(f"Error in fetch_news_task: {e}")
        raise

@shared_task
def generate_ai_summary_task(post_id):
    """Background task to generate AI summary for a post"""
    try:
        post = Post.objects.get(id=post_id)
        # Placeholder for AI integration
        # summary = openai_api_call(post.content)  # Implement this
        summary = f"AI Summary: {post.content[:150]}..."
        
        post.content = summary
        post.save()
        
        logger.info(f"Generated AI summary for post {post_id}")
        return f"Generated summary for post {post_id}"
        
    except Post.DoesNotExist:
        logger.error(f"Post {post_id} not found")
    except Exception as e:
        logger.error(f"Error generating summary for post {post_id}: {e}")
        raise

@shared_task
def cleanup_old_posts():
    """Clean up posts older than 30 days"""
    from django.utils import timezone
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=30)
    deleted_count = Post.objects.filter(created_at__lt=cutoff_date).delete()[0]
    
    logger.info(f"Cleaned up {deleted_count} old posts")
    return f"Deleted {deleted_count} old posts"

# Error handling decorator
from functools import wraps

def handle_task_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Task {func.__name__} failed: {e}")
            # You can add notification logic here
            raise
    return wrapper