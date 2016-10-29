from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.models import Page
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel

from orch.events.models import EventPage
from orch.utils.models import CallToActionSnippet, SocialFields


class HomePage(Page, SocialFields):
    strapline = models.CharField(blank=True, max_length=255)
    call_to_action = models.ForeignKey(CallToActionSnippet, blank=True,
                                       null=True, on_delete=models.SET_NULL,
                                       related_name='+')

    search_fields = Page.search_fields + [
        index.SearchField('strapline'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('strapline'),
        SnippetChooserPanel('call_to_action'),
    ]

    promote_panels = (
        Page.promote_panels +  # slug, seo_title, show_in_menus, search_description
        SocialFields.promote_panels
    )

    # Only allow creating HomePages at the root level
    parent_page_types = ['wagtailcore.Page']

    def get_context(self, request):
        context = super().get_context(request)
        next_concert = EventPage.objects.filter(event_types__event_type__title__iexact='concert').first()  # FIXME needs to be upcoming
        next_other_event = EventPage.objects.exclude(event_types__event_type__title__iexact='concert').first()  # FIXME needs to be upcoming
        upcoming_events = EventPage.objects.all()  # FIXME needs to be upcoming
        context.update({
            'next_concert': next_concert,
            'next_other_event': next_other_event,
            'upcoming_events': upcoming_events,
        })
        return context
