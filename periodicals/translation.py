from modeltranslation.translator import translator, TranslationOptions
from periodicals.models import Article, Series

class ArticleTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle','announce','description', 'content')

class SeriesTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

translator.register(Article, ArticleTranslationOptions)
translator.register(Series, SeriesTranslationOptions)