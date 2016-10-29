from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailimages.models import (AbstractImage, AbstractRendition,
                                          Image)
from wagtail.wagtailsnippets.models import register_snippet


# @register_snippet
# class ImageLicence(models.Model):
#     name = models.CharField(max_length=256)
#     description = models.TextField()
#     attribution_required = models.BooleanField(default=True)
# 
#     panels = [
#         FieldPanel('name'),
#         FieldPanel('description'),
#         FieldPanel('attribution_required'),
#     ]
# 
#     def __str__(self):
#         return self.name


# We define our own custom image class to replace wagtailimages.Image,
# providing various additional data fields
class CustomImage(AbstractImage):
    alt = models.CharField(max_length=255, blank=True)
    credit = models.CharField(max_length=255, blank=True)
    # licence = models.ForeignKey(ImageLicence, null=True, on_delete=models.SET_NULL)

    admin_form_fields = Image.admin_form_fields + (
        'alt',
        'credit',
    )

    # When you save the image, check if alt text has been set. If not, set it as the title.
    def save(self, *args, **kwargs):
        if not self.alt:
            self.alt = self.title

        super().save(*args, **kwargs)


# Do feature detection when a user saves an image without a focal point
@receiver(pre_save, sender=CustomImage)
def image_feature_detection(sender, instance, **kwargs):
    if settings.WAGTAILIMAGES_FEATURE_DETECTION_ENABLED:
        # Make sure the image doesn't already have a focal point
        if not instance.has_focal_point():
            # Set the focal point
            instance.set_focal_point(instance.get_suggested_focal_point())


# Receive the pre_delete signal and delete the file associated with the model instance.
@receiver(pre_delete, sender=CustomImage)
def image_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)


class Rendition(AbstractRendition):
    image = models.ForeignKey(
        CustomImage,
        related_name='renditions',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = (
            ('image', 'filter', 'focal_point_key'),
        )


# Receive the pre_delete signal and delete the file associated with the model instance.
@receiver(pre_delete, sender=Rendition)
def rendition_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)
