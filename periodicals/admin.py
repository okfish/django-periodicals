# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.contenttypes import generic
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.forms import TypedChoiceField

from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory


from .models import Author, Periodical, Issue, Article, Series, LinkItem
from .forms import ArticleCreateUpdateForm

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
    list_display = ('periodical', 'pub_date', 'title', 'volume', 'issue')
    ordering = ('-pub_date',)
    search_fields = ['title', 'description', 'pub_date']
    save_on_top = True
    inlines = [
        LinkItemInline
    ]


class ArticleAdmin(admin.ModelAdmin):
    form = ArticleCreateUpdateForm
    list_display = ('issue', 'created', 'series', 'page', 'title', 'tags')
    ordering = ('-created',)
    filter_horizontal = ('authors',)
    search_fields = ['title', 
		    'subtitle', 
		    'series', 
		    'description', 
		    'announce', 
		    'content',
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

class SeriesAdmin(TreeAdmin):
        form = movenodeform_factory(Series)

admin.site.register(LinkItem, LinkItemAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Periodical, PeriodicalAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Series, SeriesAdmin)