# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import modelcluster.fields
import modelcluster.tags
import wagtail.wagtailcore.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
        ('wagtailcore', '0010_change_page_owner_to_null_on_delete'),
        ('wagtailimages', '0005_make_filter_spec_unique'),
        ('wagtaildocs', '0002_initial_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='Advert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('url', models.URLField(null=True, blank=True)),
                ('text', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AdvertPlacement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('advert', models.ForeignKey(related_name='+', to='tests.Advert')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BlogEntryPage',
            fields=[
                ('page_ptr', models.OneToOneField(to='wagtailcore.Page', auto_created=True, primary_key=True, parent_link=True, serialize=False)),
                ('body', wagtail.wagtailcore.fields.RichTextField()),
                ('date', models.DateField(verbose_name='Post date')),
                ('feed_image', models.ForeignKey(to='wagtailimages.Image', null=True, related_name='+', blank=True, on_delete=django.db.models.deletion.SET_NULL)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='BlogEntryPageCarouselItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('link_external', models.URLField(verbose_name='External link', blank=True)),
                ('embed_url', models.URLField(verbose_name='Embed URL', blank=True)),
                ('caption', models.CharField(max_length=255, blank=True)),
                ('image', models.ForeignKey(to='wagtailimages.Image', null=True, related_name='+', blank=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('link_document', models.ForeignKey(to='wagtaildocs.Document', null=True, related_name='+', blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BlogEntryPageRelatedLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('link_external', models.URLField(verbose_name='External link', blank=True)),
                ('title', models.CharField(help_text='Link title', max_length=255)),
                ('link_document', models.ForeignKey(to='wagtaildocs.Document', null=True, related_name='+', blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BlogEntryPageTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('content_object', modelcluster.fields.ParentalKey(related_name='tagged_items', to='tests.BlogEntryPage')),
                ('tag', models.ForeignKey(related_name='tests_blogentrypagetag_items', to='taggit.Tag')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BlogIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(to='wagtailcore.Page', auto_created=True, primary_key=True, parent_link=True, serialize=False)),
                ('intro', wagtail.wagtailcore.fields.RichTextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='BlogIndexPageRelatedLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('link_external', models.URLField(verbose_name='External link', blank=True)),
                ('title', models.CharField(help_text='Link title', max_length=255)),
                ('link_document', models.ForeignKey(to='wagtaildocs.Document', null=True, related_name='+', blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContactPage',
            fields=[
                ('page_ptr', models.OneToOneField(to='wagtailcore.Page', auto_created=True, primary_key=True, parent_link=True, serialize=False)),
                ('telephone', models.CharField(max_length=20, blank=True)),
                ('email', models.EmailField(max_length=75, blank=True)),
                ('address_1', models.CharField(max_length=255, blank=True)),
                ('address_2', models.CharField(max_length=255, blank=True)),
                ('city', models.CharField(max_length=255, blank=True)),
                ('country', models.CharField(max_length=255, blank=True)),
                ('post_code', models.CharField(max_length=10, blank=True)),
                ('body', wagtail.wagtailcore.fields.RichTextField(blank=True)),
                ('feed_image', models.ForeignKey(to='wagtailimages.Image', null=True, related_name='+', blank=True, on_delete=django.db.models.deletion.SET_NULL)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page', models.Model),
        ),
        migrations.CreateModel(
            name='EventIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(to='wagtailcore.Page', auto_created=True, primary_key=True, parent_link=True, serialize=False)),
                ('intro', wagtail.wagtailcore.fields.RichTextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='EventIndexPageRelatedLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('link_external', models.URLField(verbose_name='External link', blank=True)),
                ('title', models.CharField(help_text='Link title', max_length=255)),
                ('link_document', models.ForeignKey(to='wagtaildocs.Document', null=True, related_name='+', blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventPage',
            fields=[
                ('page_ptr', models.OneToOneField(to='wagtailcore.Page', auto_created=True, primary_key=True, parent_link=True, serialize=False)),
                ('date_from', models.DateField(verbose_name='Start date')),
                ('date_to', models.DateField(verbose_name='End date', null=True, blank=True, help_text='Not required if event is on a single day')),
                ('time_from', models.TimeField(verbose_name='Start time', null=True, blank=True)),
                ('time_to', models.TimeField(verbose_name='End time', null=True, blank=True)),
                ('audience', models.CharField(max_length=255, choices=[('public', 'Public'), ('private', 'Private')])),
                ('location', models.CharField(max_length=255)),
                ('body', wagtail.wagtailcore.fields.RichTextField(blank=True)),
                ('cost', models.CharField(max_length=255)),
                ('signup_link', models.URLField(blank=True)),
                ('feed_image', models.ForeignKey(to='wagtailimages.Image', null=True, related_name='+', blank=True, on_delete=django.db.models.deletion.SET_NULL)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='EventPageCarouselItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('link_external', models.URLField(verbose_name='External link', blank=True)),
                ('embed_url', models.URLField(verbose_name='Embed URL', blank=True)),
                ('caption', models.CharField(max_length=255, blank=True)),
                ('image', models.ForeignKey(to='wagtailimages.Image', null=True, related_name='+', blank=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('link_document', models.ForeignKey(to='wagtaildocs.Document', null=True, related_name='+', blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventPageRelatedLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('link_external', models.URLField(verbose_name='External link', blank=True)),
                ('title', models.CharField(help_text='Link title', max_length=255)),
                ('link_document', models.ForeignKey(to='wagtaildocs.Document', null=True, related_name='+', blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventPageSpeaker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('link_external', models.URLField(verbose_name='External link', blank=True)),
                ('first_name', models.CharField(verbose_name='Name', max_length=255, blank=True)),
                ('last_name', models.CharField(verbose_name='Surname', max_length=255, blank=True)),
                ('image', models.ForeignKey(to='wagtailimages.Image', null=True, related_name='+', blank=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('link_document', models.ForeignKey(to='wagtaildocs.Document', null=True, related_name='+', blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FormField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('label', models.CharField(help_text='The label of the form field', max_length=255)),
                ('field_type', models.CharField(max_length=16, choices=[('singleline', 'Single line text'), ('multiline', 'Multi-line text'), ('email', 'Email'), ('number', 'Number'), ('url', 'URL'), ('checkbox', 'Checkbox'), ('checkboxes', 'Checkboxes'), ('dropdown', 'Drop down'), ('radio', 'Radio buttons'), ('date', 'Date'), ('datetime', 'Date/time')])),
                ('required', models.BooleanField(default=True)),
                ('choices', models.CharField(help_text='Comma separated list of choices. Only applicable in checkboxes, radio and dropdown.', max_length=512, blank=True)),
                ('default_value', models.CharField(help_text='Default value. Comma separated values supported for checkboxes.', max_length=255, blank=True)),
                ('help_text', models.CharField(max_length=255, blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FormPage',
            fields=[
                ('page_ptr', models.OneToOneField(to='wagtailcore.Page', auto_created=True, primary_key=True, parent_link=True, serialize=False)),
                ('to_address', models.CharField(help_text='Optional - form submissions will be emailed to this address', max_length=255, blank=True)),
                ('from_address', models.CharField(max_length=255, blank=True)),
                ('subject', models.CharField(max_length=255, blank=True)),
                ('intro', wagtail.wagtailcore.fields.RichTextField(blank=True)),
                ('thank_you_text', wagtail.wagtailcore.fields.RichTextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='HomePage',
            fields=[
                ('page_ptr', models.OneToOneField(to='wagtailcore.Page', auto_created=True, primary_key=True, parent_link=True, serialize=False)),
                ('body', wagtail.wagtailcore.fields.RichTextField(blank=True)),
            ],
            options={
                'verbose_name': 'Homepage',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='HomePageCarouselItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('link_external', models.URLField(verbose_name='External link', blank=True)),
                ('embed_url', models.URLField(verbose_name='Embed URL', blank=True)),
                ('caption', models.CharField(max_length=255, blank=True)),
                ('image', models.ForeignKey(to='wagtailimages.Image', null=True, related_name='+', blank=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('link_document', models.ForeignKey(to='wagtaildocs.Document', null=True, related_name='+', blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HomePageRelatedLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('link_external', models.URLField(verbose_name='External link', blank=True)),
                ('title', models.CharField(help_text='Link title', max_length=255)),
                ('link_document', models.ForeignKey(to='wagtaildocs.Document', null=True, related_name='+', blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PersonPage',
            fields=[
                ('page_ptr', models.OneToOneField(to='wagtailcore.Page', auto_created=True, primary_key=True, parent_link=True, serialize=False)),
                ('telephone', models.CharField(max_length=20, blank=True)),
                ('email', models.EmailField(max_length=75, blank=True)),
                ('address_1', models.CharField(max_length=255, blank=True)),
                ('address_2', models.CharField(max_length=255, blank=True)),
                ('city', models.CharField(max_length=255, blank=True)),
                ('country', models.CharField(max_length=255, blank=True)),
                ('post_code', models.CharField(max_length=10, blank=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('intro', wagtail.wagtailcore.fields.RichTextField(blank=True)),
                ('biography', wagtail.wagtailcore.fields.RichTextField(blank=True)),
                ('feed_image', models.ForeignKey(to='wagtailimages.Image', null=True, related_name='+', blank=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('image', models.ForeignKey(to='wagtailimages.Image', null=True, related_name='+', blank=True, on_delete=django.db.models.deletion.SET_NULL)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page', models.Model),
        ),
        migrations.CreateModel(
            name='PersonPageRelatedLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('link_external', models.URLField(verbose_name='External link', blank=True)),
                ('title', models.CharField(help_text='Link title', max_length=255)),
                ('link_document', models.ForeignKey(to='wagtaildocs.Document', null=True, related_name='+', blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StandardIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(to='wagtailcore.Page', auto_created=True, primary_key=True, parent_link=True, serialize=False)),
                ('intro', wagtail.wagtailcore.fields.RichTextField(blank=True)),
                ('feed_image', models.ForeignKey(to='wagtailimages.Image', null=True, related_name='+', blank=True, on_delete=django.db.models.deletion.SET_NULL)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='StandardIndexPageRelatedLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('link_external', models.URLField(verbose_name='External link', blank=True)),
                ('title', models.CharField(help_text='Link title', max_length=255)),
                ('link_document', models.ForeignKey(to='wagtaildocs.Document', null=True, related_name='+', blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StandardPage',
            fields=[
                ('page_ptr', models.OneToOneField(to='wagtailcore.Page', auto_created=True, primary_key=True, parent_link=True, serialize=False)),
                ('intro', wagtail.wagtailcore.fields.RichTextField(blank=True)),
                ('body', wagtail.wagtailcore.fields.RichTextField(blank=True)),
                ('feed_image', models.ForeignKey(to='wagtailimages.Image', null=True, related_name='+', blank=True, on_delete=django.db.models.deletion.SET_NULL)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='StandardPageCarouselItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('link_external', models.URLField(verbose_name='External link', blank=True)),
                ('embed_url', models.URLField(verbose_name='Embed URL', blank=True)),
                ('caption', models.CharField(max_length=255, blank=True)),
                ('image', models.ForeignKey(to='wagtailimages.Image', null=True, related_name='+', blank=True, on_delete=django.db.models.deletion.SET_NULL)),
                ('link_document', models.ForeignKey(to='wagtaildocs.Document', null=True, related_name='+', blank=True)),
                ('link_page', models.ForeignKey(to='wagtailcore.Page', null=True, related_name='+', blank=True)),
                ('page', modelcluster.fields.ParentalKey(related_name='carousel_items', to='tests.StandardPage')),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StandardPageRelatedLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('sort_order', models.IntegerField(editable=False, blank=True, null=True)),
                ('link_external', models.URLField(verbose_name='External link', blank=True)),
                ('title', models.CharField(help_text='Link title', max_length=255)),
                ('link_document', models.ForeignKey(to='wagtaildocs.Document', null=True, related_name='+', blank=True)),
                ('link_page', models.ForeignKey(to='wagtailcore.Page', null=True, related_name='+', blank=True)),
                ('page', modelcluster.fields.ParentalKey(related_name='related_links', to='tests.StandardPage')),
            ],
            options={
                'abstract': False,
                'ordering': ['sort_order'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='standardindexpagerelatedlink',
            name='link_page',
            field=models.ForeignKey(to='wagtailcore.Page', null=True, related_name='+', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='standardindexpagerelatedlink',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='related_links', to='tests.StandardIndexPage'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='personpagerelatedlink',
            name='link_page',
            field=models.ForeignKey(to='wagtailcore.Page', null=True, related_name='+', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='personpagerelatedlink',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='related_links', to='tests.PersonPage'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='homepagerelatedlink',
            name='link_page',
            field=models.ForeignKey(to='wagtailcore.Page', null=True, related_name='+', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='homepagerelatedlink',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='related_links', to='tests.HomePage'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='homepagecarouselitem',
            name='link_page',
            field=models.ForeignKey(to='wagtailcore.Page', null=True, related_name='+', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='homepagecarouselitem',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='carousel_items', to='tests.HomePage'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='formfield',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='form_fields', to='tests.FormPage'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventpagespeaker',
            name='link_page',
            field=models.ForeignKey(to='wagtailcore.Page', null=True, related_name='+', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventpagespeaker',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='speakers', to='tests.EventPage'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventpagerelatedlink',
            name='link_page',
            field=models.ForeignKey(to='wagtailcore.Page', null=True, related_name='+', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventpagerelatedlink',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='related_links', to='tests.EventPage'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventpagecarouselitem',
            name='link_page',
            field=models.ForeignKey(to='wagtailcore.Page', null=True, related_name='+', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventpagecarouselitem',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='carousel_items', to='tests.EventPage'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventindexpagerelatedlink',
            name='link_page',
            field=models.ForeignKey(to='wagtailcore.Page', null=True, related_name='+', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='eventindexpagerelatedlink',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='related_links', to='tests.EventIndexPage'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='blogindexpagerelatedlink',
            name='link_page',
            field=models.ForeignKey(to='wagtailcore.Page', null=True, related_name='+', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='blogindexpagerelatedlink',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='related_links', to='tests.BlogIndexPage'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='blogentrypagerelatedlink',
            name='link_page',
            field=models.ForeignKey(to='wagtailcore.Page', null=True, related_name='+', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='blogentrypagerelatedlink',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='related_links', to='tests.BlogEntryPage'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='blogentrypagecarouselitem',
            name='link_page',
            field=models.ForeignKey(to='wagtailcore.Page', null=True, related_name='+', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='blogentrypagecarouselitem',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='carousel_items', to='tests.BlogEntryPage'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='blogentrypage',
            name='tags',
            field=modelcluster.tags.ClusterTaggableManager(through='tests.BlogEntryPageTag', verbose_name='Tags', to='taggit.Tag', help_text='A comma-separated list of tags.', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='advertplacement',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='advert_placements', to='wagtailcore.Page'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='advert',
            name='page',
            field=models.ForeignKey(to='wagtailcore.Page', null=True, related_name='adverts', blank=True),
            preserve_default=True,
        ),
    ]
