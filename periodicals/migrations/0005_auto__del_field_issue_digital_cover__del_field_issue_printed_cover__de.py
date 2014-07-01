# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Issue.digital_cover'
        db.delete_column(u'periodicals_issue', 'digital_cover')

        # Deleting field 'Issue.printed_cover'
        db.delete_column(u'periodicals_issue', 'printed_cover')

        # Deleting field 'Article.image'
        db.delete_column(u'periodicals_article', 'image')

        # Deleting field 'Article.tags'
        db.delete_column(u'periodicals_article', 'tags')


        # Changing field 'Article.content'
        db.alter_column(u'periodicals_article', 'content', self.gf('djangocms_text_ckeditor.fields.HTMLField')())
        # Deleting field 'Periodical.logo'
        db.delete_column(u'periodicals_periodical', 'logo')


    def backwards(self, orm):
        # Adding field 'Issue.digital_cover'
        db.add_column(u'periodicals_issue', 'digital_cover',
                      self.gf('django.db.models.fields.files.ImageField')(default='', max_length=200, blank=True),
                      keep_default=False)

        # Adding field 'Issue.printed_cover'
        db.add_column(u'periodicals_issue', 'printed_cover',
                      self.gf('django.db.models.fields.files.ImageField')(default='', max_length=200, blank=True),
                      keep_default=False)

        # Adding field 'Article.image'
        db.add_column(u'periodicals_article', 'image',
                      self.gf('django.db.models.fields.files.ImageField')(default='', max_length=200, blank=True),
                      keep_default=False)

        # Adding field 'Article.tags'
        db.add_column(u'periodicals_article', 'tags',
                      self.gf('tagging.fields.TagField')(default=''),
                      keep_default=False)


        # Changing field 'Article.content'
        db.alter_column(u'periodicals_article', 'content', self.gf('django.db.models.fields.TextField')())
        # Adding field 'Periodical.logo'
        db.add_column(u'periodicals_periodical', 'logo',
                      self.gf('django.db.models.fields.files.ImageField')(default='', max_length=200, blank=True),
                      keep_default=False)


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'periodicals.article': {
            'Meta': {'ordering': "[u'issue', u'page']", 'object_name': 'Article'},
            'announce': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'articles'", 'symmetrical': 'False', 'to': u"orm['periodicals.Author']"}),
            'buy_digital': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'buy_print': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'content': ('djangocms_text_ckeditor.fields.HTMLField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'articles'", 'to': u"orm['periodicals.Issue']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'page': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'read_online': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['periodicals.Series']", 'null': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '200', 'populate_from': "u'title'", 'unique_with': '()', 'blank': 'True'}),
            'subtitle': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'periodicals.author': {
            'Meta': {'ordering': "(u'last_name', u'first_name')", 'unique_together': "((u'title', u'first_name', u'middle_name', u'last_name', u'postnomial'),)", 'object_name': 'Author'},
            'alt_website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'blog': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'postnomial': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '200'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'periodicals.issue': {
            'Meta': {'ordering': "(u'-pub_date',)", 'unique_together': "((u'periodical', u'volume', u'issue', u'slug'),)", 'object_name': 'Issue'},
            'buy_digital': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'buy_print': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'periodical': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['periodicals.Periodical']"}),
            'pub_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'read_online': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '200', 'populate_from': "u'display_name'", 'unique_with': '()', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'volume': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'periodicals.linkitem': {
            'Meta': {'ordering': "[u'title']", 'object_name': 'LinkItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'S'", 'max_length': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'periodicals.periodical': {
            'Meta': {'object_name': 'Periodical'},
            'address_1': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'address_2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'blog': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'publisher': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '200'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        u'periodicals.series': {
            'Meta': {'object_name': 'Series'},
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'numchild': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['periodicals']