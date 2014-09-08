# -*- coding: UTF-8 -*-
import os
import re
import json
import unidecode
from optparse import make_option
from datetime import datetime 
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError

from django.utils.html import escape
from django.template.defaultfilters import slugify

from bs4 import BeautifulSoup

from periodicals.models import Series as Category
from periodicals.models import Issue, Article
from .settings import *

DIRNAME = os.getcwd()

series_cache = {}

def get_cached_series(string):
    """
     looks for cached string using simplified string as a key
     returns stored string if has or store to cache silently
    """
    errors = ''
    string_orig = string
    string = remove_trails(string)
    string = remove_separator(string)
    series, e = replace_quotes(string)
    if e: errors = e
    key = simplify_string(string)
    if key in series_cache.keys():
        string = series_cache[key]
    else:
        series_cache[key] = string
    
    if string_orig != string:
        errors = errors + "\nWarning. Found stored string '%s'. Using it instead of '%s'" % (string, string_orig)
    return string, errors 

def replace_quotes(string):
    errors = ''
    count = 0
    if not string: return string, errors
    pattern = re.compile(u'[\"]', re.UNICODE)
    count = string.count('"')
    #if count == 0: return string, errors
    if count == 1: 
        errors = "Warning. String contains the double-quote symbol,  that's not safe. Replacing with [']"
        string = pattern.sub("'", string)
    elif count == 2:
        errors = """Warning. String contains pair of double-quote symbols,  that's not safe.
                 Replacing with [&raquo; &laquo;]"""
        pattern = re.compile(u'[\"{1}]', re.UNICODE)
        string = pattern.sub(u"\u00ab", string, 1)
        string = pattern.sub(u"\u00bb", string, 1)
    elif count == 3:
        errors = """Warning. String contains THREE double-quote symbols,  that's not safe
                 and strange. Replacing with [&laquo; &laquo; &raquo;].
                 Check it manually."""
        string = pattern.sub(u"\u00ab", string, 2)
        string = pattern.sub(u"\u00bb", string, 1)
    elif count > 3:
        errors = """Error. FOUR or more double-quote symbols found. 
                    This case is not defined. Check or edit it manually"""
    return string, errors

def remove_trails(string):
    return string.strip(' :,.-\n\r\t')

def remove_spaces(string):
    pattern = re.compile('[\s\.\t\n\r]+', re.UNICODE) #all duplicated spaces and dots
    return pattern.sub(' ', string)                    #replace with single space
    
def simplify_string(string):
    string = remove_spaces(remove_trails(string))
    pattern = re.compile('[\W_]+', re.UNICODE) #all non-word chars and underscore
    string = pattern.sub('-', string)
    return string.lower()

def remove_separator(string):
    #found = 0
    #pattern = re.compile(u'[•\*]', re.UNICODE)
    
    pattern = re.compile(u'[•\*]', re.UNICODE)
    #string, found = re.subn(pattern, ' > ', string)
    string = pattern.sub('', string)
    string = remove_spaces(string)
    #string = string.replace(u'•', u'>')
    #string = string.replace(u'*', u'>')
    #string = string.replace(u' - ', u'>')
    #string = string.replace(u'. ', u'>')
    #print('Finding separator... %s' % found)
    #if not found:
        #string = string.replace(u'Марка', u'Марка >')
    #   flags = re.UNICODE | re.IGNORECASE
        #string = re.sub(re.compile(u'^марка\s', flags ), u'Марка > ', string)
    #    string = re.sub(re.compile(u'^события\s', flags), u'События > ', string)
    #    string = re.sub(re.compile(u'^новости\s', flags), u'Новости > ', string)
    #    string = re.sub(re.compile(u'^выставка\s', flags), u'Выставка > ', string)
        #string = string.replace(u'События', u'События >')
        #string = string.replace(u'Новости', u'События >')
        #string = string.replace(u'Выставка', u'События >')
    return string

def remove_garbage_chars(string):
    pattern = re.compile(u'[\s\t\n\r]+', re.UNICODE)
    string = pattern.sub(' ', string)
    
    # and replace duplicated spaces with the only
    #pattern = re.compile(u'[\s]+', re.UNICODE)
    #string = pattern.sub(' ', string)
    
    # and also add spaces after colon
    pattern = re.compile(ur':(?=[^\s])')
    string = pattern.sub(': ', string)
    
    return string

def get_html_soup(filename):
    with open(filename, 'r') as content_file:
            content = content_file.read()
            return BeautifulSoup(content, from_encoding=DEFAULT_SOURCE_ENCODING)

# Two methods below are stolen from oscar's catalogue app
# No refactoring applied so Series model should be aliased as Category

def create_from_sequence(bits):
    """
    Create categories from an iterable
    """
    if len(bits) == 1:
        # Get or create root node
        name = bits[0]
        try:
            # Category names should be unique at the depth=1
            root = Category.objects.get(depth=1, name=name)
        except Category.DoesNotExist:
            root = Category.add_root(name=name)
        except Category.MultipleObjectsReturned:
            raise ValueError((
                "There are more than one categories with name "
                "%s at depth=1") % name)
        return [root]
    else:
        parents = create_from_sequence(bits[:-1])
        parent, name = parents[-1], bits[-1]
        try:
            child = parent.get_children().get(name=name)
        except Category.DoesNotExist:
            child = parent.add_child(name=name)
        except Category.MultipleObjectsReturned:
            raise ValueError((
                "There are more than one categories with name "
                "%s which are children of %s") % (name, parent))
        parents.append(child)
        return parents


def create_from_breadcrumbs(breadcrumb_str, separator='>'):
    """
    Create categories from a breadcrumb string
    """
    category_names = [x.strip() for x in breadcrumb_str.split(separator)]
    categories = create_from_sequence(category_names)
    return categories[-1]

def save_obj_to_file(file, obj):
    fp = open(file, "w")
    json.dump(obj, fp, indent=4)
    fp.close()
    
class Command(BaseCommand):
    args = '<model_label>'
    help = "Parses raw html files and generates articles fixtures in the given folder"
    article_errors = 0
    articles_processed = 0
    articles = []
    error_log = []
    
    series_list = []
    dry_run = False
    option_list = BaseCommand.option_list + (
        make_option('--out',
            action='store',
            dest='file_out',
            type='string',
            help='Filename or folder to save fixture(s). Output to stdout if no option given'),
        ) + (
        make_option('--in',
            action='store',
            dest='file_in',
            type='string',
            help="File or folder we going to find content for the given model (path should be relative."
                 "If folder given we assume there is tree like <year>/<volume>/<article> inside"),
        ) + (
        make_option('--dry-run',
            action='store_true',
            dest='dry_run',
            help="Do not store found Series in the database"),
        )+ (
        make_option('--periodical_id',
            action='store',
            dest='id',
            type='int',
            help='Periodical ID for Issues. Default is %s' % ISSUE_DEFAULT_PERIODICAL_ID),
        )
    def slug_is_valid(self, slug):
        slugs = [ a['fields']['slug'] for a in self.articles ]
        return not slug in slugs
    def get_unique_slug(self, string):
        i = 2
        string_orig = string = slugify(unidecode.unidecode(string))[:197]
        while not self.slug_is_valid(string): 
            string = "%s-%s" % (string_orig, i)
            i = i + 1
        return string
    
    def get_article_link_tag(self, index, filename):
        link_tags = index.find_all(href=re.compile(os.path.basename(filename)))
        link_text1 = link_text2 = ''
        if len(link_tags) == 1:
            return link_tags[0]
        elif len(link_tags) == 2:
            self.stdout.write('Found 2 links in the index.')
            try:
                link_text1 = link_tags[0].text.strip(' \n\r\t')
            except AttributeError:
                self.stdout.write('Strange. First link in the index has no text for title. Trying second')
            try:
                link_text2 = link_tags[1].text.strip(' \n\r\t')
            except AttributeError:
                self.stdout.write('More strange. Second link in the index has no text for title')
                if not link_text1:
                    self.log_error(filename, "Very strange. Found 2 links in the index and no text for title. Use first link by default")
                return link_tags[0]
            if link_text1:
                return link_tags[0]
            elif link_text2:
                return link_tags[1]
            else:
                return link_tags[1]
        elif len(link_tags) > 2:
            self.stdout.write('Found 3 or more links in the index. Strange situation. Using first link')
            self.log_error(filename, "Found 3 or more links in the index. Strange situation. Using first link")
            return link_tags[0]
        else:
            self.log_error(filename, "Article link not found in the index file given")
            return None
 
    def get_cleaned_series(self, tag):
        cleaned_series = ''
        try:
            cleaned_series = tag.find('span').contents[0]
        except (AttributeError, IndexError):
            return ''
        if cleaned_series:
            self.stdout.write('Warning. Using truncated variant: "%s"' % cleaned_series)
            return cleaned_series 
            
        
    def extract_data(self, file_in_full, **kwargs):
        article = {'model' : 'periodicals.article',
                   'fields' : {
                               'issue' : '',
                               'title' : '',
                               'subtitle' : '',
                               'description' : '',
                               'announce' : '',
                               'content' : '',
                               'series' : '',
                               'created' : '',
                               'modified' : '',
                               'slug' : '',
                               'comment' : '',
                               'organization' : '',
                               'buy_print' : '',
                               'buy_digital' : '',
                               'read_online' : '',
                               'is_commercial': '',
                               }
                   }
        series = series2 = series3 = subseries = subseries2 = '' 
        series_tag = series_tag2 = series_tag3 = subseries_tag = subseries_tag2 = {}
        title = title2 = content = slug = ''
        volume = 0
        periodical_id = 0
        self.stdout.write('-------------------------------------------------------------------------')
        self.stdout.write('Processing file "%s".' % file_in_full)
        
        html = get_html_soup(file_in_full)
        #article['title'] = html.title.string.rsplit( ')', 1)[1].strip()
        
        now = datetime.now()
        r =now.isoformat()
        if now.microsecond:
            r = r[:23] + r[26:]
        if r.endswith('+00:00'):
            r = r[:-6] + 'Z'
        article['fields']['created'] = article['fields']['modified'] = r
        
        article['origin'] = file_in_full
        if 'volume' in kwargs:
            volume = kwargs['volume']
        else:
            rx = re.compile(r"\(([^)]+)\)") # take string between brackets
            volume = rx.findall(html.title.string)
        
        if volume:
            try:
                issue = Issue.objects.get(issue=volume, periodical=self.periodical_id)
            except Issue.DoesNotExist:
                self.stdout.write('Cant find Issue "%s". Create a new one manually or use generate_fixture. Skipping.' % volume)
                self.log_error(file_in_full, 'Cant find Issue "%s". Create a new one manually or use generate_fixture' % volume)
                return None
            except Issue.MultipleObjectsReturned:
                raise ValueError((
                    "There are more than one Issue with volume %s"
                    "of periodical id:%s") % (volume, periodical_id))
            if issue.pk:
                article['fields']['issue'] = issue.pk if self.dry_run else issue
            else:
                self.stdout.write('Issue key error "%s". Skipping.' % issue.pk)
                self.log_error(file_in_full, 'Issue key wrror "%s".' % issue.pk)
        
        if 'index' in kwargs:
            index = kwargs['index']
            article_link = self.get_article_link_tag(index, file_in_full)
            try:
                title_indexed = article_link.text.strip(' \n\r\t')
            except AttributeError:
                title_indexed = ""
        try:
            title = html.find('h2').contents[0]
        except (AttributeError, IndexError):
            title = ""
            
        try:
            title = title.strip(' \n\r\t')
        except TypeError:
            pass
            
        try:
            title2 = html.title.string.rsplit( ')"', 1)[1].strip(' \n\r\t')
        except (AttributeError, IndexError):
            title2 = ''
        
        try:
            content_strings = html.find('td', bgcolor="#E6E6E6", colspan=2).contents
        except AttributeError:
            content_strings = None
        try:
            content_strings2 = html.find('td', bgcolor="#E6E6E6", colspan=4).contents
        except AttributeError:
            content_strings2 = None
        try:
            content_strings3 = html.find('td', bgcolor="#E6E6E6", colspan=3).contents
        except AttributeError:
            content_strings3 = None
        
        content_strings = (content_strings or content_strings2 or content_strings3)
        if not content_strings:            
            self.log_error(file_in_full, "Cant find article content.")
            content = 'no_content_found_please_check_manually'
        else:
            content = ''.join(unicode(s) for s in content_strings).strip(' \n\r\t')
            
        article['fields']['content'] = escape(content) if self.dry_run else content
            
        if article_link:
            article_title = title_indexed or title or title2
            article_title = remove_garbage_chars(article_title)
            article['fields']['title'] = escape(article_title)
            self.stdout.write('Found title: "%s".' % article_title)
            
            table = article_link.find_parent('table')
            if table:
                series_tag = table.find('strong')
                series_tag2 = table.find(class_="top_no_indent")
                series_tag3 = table.find('span', class_="top")
            else:
                self.stdout.write('No surrounding table found. Cant find series tags')
                self.log_error(file_in_full, "No surrounding table found. Cant find series tags")
            try:
                series = escape(series_tag.text)
            except AttributeError:
                self.stdout.write('Series not found.  Only "%s". Going another way' % series)
                
            try:
                series2 = escape(series_tag2.text)
            except AttributeError:
                self.stdout.write('Series (variant 2) not found. Only "%s".' % series2)
            
            try:
                series3 = escape(series_tag3.text)
            except AttributeError:
                self.stdout.write('Series (variant 3) not found. Only "%s".' % series3)
            
            cleaned_series = ''
            if series_tag and series_tag.contents[0].name == 'a':
                self.stdout.write('Series (1 variant) contains link and this is wrong. Use second variant: "%s"' % series2)
                series = series2
            elif not series_tag and series_tag2:
                series = series2
                self.stdout.write('Series (1 variant) not found. Use second variant: "%s"' % series2)
            elif not series_tag2 and series_tag3:
                self.stdout.write('Series (2 variant) not found. Use third variant: "%s"' % series3)
                self.stdout.write('Cheking series3...')
                try:
                    cleaned_series = series_tag3.find('span', class_="eng_h").contents[0]
                except (AttributeError, IndexError):
                    self.stdout.write('Special tags not found. Seems like "%s" is wrong series. Drop it' % series3)
                    series3 = ''
                if cleaned_series: 
                    series = series_tag3.contents[0]
            if series == series2:
                series = self.get_cleaned_series(series_tag2) or series  
                
            if not series:
                self.stdout.write('Check for special case for first three articles')
                if os.path.basename(file_in_full) in ['01.php','01_1.php','01_2.php', '01_3.php', '02.php', '03.php']:
                    series = article_link.text
                    self.stdout.write('Using article link from index file as series name %s' % series)
                else:
                    series = "series_not_found"
                    self.log_error(file_in_full, "Error. Cant find article series in three way. Use default '%s'" % series)
            
            #series = remove_trails(series)
            #series = remove_separator(series)
            series, e = get_cached_series(series)
            if e: self.stdout.write(e)
            #if series != series_cached:
                #self.stdout.write("Warning. Found stored series name '%s'. Using it instead of '%s'" % (series_cached, series))
                #series = series_cached
                #self.log_error(file_in_full, "Warning. Found stored series name '%s'. Using it instead of '%s'" % (series_cached, series))
            
            
            try:
                subseries = article_link.find('strong').text
            except AttributeError:
                self.stdout.write('Subseries (0 variant) not found. Only "%s".' % subseries)
                subseries = ''
            if not subseries:    
                subseries_tag = article_link.find_previous('strong')
                try:
                    subseries = escape(subseries_tag.text)
                except AttributeError:
                    self.stdout.write('Subseries (1 variant) not found. Only "%s".' % subseries)
                    subseries = ''
            else:
                try:
                    title_indexed_2 = article_link.find('br').next_sibling
                    self.stdout.write('Subseries (0 variant) found: "%s".' % subseries)
                    self.stdout.write('Title changed from: "%s" to "%s"' % (article_title, title_indexed_2))
                    article_title = remove_trails(title_indexed_2)
                except AttributeError:
                    self.log_error(file_in_full, 'Subseries (0 variant) found but no <br> tag. Using next variant for title')
                    self.stdout.write('Subseries (0 variant) found but no <br> tag. Using next variant for title if exists')
                
                    
            subseries_tag2 = article_link.find_previous(style="color:#2e8b57")
            subseries2 = ''
            #self.stdout.write('Subseries (2 variant) before TRY "%s".' % subseries2)
            try:
                subseries2 = escape(subseries_tag2.text)
            except AttributeError:
                self.stdout.write('Subseries (2 variant) not found. Only "%s".' % subseries2)
                subseries2 = ''
            #self.stdout.write('Subseries (2 variant) after TRY "%s".' % subseries2)
            subseries = subseries or subseries2
            if subseries_tag and ('a' in [ t.name for t in subseries_tag.children ]):
                self.stdout.write('SubSeries (1 variant) contains link and this is wrong. Try to use second variant: "%s"' % subseries2)
                if subseries_tag2 and ('a' in [ t2.name for t2 in subseries_tag2.children ]):
                    self.stdout.write('SubSeries (2 variant) contains link and this is wrong. Drop it')
                    subseries = ''
                else:    
                    subseries = self.get_cleaned_series(subseries_tag2) or subseries2
            subseries = remove_separator(subseries)
            if subseries:
                #subseries = remove_trails(subseries)
                #subseries = remove_separator(subseries)
                subseries, e = get_cached_series(subseries)
                if e: self.stdout.write(e)
                #if subseries != subseries_cached:
                    #self.stdout.write("Warning. Found stored subseries name '%s'. Using it instead of '%s'" % (subseries_cached, subseries))
                    #subseries = subseries_cached
                    #self.log_error(file_in_full, "Warning. Found stored subseries name '%s'. Using it instead of '%s'" % (subseries_cached, subseries))
            
            if series == subseries:
                
                self.stdout.write("Strange! Series and subseries strings identical. Trying another variant for series")
                if series2 and subseries != series2:
                    self.log_error(file_in_full, "It's seems like another series name found. Use series2")
                    self.stdout.write("It's seems like another series name found. Use series2")
                    self.stdout.write("Changing series '%s' to: '%s'" % (series, series2))
                    series = self.get_cleaned_series(series_tag2)
                    series, e = get_cached_series(series)
                    if e: self.stdout.write(e)
                elif series3 and subseries != series3:
                    self.log_error(file_in_full, "It's seems like another series name found. Use series3")
                    self.stdout.write("It's seems like another series name found. Use series3")
                    self.stdout.write("Changing series '%s' to: '%s'" % (series, series3))
                    series = series3
                    series, e = get_cached_series(series)
                    if e: self.stdout.write(e)
                else:
                    self.stdout.write("There are no second or third variant for series. Assuming we found right one twice so use only series")
            
            # Check for special case for subseries of "Mark Equipment" which may contains Organisation
            organisation = ''
            flags = re.UNICODE | re.IGNORECASE
            if len(re.findall(re.compile(u'^Марка\sОборудование', flags ), series)) == 1:
                self.stdout.write("Warning. Found special series %s" % series)
                self.stdout.write("Looking for Organisation title...")
                
                if subseries and subseries != series:
                    self.stdout.write("Subseries is not empty. Use '%s' as Organisation name..." % subseries)
                    organisation = subseries
                    subseries = ''
                else:
                    self.stdout.write("Subseries not found. Looking for Org.name in the article title...")
                    if article_title and article_title.count(':') > 0:
                        organisation, e = get_cached_series(article_title.split(':', 1)[0])
                        if e: self.stdout.write(e)
                if organisation:
                    self.stdout.write("Saving '%s' as organisation title and mark article as commercial..." % organisation)
                    article['fields']['organization'] = organisation
                    article['fields']['is_commercial'] = True
                else:
                    self.stdout.write("No Organisation title found...")
            # Final series breadcrumb. No more futher modifications
            if (series and subseries) and (series != subseries):
                #series_main = series
                series = series + ' > ' + subseries
            
            self.series_list.append(series)
            self.stdout.write("Result series for article: '%s'" % series)
            if len(series) > 100:
                self.log_error(file_in_full, "Warning! Series string is too long (>100)")
            
            
            if article_link.next_sibling:
                if article_link.next_sibling.name == 'br' and \
                                        article_link.next_sibling.next_sibling.name in ('em', 'i'):
                    article['fields']['announce'] = unicode(article_link.next_sibling.next_sibling.string)
                else:
                    for s in article_link.next_siblings:
                        if s.name in ('strong', 'a'):
                            break
                        if s.name in ('em', 'i') or len(" ".split(s.string)) > 2:
                            article['fields']['announce'] = unicode(s.string)
                        #elif len(" ".split(s.string)) > 2:
                        #    article['fields']['announce'] = s.string
                                 
        elif title or title2:
            article['fields']['title'] = escape(title) or title2
            series = "article_not_indexed"
        else:
            self.stdout.write('Title not found.')
            self.log_error(file_in_full, "Cant find article title. Use default")
            series = "article_untitled_not_indexed"
            article['fields']['title'] = "title_not_found_%s" % self.articles_processed 
        self.articles_processed = self.articles_processed + 1
        
        self.stdout.write('Storing series "%s" in the DB.' % series)
        if not self.dry_run:
            series = create_from_breadcrumbs(series) 
            if series.pk > 0:
                article['fields']['series'] = series.pk if self.dry_run else series
            else:
                self.stdout.write('Cant find series in the DB or get a new one. It will raise an error while loading json.')
                self.log_error(file_in_full, "Cant find series in the DB or get a new one. Series: %s" % series)
        
        if len(article['fields']['title']) > 254:
            self.stdout.write('Title too looong. Should be truncated. Original stored as comment')
            self.log_error(file_in_full, "Title too looong. Should be truncated. Original stored as comment")
            article['fields']['comment'] = article['fields']['comment'] + "\nOriginal title: %s" % article['fields']['title']
            article['fields']['title'] = article['fields']['title'][:254]
        
        slug = self.get_unique_slug(article['fields']['title'])
        if slug:
            article['fields']['slug'] = slug
        else:
            self.stdout.write('Cant slugify title. It will raise an error while loading json.')
            self.log_error(file_in_full, "Cant make slug for given title")
            return False
        return article
    
    def log_error(self, key, message):
        self.article_errors = self.article_errors + 1
        self.error_log.append({key : message })
    
    def handle(self, *args, **options):
        for model_label in args:
            if model_label.lower() == 'article':
                self.stdout.write('Generating fixtures for model "%s"' % model_label)
                if options.get('file_in', None):
                    file_in = options['file_in']
                    if os.path.isabs(file_in):
                        file_in_full = file_in
                    else:
                        file_in_full = os.path.join(DIRNAME, file_in)
                    if os.path.exists(file_in_full):
                        self.stdout.write('Using "%s" for input' % file_in)
                    else:
                        raise CommandError('Seems like the given input file (%s) or folder not exists. Try again.' % file_in_full)
                else:
                    raise CommandError('No input file or folder specified. Try again.')
                if options.get('file_out', None):
                    file_out = options['file_out']
                else:
                    file_out = 'stdout'
                self.stdout.write('Using "%s" for output' % file_out)
                
                if options.get('dry_run', False):
                    self.dry_run = options['dry_run']
                    self.stdout.write('We do NOT write anything in the DB because you said so')
                
                if options.get('id', None):
                    self.periodical_id = options['id']
                    self.stdout.write('Using periodical ID: %s.' % self.periodical_id)
                else:
                    self.periodical_id = ISSUE_DEFAULT_PERIODICAL_ID
                    self.stdout.write('Using default periodical ID: %s.' % self.periodical_id)
                
                volume = 1
                self.articles = []

                if os.path.isfile(file_in_full):
                    self.stdout.write('We have a single file. Processing...')
                    article = self.extract_data(file_in_full)
                    if article:
                        self.articles.append(article)
                elif os.path.isdir(file_in_full):
                    self.stdout.write('We have a whole folder. Processing...')
                    for year in ISSUE_YEARS:
                        year_dir = os.path.join(file_in_full, "%s" % year)
                        self.stdout.write('=======================================================================')
                        self.stdout.write('YEAR: %d' % year)
                        self.stdout.write('Going to: %s' % year_dir)
                        
                        for issue_num in range(1, ISSUE_PERIOD+1):
                            issue_month = issue_num * (12/ISSUE_PERIOD) - 1
                            issue_dir = os.path.join(year_dir, "%d" % ((year-ISSUE_FIRST_YEAR)*ISSUE_PERIOD+issue_num))
                            if os.path.isdir(issue_dir):
                                self.stdout.write('*** Going to: %s ***' % issue_dir)
                                issue_index_file = os.path.join(issue_dir, "index.php")
                                issue_index_html = None
                                if os.path.isfile(issue_index_file):
                                    issue_index_html = get_html_soup(issue_index_file)
                                issue_files = [f for f in os.listdir(issue_dir) if re.match(r'^[0-9]+\S*\.php', f)]
                                self.stdout.write('Found: %(num)d articles' % { 'num':len(issue_files)+1})
                                for issue_file in issue_files:
                                    issue_file_full = os.path.join(issue_dir, issue_file)
                                    article = self.extract_data(issue_file_full, index=issue_index_html, volume=volume)
                                    if article:
                                        article['fields']['comment'] = article['fields']['comment'] + '\n' + \
                                                    "Original url: %s/%d/%d/%s" % (ORIGIN_URL, year, issue_num, issue_file )
                                        self.articles.append(article)
                            else:
                                self.stdout.write('Skipping as %s is not directory' % issue_dir)
                            
                            volume = volume + 1 
                        
                break
            else:
                raise CommandError('Only "article" model supported at the moment. Not "%s".' % model_label)
                 
        else:
            raise CommandError('No model specified.')
        
        self.stdout.write('Articles processed: %s' % self.articles_processed)
 
        if file_out != 'stdout':
            series_filename = os.path.join(os.path.dirname(file_out), "found_series_list.json")
            self.stdout.write('Store found series in the file.%s' % series_filename)
            save_obj_to_file(series_filename, self.series_list)
            
            if self.dry_run:
                if os.path.isdir(file_out):
                    self.stdout.write('Store data files in the directory "%s".' % file_out)
                    article_processed = 1
                    for article in self.articles:
                        filename = os.path.join(file_out, "%04d.json" % article_processed)
                        self.stdout.write('Saving file "%s".' % filename)
                        save_obj_to_file(filename, self.article)
                        article_processed = article_processed + 1
                else:
                    self.stdout.write('Store data in the file "%s".' % file_out)
                    save_obj_to_file(file_out, self.articles)
            else:
                # Import articles to DB
                self.stdout.write('Store data in the DB...')
                
                article_processed = 1
                for article in self.articles:
                    article_errors = ''
                    self.stdout.write('Saving article from file: "%s".' % article['origin'])
                    article_fields = article['fields']
                    article_instance = Article(**article_fields)
                    try:
                        article_instance.full_clean()
                    except ValidationError as e:
                        article_errors = e.message_dict
                    if article_errors:
                        self.stdout.write('Errors occured while validating models data "%s".' % json.dumps(article_errors, indent=4))
                        self.log_error(article['origin'], 'Errors occured while validating models data: "%s".' % json.dumps(article_errors, indent=4))
                    else:
                        self.stdout.write('Everything seems to be ok. Trying to save...')
                        try:
                            article_instance.save()
                        except UnicodeEncodeError as e:
                            article_errors = e.reason
                            error_object = e.object
                        if article_errors:
                            self.stdout.write('FAIL! Errors occured while saving models data: reason "%s", object: %s .' % (article_errors, error_object))
                            self.stdout.write('We had try to save article fields')
                            for k in article_fields.keys():
                                self.stdout.write(u'Field: "%s" \nValue: %s' % (k, article_fields[k]))
                            self.log_error(article['origin'], 'Errors occured while saving models data: "%s".' % article_errors)
                            #break
                        else:
                            self.stdout.write('OK. Seems to be saved. Checking for ID...".')
                        
                        if article_instance.id:
                            self.stdout.write('Saved OK. Article ID is: %s' % article_instance.id)
                            article_processed = article_processed + 1
                        else:
                            self.stdout.write('Something was wrong... Article saved but has not ID?')
                self.stdout.write('Articles processed: %d' % (article_processed-1))
            
        else:
            self.stdout.write('Output found series to stdout.')
            self.stdout.write(json.dumps(series_list, indent=4))
            self.stdout.write('Output data to stdout.')
            self.stdout.write(json.dumps(self.articles, indent=4))
        
        if self.article_errors:
            self.stdout.write('Found errors while parsing and saving articles: %s' % self.article_errors)
            self.stdout.write(json.dumps(self.error_log, indent=4))
            
        self.stdout.write('Done.')
        
        
            #print article
# >>> for y in range(2000,2003):
#...     for root, dirs, fnames in os.walk("fixtures/raw/arh/%s/" % y):
#...         for f in fnames:
#...             print f
# output all files year by year 

# rx = re.compile(r"\(([^)]+)\)") # take string between brackets
# rx.findall(html.title.string)

