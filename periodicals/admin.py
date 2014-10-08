# -*- coding: utf-8 -*-
import urllib
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.contrib import admin
from django.contrib.contenttypes import generic
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.forms import TypedChoiceField
from django.shortcuts import render 
from django.http import HttpResponseRedirect

from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from modeltranslation.admin import TranslationAdmin, TabbedExternalJqueryTranslationAdmin

from .models import Author, Periodical, Issue, Article, Series, LinkItem, ARTICLE_STATUS_CHOICES
from .forms import ArticleCreateUpdateForm, ChangeStatusForm, ChangeSeriesForm, MergeSeriesForm

# as there is no GET queries support in the reverse function of Django
# the build_url picked from http://stackoverflow.com/a/13163095 
def build_url(*args, **kwargs):
    """
    Builds an url with get parameters passed.
    Thanks http://stackoverflow.com/a/13163095
    """
    get = kwargs.pop('get', {})
    url = reverse(*args, **kwargs)
    if get:
        url += '?' + urllib.urlencode(get)
    return url

class AuthorAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':
                           ('last_name',
                            'first_name',
                            'middle_name',
                            'postnomial')}
    list_display = ('last_name',
                    'first_name',
                    'middle_name',
                    'email',
                    'website',
                    'blog',
                    'alt_website')
    fields = ('user',
              'email',
              'image',
              ('first_name','middle_name','last_name',),
              'postnomial',
              ('website', 'alt_website', 'blog',),
              ('organization','position',),
              'comment',
              'slug',)
    ordering = ('last_name', 'first_name')
    search_fields = ['last_name']
    save_on_top = True


class PeriodicalAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    save_on_top = True


class LinkItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'url', 'created')
    list_filter = ('status',)
    search_fields = ('title', 'url')
    save_on_top = True


class LinkItemInline(generic.GenericTabularInline):
    model = LinkItem


class IssueAdmin(admin.ModelAdmin):
    list_display = ('digital_cover', 'periodical', 'pub_date', 'title', 'volume', 'issue')
    ordering = ('-pub_date',)
    search_fields = ['title', 'description', 'pub_date']
    save_on_top = True
    inlines = [
        LinkItemInline
    ]


class ArticleAdmin(TabbedExternalJqueryTranslationAdmin):
    form = ArticleCreateUpdateForm
    list_display = ('id', 'title', 'issue_display_name', 'series', 'organization')
    list_editable = ('title', 'organization',)
    list_filter = ('status', 'is_commercial', 'series')
    list_select_related = ('authors', 'articles' , 'issue')
    ordering = ('-issue', '-issue__volume')
    filter_vertical = ('authors', )
    search_fields = ['title', 
		    'subtitle', 
		    'description', 
		    'announce', 
		    'content',
            'organization',
		    'tags']
    save_on_top = True

    fieldsets = (
        (_('Article'), {
            'fields': (('issue','status',),
                       ('title','series',), 
                       ('subtitle','image',), 
                       'description', 
                       'content', 
                       )}),
        (_('Publication'), {
            'fields': ('announce', 
                       'authors',
                       ('organization', 'is_commercial'),
                       ('tags', 'slug'),
                       ),
            'classes': ('collapse', 'collapse-closed')}),
        (_('Extra'), {
            'fields': ('buy_print', 
                       'buy_digital',
                       'read_online',
                       'digital_version',
                       'comment',),
            'classes': ('collapse', 'collapse-closed')}),
                 )

    inlines = [
        LinkItemInline
    ]
    actions = ['change_status', 'change_series']
    
    def issue_display_name(self, inst):
        return inst.issue.display_name()
    issue_display_name.short_description = _('Issue')
    
    def change_status(modeladmin, request, queryset):
        form = None

        if 'apply' in request.POST:
            form = ChangeStatusForm(request.POST)

            if form.is_valid():
                status = form.cleaned_data['status']
                status_title = [s[1] for s in ARTICLE_STATUS_CHOICES if s[0] == status][0]
                count = 0
                for item in queryset:
                    item.status = status
                    item.save()
                    count += 1
                modeladmin.message_user(request, _(u"New status '%s' applied for %d articles.") \
                                         % (unicode(status_title), count))
                return HttpResponseRedirect(request.get_full_path())
        if not form:
            form = ChangeStatusForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

        return render(request, 'periodicals/admin/change_status.html', {'items': queryset,'form': form, 'title':_('Change articles status')})
    change_status.short_description = _("Change article status")
    
    def change_series(modeladmin, request, queryset):
        form = None

        if 'apply' in request.POST:
            form = ChangeSeriesForm(request.POST)

            if form.is_valid():
                series_id = form.cleaned_data['series']
                series = Series.objects.get(pk=series_id)
                series_title = series.full_name
                count = 0
                for item in queryset:
                    item.series = series
                    item.save()
                    count += 1
                modeladmin.message_user(request, _(u"%d articles now in the series '%s'") \
                                         % (count, unicode(series_title)))
                return HttpResponseRedirect(request.get_full_path())
        if not form:
            form = ChangeSeriesForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

        return render(request, 'periodicals/admin/change_series.html', {'items': queryset,'form': form, 'title':_('Change articles series')})
    change_series.short_description = _("Change article series")
    
        
class SeriesAdmin(TreeAdmin, TabbedExternalJqueryTranslationAdmin):
    form = movenodeform_factory(Series)
    list_display = ('name', 'articles_count')
    list_per_page = 300
    actions = [#'change_status', 
               'merge_series']
 
    def queryset(self, request):
        return Series.objects.annotate(articles_count=Count('article'))

    def articles_count(self, inst):
        return '<a href="%s">%s</a>' % (build_url("admin:periodicals_article_changelist", get={'series__id__exact' : int(inst.pk)}) , inst.articles_count)

    def merge_series(modeladmin, request, queryset):
        form = None

        if 'apply' in request.POST:
            form = MergeSeriesForm(request.POST)

            if form.is_valid():
                series_id = form.cleaned_data['series']
                series = Series.objects.get(pk=series_id)
                series_title = series.full_name
                count = 0
                articles_qs = None
                for item in queryset:
                    articles_qs = Article.objects.filter(series=item.id)
                    for article in articles_qs:
                        
                        article.series = series
                        article.save()
                        count += 1
                modeladmin.message_user(request, _(u"%d articles now in the series '%s'") \
                                         % (count, unicode(series_title)))
                return HttpResponseRedirect(request.get_full_path())
        if not form:
            selected_items = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
            form = MergeSeriesForm(initial={'_selected_action': selected_items, 
                                             'series' : selected_items[0]
                                             }
                                    )

        return render(request, 'periodicals/admin/merge_series.html', {'items': queryset,'form': form, 'title':_('Move articles to another series')})
    
    merge_series.short_description = _("Move all articles of the selected series to another one")

    articles_count.admin_order_field = 'articles_count'    
    articles_count.allow_tags = True
    articles_count.short_description = _("Articles")
 
    
admin.site.register(LinkItem, LinkItemAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Periodical, PeriodicalAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Series, SeriesAdmin)
