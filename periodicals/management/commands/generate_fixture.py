import json
from optparse import make_option
from datetime import datetime 
from django.core.management.base import BaseCommand, CommandError

ISSUE_YEARS = range(2000,2015)
ISSUE_PERIOD = 6
ISSUE_DEFAULT_PERIODICAL_ID = 1

class Command(BaseCommand):
    args = '<model_label>'
    help = 'Generates fixture for the given model using template. For now the only Issue model implemented'

    option_list = BaseCommand.option_list + (
        make_option('--out',
            action='store',
            dest='filename',
            type='string',
            help='Filename to save fixture. Output to stdout if no option given'),
        ) + (
        make_option('--periodical_id',
            action='store',
            dest='id',
            type='int',
            help='Periodical ID for Issues. Default is %s' % ISSUE_DEFAULT_PERIODICAL_ID),
        )
    
    def handle(self, *args, **options):
        for model_label in args:
            if model_label.lower() <> 'issue':
                raise CommandError('Only Issue model supported at the moment. Not "%s".' % model_label)
            self.stdout.write('Generating fixtures for model "%s"' % model_label)
            if options.get('id', None):
                periodical_id = options['id']
                self.stdout.write('Using periodical ID: %s.' % periodical_id)
            else:
                periodical_id = ISSUE_DEFAULT_PERIODICAL_ID
                self.stdout.write('Using default periodical ID: %s.' % periodical_id)
            volume = 1
            issue = { 'model' : '', 'fields' : {}}
            issues = []
            for year in ISSUE_YEARS:
                for issue_num in range(1, ISSUE_PERIOD+1):
                    issue_month = issue_num * (12/ISSUE_PERIOD) - 1
                    issue['model'] = "periodicals.issue"
                    issue['fields']['issue'] = volume
                    issue['fields']['volume'] = issue_num
                    issue['fields']['pub_date'] = datetime(year, issue_month, 1).isoformat()
                    
                    now = datetime.now()
                    r =now.isoformat()
                    if now.microsecond:
                        r = r[:23] + r[26:]
                    if r.endswith('+00:00'):
                        r = r[:-6] + 'Z'

                    issue['fields']['created'] = issue['fields']['modified'] = r 
                    issue['fields']['periodical'] = periodical_id 
                    issue['fields']['slug'] = "%s-%s" % (issue_num, volume)
                    issues.append(issue)
                    volume = volume + 1 
                    issue = {'model' : '', 'fields' : {}}
            break
        else:
            raise CommandError('No model specified.')
        if options.get('filename', None):
                filename = options['filename']
                self.stdout.write('Store data in the file "%s".' % filename)
                fp = open(filename, "w")
                json.dump(issues, fp, indent=4)
                fp.close()
        else:
            self.stdout.write('Output data to stdout.')
            self.stdout.write(json.dumps(issues, indent=4))    