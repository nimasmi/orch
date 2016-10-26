import datetime
from collections import defaultdict

from django.conf import settings
from django.core import checks
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _

from modelcluster.fields import ParentalKey
from wagtail.wagtailadmin.edit_handlers import (FieldPanel, FieldRowPanel,
                                                InlinePanel, MultiFieldPanel,
                                                StreamFieldPanel)
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore.models import (Orderable, Page, PageManager,
                                        PageQuerySet)
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtailsnippets.models import register_snippet

from orch.utils.blocks import StoryBlock
from orch.utils.models import (ListingFields, RelatedDocument, RelatedPage,
                               SocialFields)


@register_snippet
class EventType(models.Model):
    title = models.CharField(max_length=255)
    description = RichTextField(help_text="This isn't currently shown "
                                "publicly, but could be in the future")

    def __str__(self):
        return self.title


class EventPageRelatedDocument(RelatedDocument):
    page = ParentalKey('events.EventPage', related_name='related_documents')


class EventPageRelatedPage(RelatedPage):
    source_page = ParentalKey('events.EventPage', related_name='related_pages')


class EventPageEventType(models.Model):
    event_type = models.ForeignKey(
        'events.EventType',
        on_delete=models.CASCADE
    )
    page = ParentalKey('events.EventPage', related_name='event_types')

    panels = [
        SnippetChooserPanel('event_type'),
    ]


class Rehearsal(models.Model):
    event = ParentalKey('events.EventPage', related_name='rehearsals')
    date = models.DateField()
    time = models.TimeField(default=datetime.time(19, 30))
    notes = RichTextField(blank=True)
    location = models.ForeignKey('locations.Location', related_name='+',
                                 null=True, blank=True,
                                 on_delete=models.SET_NULL,
                                 help_text="Leave blank unless it's a non-default location.")
    first_half = models.CharField(max_length=255, blank=True)
    second_half = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = 'date', 'time'

    panels = (
        FieldPanel('date', classname='full'),
        FieldPanel('time', classname='full'),
        SnippetChooserPanel('location'),
        FieldPanel('first_half'),
        FieldPanel('first_half', classname='full'),
    )


class EventPiecePerformance(Orderable, models.Model):
    page = ParentalKey('events.EventPage', related_name='pieces')
    piece = models.ForeignKey('music.Piece', related_name='+')

    panels = [
        SnippetChooserPanel('piece'),
    ]

    def __str__(self):
        return self.page.title + ": " + self.piece.title


class EventPageQuerySet(PageQuerySet):

    def _annotate_latest_date(self):
        return (
            self.annotate(latest_date=Coalesce('end_date', 'start_date'))
        )

    def upcoming(self):
        return (
            self._annotate_latest_date()
            .filter(latest_date__gte=timezone.now().date())
            .order_by('start_date')
        )

    def past(self):
        return (
            self._annotate_latest_date()
            .filter(latest_date__lt=timezone.now().date())
            .order_by('-start_date')
        )


class EventPageManager(PageManager):
    def get_queryset(self):
        return EventPageQuerySet(self.model, using=self._db)

    def upcoming(self):
        return self.get_queryset().upcoming()

    def past(self):
        return self.get_queryset().past()


class EventPage(Page, SocialFields, ListingFields):
    start_date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    # Permit null=True on end_date, as we use Coalesce to query 'end_date or start_date'
    end_date = models.DateField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)

    # It's datetime for easy comparison with first_published_at
    publication_date = models.DateTimeField(
        null=True, blank=True,
        help_text="Use this field to override the date that the "
        "event item appears to have been published."
    )

    location = models.ForeignKey('locations.Location', related_name='+',
                                 on_delete=models.SET_NULL, null=True)
    cost = models.CharField(max_length=100)

    poster = models.ForeignKey('wagtaildocs.Document', null=True, blank=True,
                               related_name='+', on_delete=models.SET_NULL)

    header_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True,
                                     on_delete=models.SET_NULL, related_name='+',
                                     help_text="Leave blank to have no header image.")

    introduction = models.TextField(blank=True)
    body = StreamField(StoryBlock())

    objects = EventPageManager()

    parent_page_types = ['events.EventIndexPage']

    search_fields = Page.search_fields + [
        index.SearchField('introduction'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [FieldRowPanel([
                FieldPanel('start_date'),
                FieldPanel('start_time'),
            ])],
            heading='Start'
        ),
        MultiFieldPanel(
            [FieldRowPanel([
                FieldPanel('end_date'),
                FieldPanel('end_time'),
            ])],
            heading='End'
        ),
        InlinePanel('event_types', label="Event types"),

        FieldPanel('location'),
        InlinePanel('rehearsals', label="Rehearsals"),
        InlinePanel('pieces', label="Pieces"),

        FieldPanel('introduction'),
        StreamFieldPanel('body'),

        InlinePanel('related_documents', label="Related documents"),
        InlinePanel('related_pages', label="Related pages"),
    ]

    promote_panels = (
        Page.promote_panels +  # slug, seo_title, show_in_menus, search_description
        SocialFields.promote_panels +
        ListingFields.promote_panels
    )

    def clean_fields(self, exclude=None):
        errors = defaultdict(list)
        try:
            super().clean_fields(exclude)
        except ValidationError as e:
            errors.update(e.message_dict)

        # Require start time if there's an end time
        if self.end_time and not self.start_time:
            errors["start_time"].append(_("If you enter an end time, you must also enter a start time"))

        if self.end_date and self.end_date < self.start_date:
            errors["end_date"].append(_("Events involving time travel are not supported"))
        elif self.end_date == self.start_date and self.end_time and self.end_time < self.start_time:
            errors["end_time"].append(_("Events involving time travel are not supported"))

        if errors:
            raise ValidationError(errors)


class EventIndexPage(Page):

    @classmethod
    def check(cls, **kwargs):
        is_mysql = any(['mysql' in db['ENGINE'].lower()
                        for db in settings.DATABASES.values()])
        errors = super(EventIndexPage, cls).check(**kwargs)
        if is_mysql:
            errors.append(
                checks.Error(
                    "Event Page uses Coalesce function; not tested on MySQL",
                    hint="The query for returning past and future events uses "
                    "django.db.models.functions.Coalesce, which on MySQL "
                    "requires explicit casting to the correct database type, "
                    "see https://docs.djangoproject.com/en/1.9/ref/models/database-functions/#coalesce. "
                    "The Django documentation specifically mentions datetime "
                    "types, but this codebase has been written using "
                    "PostgreSQL, so no such casting or testing has been done. "
                    "If your project uses Django 1.10+, then you can easily "
                    "address this using django.db.models.functions.Cast, and "
                    "on Django 1.9 this could easily be backported from 1.10.",
                    obj=cls,
                    id='events.E001',
                )
            )
        return errors

    @cached_property
    def upcoming_events(self):
        return (
            EventPage.objects
            .live().public().descendant_of(self).upcoming()
        )

    @cached_property
    def past_events(self):
        return (
            EventPage.objects
            .live().public().descendant_of(self).past()
        )

    def get_context(self, request):
        context = super().get_context(request)
        past_events = self.past_events
        upcoming_events = self.upcoming_events

        past = request.GET.get('past', False)
        if past:
            events = past_events
        else:
            events = upcoming_events
        per_page = settings.DEFAULT_PER_PAGE
        page_number = request.GET.get('page')
        paginator = Paginator(events, per_page)

        try:
            events = paginator.page(page_number)
        except PageNotAnInteger:
            events = paginator.page(1)
        except EmptyPage:
            events = paginator.page(paginator.num_pages)

        context.update({
            'show_past': past,
            'events': events,
            'past_events': past_events,
            'upcoming_events': upcoming_events,
        })

        if past:
            context['extra_url_params'] = urlencode({'past': True})

        return context
