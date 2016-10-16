from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models

from modelcluster.fields import ParentalKey
from wagtail.wagtailadmin.edit_handlers import (FieldPanel, InlinePanel,
                                                StreamFieldPanel)
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailsearch import index
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel

from orch.utils.blocks import StoryBlock
from orch.utils.models import (CallToActionSnippet, ListingFields,
                               RelatedDocument, RelatedPage, SocialFields)


class StandardPageRelatedDocument(RelatedDocument):
    page = ParentalKey('standardpage.StandardPage', related_name='related_documents')


class StandardPageRelatedPage(RelatedPage):
    source_page = ParentalKey('standardpage.StandardPage', related_name='related_pages')


class StandardPage(Page, SocialFields, ListingFields):
    introduction = models.TextField(blank=True)
    call_to_action = models.ForeignKey(CallToActionSnippet, blank=True,
                                       null=True, on_delete=models.SET_NULL,
                                       related_name='+')
    body = StreamField(StoryBlock())

    search_fields = Page.search_fields + [
        index.SearchField('introduction'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
        SnippetChooserPanel('call_to_action'),
        StreamFieldPanel('body'),
        InlinePanel('related_documents', label="Related documents"),
        InlinePanel('related_pages', label="Related pages"),
    ]

    promote_panels = Page.promote_panels + SocialFields.promote_panels + ListingFields.promote_panels


class StandardIndex(Page, SocialFields):
    introduction = models.TextField(blank=True)
    call_to_action = models.ForeignKey(CallToActionSnippet, blank=True,
                                       null=True, on_delete=models.SET_NULL,
                                       related_name='+')

    content_panels = Page.content_panels + [
        FieldPanel('introduction'),
        SnippetChooserPanel('call_to_action'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('introduction'),
    ]

    promote_panels = Page.promote_panels + SocialFields.promote_panels

    def get_context(self, request):
        context = super().get_context(request)
        subpages = self.get_children().live()
        per_page = settings.DEFAULT_PER_PAGE
        page_number = request.GET.get('page')
        paginator = Paginator(subpages, per_page)

        try:
            subpages = paginator.page(page_number)
        except PageNotAnInteger:
            subpages = paginator.page(1)
        except EmptyPage:
            subpages = paginator.page(paginator.num_pages)

        context['subpages'] = subpages

        return context
