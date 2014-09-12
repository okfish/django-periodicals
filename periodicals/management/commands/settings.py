# settings for periodicals management commands
# very project-specific

ISSUE_FIRST_YEAR = 2000
ISSUE_YEARS = range(2000,2015)
ISSUE_PERIOD = 6
ISSUE_DEFAULT_PERIODICAL_ID = 1

DEFAULT_SOURCE_ENCODING = 'windows-1251'

PERIODICAL_IMAGE_FILE_EXTENSIONS = ['gif','jpg','png']
PERIODICAL_IMAGE_FILE_FORMAT = '{MEDIA_ROOT}/pics/cover_{issue:02d}.{ext}'
POPULATE_MODEL_EXTRA_FILTERS = {
                                'periodicals.issue': { 'filters' : {
                                                                    'periodical__exact' : ISSUE_DEFAULT_PERIODICAL_ID
                                                                    }
                                                      }
                                }


ORIGIN_URL = 'http://news.elteh.ru/arh/'