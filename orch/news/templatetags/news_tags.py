from django import template
from django.db.models.functions import Coalesce
from django.utils import timezone

from orch.esi import register_inclusion_tag
from orch.news.models import NewsPage

register = template.Library()

esi_inclusion_tag = register_inclusion_tag(register)


@esi_inclusion_tag('news/tags/latest_news.html')
def latest_news(context, count=None):
    now = timezone.now()
    news = NewsPage.objects.live().public().annotate(
        date=Coalesce('publication_date', 'first_published_at'),
    ).order_by('-date').filter(date__lte=now, expiry_date__gte=now)
    if (count is not None):
        news = news[:count]
    return {
        'news': news,
        'request': context['request'],
    }
