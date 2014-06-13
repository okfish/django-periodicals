# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LinkItem'
        db.create_table(u'periodicals_linkitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('status', self.gf('django.db.models.fields.CharField')(default=u'S', max_length=1)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'periodicals', ['LinkItem'])

        # Adding model 'Author'
        db.create_table(u'periodicals_author', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=3, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('middle_name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('postnomial', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('alt_website', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('blog', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=200)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'periodicals', ['Author'])

        # Adding unique constraint on 'Author', fields ['title', 'first_name', 'middle_name', 'last_name', 'postnomial']
        db.create_unique(u'periodicals_author', ['title', 'first_name', 'middle_name', 'last_name', 'postnomial'])

        # Adding model 'Periodical'
        db.create_table(u'periodicals_periodical', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('publisher', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('address_1', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('address_2', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=200, blank=True)),
            ('blog', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=200)),
        ))
        db.send_create_signal(u'periodicals', ['Periodical'])

        # Adding model 'Issue'
        db.create_table(u'periodicals_issue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('periodical', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['periodicals.Periodical'])),
            ('volume', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('issue', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('pub_date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime.now)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=200, blank=True)),
            ('printed_cover', self.gf('django.db.models.fields.files.ImageField')(max_length=200, blank=True)),
            ('buy_print', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('digital_cover', self.gf('django.db.models.fields.files.ImageField')(max_length=200, blank=True)),
            ('buy_digital', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('read_online', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=200, populate_from=u'display_name', unique_with=(), blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'periodicals', ['Issue'])

        # Adding unique constraint on 'Issue', fields ['periodical', 'volume', 'issue', 'slug']
        db.create_unique(u'periodicals_issue', ['periodical_id', 'volume', 'issue', 'slug'])

        # Adding model 'Article'
        db.create_table(u'periodicals_article', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('series', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('page', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('tags', self.gf('tagging.fields.TagField')()),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=200, blank=True)),
            ('buy_print', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('buy_digital', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('read_online', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'articles', to=orm['periodicals.Issue'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=200, populate_from=u'title', unique_with=(), blank=True)),
        ))
        db.send_create_signal(u'periodicals', ['Article'])

        # Adding M2M table for field authors on 'Article'
        m2m_table_name = db.shorten_name(u'periodicals_article_authors')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('article', models.ForeignKey(orm[u'periodicals.article'], null=False)),
            ('author', models.ForeignKey(orm[u'periodicals.author'], null=False))
        ))
        db.create_unique(m2m_table_name, ['article_id', 'author_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Issue', fields ['periodical', 'volume', 'issue', 'slug']
        db.delete_unique(u'periodicals_issue', ['periodical_id', 'volume', 'issue', 'slug'])

        # Removing unique constraint on 'Author', fields ['title', 'first_name', 'middle_name', 'last_name', 'postnomial']
        db.delete_unique(u'periodicals_author', ['title', 'first_name', 'middle_name', 'last_name', 'postnomial'])

        # Deleting model 'LinkItem'
        db.delete_table(u'periodicals_linkitem')

        # Deleting model 'Author'
        db.delete_table(u'periodicals_author')

        # Deleting model 'Periodical'
        db.delete_table(u'periodicals_periodical')

        # Deleting model 'Issue'
        db.delete_table(u'periodicals_issue')

        # Deleting model 'Article'
        db.delete_table(u'periodicals_article')

        # Removing M2M table for field authors on 'Article'
        db.delete_table(db.shorten_name(u'periodicals_article_authors'))


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
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'articles'", 'symmetrical': 'False', 'to': u"orm['periodicals.Author']"}),
            'buy_digital': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'buy_print': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '200', 'blank': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'articles'", 'to': u"orm['periodicals.Issue']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'page': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'read_online': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'series': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '200', 'populate_from': "u'title'", 'unique_with': '()', 'blank': 'True'}),
            'tags': ('tagging.fields.TagField', [], {}),
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
            'digital_cover': ('django.db.models.fields.files.ImageField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'periodical': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['periodicals.Periodical']"}),
            'printed_cover': ('django.db.models.fields.files.ImageField', [], {'max_length': '200', 'blank': 'True'}),
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
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '200', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'publisher': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '200'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        }
    }

    complete_apps = ['periodicals']