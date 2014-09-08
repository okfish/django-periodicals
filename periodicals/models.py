# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import os
from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.template.defaultfilters import slugify
from django.template.defaultfilters import date as _date
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.forms.models import model_to_dict

from autoslug.fields import AutoSlugField
from filer.fields.image import FilerImageField, FilerFileField
from djangocms_text_ckeditor.fields import HTMLField
from treebeard.mp_tree import MP_Node

try:
    # use tagging_autocomplete if it is installed
    from tagging_autocomplete.models import TagAutocompleteField as TagField
except ImportError:
    from tagging.fields import TagField

settings.PERIODICALS_AUTHOR_FORMAT = \
    getattr(settings, "PERIODICALS_AUTHOR_FORMAT",
            "%(last_name)s, %(first_name)s %(middle_name)s %(postnomial)s")

settings.PERIODICALS_AUTHOR_SLUG_FORMAT = \
    getattr(settings, "PERIODICALS_AUTHOR_SLUG_FORMAT",
            "%(last_name)s %(first_name)s %(middle_name)s %(postnomial)s")

settings.PERIODICALS_PERIODICAL_FORMAT = \
    getattr(settings, "PERIODICALS_PERIODICAL_FORMAT", "%(name)s")

settings.PERIODICALS_PERIODICAL_SLUG_FORMAT = \
    getattr(settings, "PERIODICALS_PERIODICAL_SLUG_FORMAT", "%(name)s")

settings.PERIODICALS_ISSUE_FORMAT = \
    getattr(settings, "PERIODICALS_ISSUE_FORMAT",
            "Vol. %(volume)s No. %(issue)s")

settings.PERIODICALS_ISSUE_SLUG_FORMAT = \
    getattr(settings, "PERIODICALS_ISSUE_SLUG_FORMAT", "%(volume)s %(issue)s")


STATUS_SUBMITTED = 'S'
STATUS_ACTIVE = 'A'
STATUS_DELETED = 'D'
STATUS_DRAFT = 'F'
STATUS_HIDDEN = 'H'
STATUS_PREPRINT = 'P'
STATUS_ANNOUNCED = 'N'
STATUS_PUBLISHED = 'U'

LINK_STATUS_CHOICES = (
    (STATUS_SUBMITTED, _('Submitted')),
    (STATUS_ACTIVE, _('Active')),
    (STATUS_DELETED, _('Deleted')),
)


ARTICLE_STATUS_CHOICES = (
    (STATUS_DRAFT, _('Draft')),
    (STATUS_HIDDEN, _('Hidden')),
    (STATUS_ANNOUNCED, _('Announced')),
    (STATUS_PUBLISHED, _('Published')),
)

ISSUE_STATUS_CHOICES = (
    (STATUS_DRAFT, _('Draft')),
    (STATUS_PREPRINT, _('Preprint')),
    (STATUS_PUBLISHED, _('Published')),
)

class ActiveLinkManager(models.Manager):
    def get_query_set(self):
        return super(ActiveLinkManager, self).get_query_set().\
            filter(status=self.model.STATUS_ACTIVE)


class LinkItem(models.Model):
    """
    LinkItem is a link to another article that refers to an Issue or Article.
    Used when someone external to the publisher writes a blog post
    or other online article that refers to or expands upon the original
    Issue or Article. The 'status' controls whether or not the link is
    displayed on the web page.
    """
    STATUS_SUBMITTED = 'S'
    STATUS_ACTIVE = 'A'
    STATUS_DELETED = 'D'
    STATUS_CHOICES = (
        (STATUS_SUBMITTED, _('Submitted')),
        (STATUS_ACTIVE, _('Active')),
        (STATUS_DELETED, _('Deleted')),
    )

    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'))
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    status = models.CharField(verbose_name=_('status'),
                              max_length=1,
                              choices=STATUS_CHOICES,
                              default=STATUS_SUBMITTED)

    url = models.URLField(_("url"), blank=True)
    title = models.CharField(_("title"), max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date created'))
    modified = models.DateTimeField(auto_now=True, verbose_name=_('Date modified'))

    # Define first so admin shows all regardless of status
    objects = models.Manager()
    active = ActiveLinkManager()

    class Meta:
        ordering = ['title']
        verbose_name = _('link item')
        verbose_name_plural = _('link items')

    def __unicode__(self):
        return self.title


class Author(models.Model):
    """
    The author of an Article.
    """
    TITLE_CHOICES = (
        ('MR', _('Mr.')),
        ('MRS', _('Mrs.')),
        ('MS', _('Ms.')),
        ('DR', _('Dr.')),
        )
    title = models.CharField(_("title"),
                             max_length=3,
                             choices=TITLE_CHOICES,
                             blank=True)
    first_name = models.CharField(_("first name"),
                                  max_length=100)
    middle_name = models.CharField(_("middle name"),
                                   max_length=100,
                                   blank=True)
    last_name = models.CharField(_("last name"),
                                 max_length=100)
    postnomial = models.CharField(_("postnomial"),
                                  max_length=200,
                                  blank=True,
                                  help_text=_("i.e. PhD, DVM"))
    user = models.OneToOneField(User,
                                unique=True,
                                null=True,
                                blank=True,
                                verbose_name=_('user'),
                                related_name='author_profile',
                                help_text=_("Link to the existing username or create a new one"))
    website = models.URLField(_("website"),
                              blank=True)
    alt_website = models.URLField(_("website"),
                                  blank=True,
                                  help_text=_("Alternate website for this author"))
    blog = models.URLField(_("blog"), blank=True)
    email = models.EmailField(_("email"), blank=True)
    slug = models.SlugField(_("slug"), max_length=200, unique=True)
    modified = models.DateTimeField(auto_now=True, verbose_name=_('Date modified'))
    
    image = FilerImageField(null=True, 
                            blank=True, 
                            verbose_name=_('author image'),
                            related_name='author_images',
                            help_text=_('Choose or upload your portrait or other picture'))
    organization = models.CharField(_("organization"),
                                  max_length=200,
                                  blank=True,
                                  help_text=_("Current organization name (if no partner's profile linked)"))
    position = models.CharField(_("position"),
                                  max_length=200,
                                  blank=True,
                                  help_text=_("Position in the current organization"))
    comment = models.TextField(_("comment"),
                                   max_length=200,
                                   blank=True,
                                   help_text=_("Comment, e.g. for internal usage"))
    class Meta:
        verbose_name = _('author')
        verbose_name_plural = _('authors')
        unique_together = ("title",
                           "first_name",
                           "middle_name",
                           "last_name",
                           "postnomial")
        ordering = ('last_name', 'first_name')

    def __unicode__(self):
        return _(settings.PERIODICALS_AUTHOR_FORMAT) % _instanceFields(self)

    @permalink
    def get_absolute_url(self):
        return ('periodicals_author_detail', (), {'author_slug': self.slug})

    def save(self, force_insert=False, force_update=False):
        if not self.id and not self.slug:  # use the user's slug if supplied
            # don't transmogrify slug/URL on update
            self.slug = slugify(_(settings.PERIODICALS_AUTHOR_SLUG_FORMAT)
                                % _instanceFields(self))
        super(Author, self).save(force_insert, force_update)

    def display_name(self):
        if self.first_name or self.middle_name or self.postnomial:
            return _(settings.PERIODICALS_AUTHOR_FORMAT) % _instanceFields(self)
        else:
            return self.last_name  # no comma


class Periodical(models.Model):

    def logo_upload(self, filename):
        filename, file_extension = os.path.splitext(filename)
        name = self.slug.lower()
        full_path = "%s/logo%s" % (name, file_extension)
        return full_path

    name = models.CharField(_("name"), max_length=100)
    publisher = models.CharField(_("publisher"), max_length=100, blank=True)
    address_1 = models.CharField(_("address_1"), max_length=100, blank=True)
    address_2 = models.CharField(_("address_2"), max_length=100, blank=True)
    city = models.CharField(_("city"), max_length=100, blank=True)
    state = models.CharField(_("state"), max_length=100, blank=True)
    country = models.CharField(_("country"), max_length=100, blank=True)
    zipcode = models.CharField(_("zipcode"), max_length=10, blank=True)
    website = models.URLField(_("website"), blank=True)
    logo = FilerImageField(null=True, 
                           blank=True, 
                           verbose_name=_('logo image'),
                           help_text=_("Upload logo image of the periodical"))
    blog = models.URLField(_("blog"), blank=True)
    email = models.EmailField(_("email"), blank=True)
    phone = models.CharField(_("phone"), max_length=20, blank=True)
    slug = models.SlugField(_("slug"), max_length=200, unique=True)

    class Meta:
        verbose_name = _('periodical')
        verbose_name_plural = _('periodicals')

    def __unicode__(self):
        return _(settings.PERIODICALS_PERIODICAL_FORMAT) % _instanceFields(self)

    @permalink
    def get_absolute_url(self):
        return ('periodicals_periodical_detail',
                (),
                {'periodical_slug': self.slug})

    def save(self, force_insert=False, force_update=False):
        # don't transmogrify slug/URL on update
        if not self.id and not self.slug:  # use the user's slug if supplied
                self.slug = slugify(_(settings.PERIODICALS_PERIODICAL_SLUG_FORMAT) % _instanceFields(self))
        super(Periodical, self).save(force_insert, force_update)

    def display_name(self):
        return _(settings.PERIODICALS_PERIODICAL_FORMAT) % _instanceFields(self)

@python_2_unicode_compatible
class Issue(models.Model):

    def issue_upload_to(self, filename, suffix):
        filename, file_extension = os.path.splitext(filename)
        full_path = "%s/issues/%s-%s-%s%s" % (
            self.periodical.slug.lower(),
            self.display_year(),
            self.display_month() or slugify(self.title),
            suffix,
            file_extension)
        return full_path

    def issue_upload_print(self, filename):
        return self.issue_upload_to(filename, "print")

    def issue_upload_digital(self, filename):
        return self.issue_upload_to(filename, "digital")
    
    status = models.CharField(verbose_name=_('status'),
                              max_length=1,
                              choices=ISSUE_STATUS_CHOICES,
                              default=STATUS_DRAFT)
    periodical = models.ForeignKey('Periodical', verbose_name=_('periodical'))
    volume = models.PositiveIntegerField(_("volume"))
    issue = models.PositiveIntegerField(_("issue"))
    pub_date = models.DateField(default=datetime.datetime.now,  verbose_name=_('Date published'))
    title = models.CharField(_("title"),
                             max_length=100,
                             blank=True,
                             help_text=_("Title for special issues"))
    description = HTMLField(_("description"), blank=True)
    printed_cover = FilerImageField(null=True, 
                                    blank=True, 
                                    verbose_name=_('printed cover'),
                                    related_name='issue_printed_covers',
                                    help_text=_("Upload image of printed issue's cover")) 

    buy_print = models.URLField(_("buy print"),
                                blank=True,
                                help_text=_("URL to buy print issue"))
    digital_cover = FilerImageField(null=True, 
                                    blank=True, 
                                    verbose_name=_('digital cover'),
                                    related_name='issue_digital_covers',
                                    help_text=_("Upload image of digital issue's cover")) 

    buy_digital = models.URLField(_("buy digital"),
                                  blank=True,
                                  help_text=_("URL to buy digital issue"))
    read_online = models.URLField(_("read online"),
                                  blank=True,
                                  help_text=_("URL to read online issue"))
    slug = AutoSlugField(populate_from='display_name',
                 unique=True,
                 editable=True,
                 max_length=200,
                 verbose_name=_('slug'),
                 help_text=_("Automatically generated when saved"),
                 blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date created'))
    modified = models.DateTimeField(auto_now=True, verbose_name=_('Date modified'))
    links = generic.GenericRelation(LinkItem)

    class Meta:
        verbose_name = _('issue')
        verbose_name_plural = _('issues')
        unique_together = ("periodical", "volume", "issue", "slug")
        ordering = ('-pub_date',)

    def __str__(self):
        format_str ="%(periodical)s " + settings.PERIODICALS_ISSUE_FORMAT + " %(pub_date)s"
        return format_str % {'periodical' : self.periodical,
                             'volume' : self.volume,
                             'issue' : self.issue,
                             'pub_date' : _date(self.pub_date, "b. Y")}

    @permalink
    def get_absolute_url(self):
        return ('periodicals_issue_detail', (),
                {'periodical_slug': self.periodical.slug,
                 'issue_slug': self.slug,
                 })

    def save(self, force_insert=False, force_update=False):
        # slugifying in save so data imported via fixtures gets slugged
        if not self.id and not self.slug:  # use the user's slug if supplied
            if self.title:
                # special issues have titles and not volume/issues
                self.slug = slugify(self.title)
            else:
                # regular issues
                self.slug = slugify(_(settings.PERIODICALS_ISSUE_SLUG_FORMAT) % _instanceFields(self))
        super(Issue, self).save(force_insert, force_update)

    def display_name(self):
        if self.title:
            return self.title
        else:
            return _(settings.PERIODICALS_ISSUE_FORMAT) % _instanceFields(self)

    def display_date(self):
        return self.display_year() + " - " + self.display_month()

    def display_year(self):
        return self.pub_date.strftime("%Y")

    def display_month(self):
        return self.pub_date.strftime("%b")

    def active_links(self):
        return [link for link in self.links.all()
                if link.status == LinkItem.STATUS_ACTIVE]

@python_2_unicode_compatible
class Article(models.Model):


    def upload_image(self, filename):
        filename, file_extension = os.path.splitext(filename)
        periodical = self.issue.periodical.slug.lower()
        full_path = "%s/articles/%s%s" % (periodical,
                                          self.slug.lower(),
                                          file_extension)
        return full_path

    status = models.CharField(verbose_name=_('status'),
                              max_length=1,
                              choices=ARTICLE_STATUS_CHOICES,
                              default=STATUS_DRAFT)
    series = models.ForeignKey('Series', 
                               verbose_name=_("series"),
                               blank=True,
                               null=True, 
                               )
    title = models.CharField(_("title"),
                             max_length=255)
    subtitle = models.CharField(_("subtitle"),
                             max_length=255,
                             null=True,
			                 blank=True)
    description = HTMLField(_("description"), blank=True, null=True)
    announce = models.TextField(_("announce"), blank=True, null=True)
    content = HTMLField(_("content"), blank=True, null=True)
    page = models.PositiveIntegerField(_("page"),
                                       blank=True,
                                       null=True,
                                       help_text=_('Page number in the printed issue'))
    tags = TagField(verbose_name=_('tags'))
    image = FilerImageField(null=True, 
                            blank=True, 
                            verbose_name=_('article image'),
                            related_name='article_images',
                            help_text=_('Choose or upload image associated with article'))
    
    buy_print = models.URLField(_("buy print"),
                                blank=True,
                                null=True,
                                help_text=_("URL to buy print article"))
    buy_digital = models.URLField(_("buy digital"),
                                  blank=True,
                                  null=True,
                                  help_text=_("URL to buy digital article"))
    read_online = models.URLField(_("read online"),
                                  blank=True,
                                  null=True,
                                  help_text=_("URL to read online article"))
    digital_version = FilerFileField(null=True, 
                                    blank=True, 
                                    verbose_name=_('digital version'),
                                    related_name='article_digital_versions',
                                    help_text=_("Upload PDF or any downloadable format of the article"))
    issue = models.ForeignKey('Issue', related_name='articles', verbose_name=_('issue'))
    authors = models.ManyToManyField('Author', 
                                     blank=True,
                                     null=True,
                                     related_name='articles', 
                                     verbose_name=_('authors'))
    organization = models.CharField(_("organization"),
                                  max_length=255,
                                  blank=True,
                                  null=True,
                                  help_text=_("Organization or company related to the article"
                                              " in any way or has the rights on it"))
    is_commercial = models.BooleanField(_('commercial'), default=False,
                                        help_text=_('Commercial or advertising article'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date created'))
    modified = models.DateTimeField(auto_now=True, verbose_name=_('Date modified'))
    slug = AutoSlugField(max_length=200,
                         populate_from='title',
                         unique=True,
                         editable=True,
                         verbose_name=_('slug'),
                         help_text=_("Automatically generated when saved"),
                         blank=True)
    links = generic.GenericRelation(LinkItem)
    comment = models.TextField(_("comment"),
                                   blank=True,
                                   null=True,
                                   help_text=_("Comment, e.g. for internal usage"))
    class Meta:
        verbose_name = _('article')
        verbose_name_plural = _('articles')
        ordering = ['issue', 'page', ]

    def __str__(self):
        # may only have a series name and not a title
        title = self.title
        return ("%s" % self.issue) + (title and ' - ' + title or '')

    @permalink
    def get_absolute_url(self):
        return ('periodicals_article_detail', (),
                {'periodical_slug': self.issue.periodical.slug,
                 'issue_slug': self.issue.slug,
                 'article_slug': self.slug})

    def active_links(self):
        return [link for link in self.links.all()
                if link.status == LinkItem.STATUS_ACTIVE]

# Trying to introduce series as separated model
@python_2_unicode_compatible
class Series(MP_Node):
    """
    An article series. 

    Uses django-treebeard.
    """
    node_order_by = ['name', ]
    
    name = models.CharField(_('Name'), max_length=255, db_index=True)
    description = HTMLField(_("description"), blank=True)
    image = FilerImageField(null=True, 
                            blank=True, 
                            verbose_name=_('series image'),
                            related_name='series_images',
                            help_text=_('Choose or upload image associated with the series'))
    is_commercial = models.BooleanField(_('commercial'), default=False,
                                        help_text=_("""All articles in the series 
                                                    are commercial or advertising"""))
    
    _full_name_separator = ' > '
    
    class Meta:
        verbose_name = _('series')
        verbose_name_plural = _('series')

    def __str__(self):
        # may only have a series name and not a title
        return ("%s" % self.name)
    
    @property
    def full_name(self):
        anc_names = []
        separator = self._full_name_separator
        if self.is_root():
            return self.__str__()
        for anc in self.get_ancestors().values('name'):
            anc_names.append(anc['name'])
        anc_names.append(self.name)
        return separator.join(anc_names)   

# utilities
def _instanceFields(instance):
    return model_to_dict(instance,
                         fields=[field.name for field in instance._meta.fields])
