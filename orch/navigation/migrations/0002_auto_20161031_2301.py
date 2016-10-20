# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0029_unicode_slugfield_dj19'),
        ('navigation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NavigationLinkFooter',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('link_url', models.URLField(blank=True)),
                ('link_text', models.CharField(max_length=255, blank=True)),
                ('link_page', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to='wagtailcore.Page', blank=True)),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NavigationLinkPrimary',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('link_url', models.URLField(blank=True)),
                ('link_text', models.CharField(max_length=255, blank=True)),
                ('link_page', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to='wagtailcore.Page', blank=True)),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NavigationLinkSecondary',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('link_url', models.URLField(blank=True)),
                ('link_text', models.CharField(max_length=255, blank=True)),
                ('link_page', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to='wagtailcore.Page', blank=True)),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NavigationSettings',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('site', models.OneToOneField(to='wagtailcore.Site', editable=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='footernavigationsnippet',
            name='menu_item',
        ),
        migrations.RemoveField(
            model_name='primarynavigationsnippet',
            name='menu_item',
        ),
        migrations.RemoveField(
            model_name='primarynavigationsubmenusnippet',
            name='menu_item',
        ),
        migrations.RemoveField(
            model_name='primarynavigationsubmenusnippet',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='secondarynavigationsnippet',
            name='menu_item',
        ),
        migrations.DeleteModel(
            name='FooterNavigationSnippet',
        ),
        migrations.DeleteModel(
            name='PrimaryNavigationSnippet',
        ),
        migrations.DeleteModel(
            name='PrimaryNavigationSubmenuSnippet',
        ),
        migrations.DeleteModel(
            name='SecondaryNavigationSnippet',
        ),
        migrations.AddField(
            model_name='navigationlinksecondary',
            name='nav_settings',
            field=modelcluster.fields.ParentalKey(related_name='secondary_links', to='navigation.NavigationSettings'),
        ),
        migrations.AddField(
            model_name='navigationlinkprimary',
            name='nav_settings',
            field=modelcluster.fields.ParentalKey(related_name='primary_links', to='navigation.NavigationSettings'),
        ),
        migrations.AddField(
            model_name='navigationlinkfooter',
            name='nav_settings',
            field=modelcluster.fields.ParentalKey(related_name='footer_links', to='navigation.NavigationSettings'),
        ),
    ]
