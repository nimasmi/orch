from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.wagtailadmin.edit_handlers import InlinePanel
from wagtail.wagtailcore.models import Orderable

from orch.utils.models import LinkFields


class NavigationLinkPrimary(Orderable, LinkFields):
    nav_settings = ParentalKey('NavigationSettings', related_name='primary_links')


class NavigationLinkSecondary(Orderable, LinkFields):
    nav_settings = ParentalKey('NavigationSettings', related_name='secondary_links')


class NavigationLinkFooter(Orderable, LinkFields):
    nav_settings = ParentalKey('NavigationSettings', related_name='footer_links')


@register_setting(icon='list-ul')
class NavigationSettings(BaseSetting, ClusterableModel):

    panels = [
        InlinePanel('primary_links', label="Primary Navigation Links"),
        InlinePanel('secondary_links', label="Secondary Navigation Links"),
        InlinePanel('footer_links', label="Footer Navigation Links"),
    ]
