from django import template

from orch.esi import register_inclusion_tag
from orch.navigation.models import NavigationSettings

register = template.Library()

esi_inclusion_tag = register_inclusion_tag(register)


# Primary nav
@esi_inclusion_tag('navigation/primarynav.html')
def primarynav(context):
    nav_settings = NavigationSettings.for_site(context.request.site)
    return {
        'primarynav': nav_settings.primary_links.all()[:8],
        'request': context['request'],
    }


# Secondary nav
@esi_inclusion_tag('navigation/secondarynav.html')
def secondarynav(context):
    nav_settings = NavigationSettings.for_site(context.request.site)
    return {
        'secondarynav': nav_settings.secondary_links.all()[:8],
        'request': context['request'],
    }


# Footer nav
@esi_inclusion_tag('navigation/footernav.html')
def footernav(context):
    nav_settings = NavigationSettings.for_site(context.request.site)
    return {
        'footernav': nav_settings.footer_links.all()[:8],
        'request': context['request'],
    }
