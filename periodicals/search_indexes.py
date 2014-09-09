import datetime
from haystack import indexes
from periodicals.models import Article


class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(
        document=True, use_template=True,
        #template_name='search/indexes/periodicals/item_text.txt',
        )
    title = indexes.CharField(null=True, faceted=False, model_attr='title')
    subtitle = indexes.CharField(null=True, faceted=False, model_attr='subtitle')
    pub_date = indexes.DateTimeField(model_attr='issue__pub_date')
    series = indexes.CharField(null=True, faceted=True)
    authors = indexes.MultiValueField(null=True, faceted=True)
    organization = indexes.CharField(null=True, faceted=True, model_attr='organization')
    issue = indexes.CharField(null=True, faceted=True)
    year = indexes.CharField(null=True, faceted=True)
    # pregenerate the search result HTML for an Article
    # this avoids any database hits when results are processed
    # at the cost of storing all the data in the Haystack index
    #result_text = indexes.CharField(indexed=False, use_template=True)
    # Spelling suggestions
    suggestions = indexes.FacetCharField()
        
    def get_model(self):
        return Article

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(issue__pub_date__lte=datetime.datetime.now())
    
    def prepare_authors(self, obj):
        authors = obj.authors.all()
        if len(authors) > 0:
            return [a.get_name_display() for a in authors]
    
    def prepare_series(self, obj):
        return obj.series.full_name
    
    def prepare_issue(self, obj):
        return "%s %s" % (obj.issue.display_name(), obj.issue.display_year())
    
    def prepare_year(self, obj):
        return obj.issue.display_year()
    
    def prepare(self, obj):
        prepared_data = super(ArticleIndex, self).prepare(obj)

        # We use Haystack's dynamic fields to ensure that the title field used
        # for sorting is of type "string'.
        prepared_data['title_s'] = prepared_data['title']

        # Use title to for spelling suggestions
        prepared_data['suggestions'] = prepared_data['text']

        return prepared_data