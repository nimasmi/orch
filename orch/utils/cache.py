from django.conf import settings

from wagtail.contrib.wagtailfrontendcache.utils import purge_url_from_cache
from wagtail.wagtailcore.models import Site


def purge_cache_on_all_sites(path):
    if settings.DEBUG:
        return

    for site in Site.objects.all():
        purge_url_from_cache('%s%s' % (site.root_url.rstrip('/'), path))
