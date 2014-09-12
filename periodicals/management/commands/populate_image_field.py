import os
import json
from optparse import make_option
from datetime import date, datetime 

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings 
from django.db.models.loading import get_model
from django.forms.models import model_to_dict
from django.core.files import File
from filer.models import Image

MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')


from .settings import *

class Command(BaseCommand):
    args = '<model_label>'
    help = """Tries to populate given django-filer FilerImageField of a given model 
              with image files which filename computed via each model's instance properties
              and filename_format string (in a python meaning).
              
              By default, if no POPULATE_MODEL_EXTRA_FILTERS given for the model in the 
              settings, we just get objects.all() and iterate over. 
              
              TODO: make extra filters available via options, not settings
            """
    dry_run = False
    option_list = BaseCommand.option_list + (
                    make_option('--dry-run',
                        action='store_true',
                        dest='dry_run',
                        help="Do not store found Series in the database"),
                    ) + (
                    make_option('--filename_format',
                        action='store',
                        dest='format_str',
                        type='str',
                        help='Format string to find file. Default is %s' \
                                             % PERIODICAL_IMAGE_FILE_FORMAT),
                    ) + (
                    make_option('--image-field',
                        action='store',
                        dest='image_field',
                        type='str',
                        help='Format string to find file. Default is %s' \
                                             % PERIODICAL_IMAGE_FILE_FORMAT),
                    )

    
    def handle(self, *args, **options):
        images_created = 0
        objects_saved = 0
        if options.get('image_field', None):
            image_field = options['image_field']
        else:
           raise CommandError('No image specified.')
        if options.get('dry_run', False):
                    self.dry_run = options['dry_run']
                    self.stdout.write('We do NOT write anything in the DB because you said so') 
        for model_label in args:
            self.stdout.write('Populating "%s" field for model "%s"' % (image_field, model_label))
#                                    % (image_field, model_label))          
#             for image_field in args:
#                #if model_label.lower() <> 'issue':
#                #     raise CommandError('Only Issue model supported at the moment. Not "%s".' % model_label)
#                 self.stdout.write('Populating  field %s for model "%s"'\
#                                    % (image_field, model_label))
            if options.get('format_str', None):
                format_str = options['format_str']
                self.stdout.write('Using %s as format to calculate file names' % format_str)
            else:
                format_str = PERIODICAL_IMAGE_FILE_FORMAT
                self.stdout.write('Using default %s format to calculate file names' % format_str)
            
            self.stdout.write('Test for default: %s' \
                              % PERIODICAL_IMAGE_FILE_FORMAT.format(MEDIA_ROOT=MEDIA_ROOT,
                                                                    issue=1,
                                                                    volume='99',
                                                                    ext='jpg',
                                                                    ))
            model_opts = POPULATE_MODEL_EXTRA_FILTERS.get( model_label, {'filters':'all'})
            extra_filter = model_opts['filters']

            app_name, model_name = model_label.split('.')
            dest_model = get_model(app_name, model_name)

            if not dest_model:
                 raise CommandError('Cant load destionation model')
            else:
                self.stdout.write('"%s" model loaded.' % dest_model.__name__)
            
            if extra_filter == 'all':
                self.stdout.write('Using all model instances')
                qs = dest_model.objects.all()
            else:
                self.stdout.write('Using "%s" for extra filtering on model instances' % extra_filter)    
                qs = dest_model.objects.filter(**extra_filter)
            self.stdout.write('Found "%s" instances' % qs.count())
            user = User.objects.get(username='admin')
            if not user:
                raise CommandError('ERROR. Cant get user "%s". Django-filer wants user to save files' % username)                        
            for obj in qs:
                try:
                    getattr(obj, image_field)
                except AttributeError:
                    raise CommandError('ERROR. Cant get attr "%s" of the model %s' % (image_field, dest_model))
                filepath=''
                filename=''
                data = model_to_dict(obj)
                data['MEDIA_ROOT'] = MEDIA_ROOT
                self.stdout.write('****************** Getting values of "%s" instance ************' % obj.pk)
                
                for ext in PERIODICAL_IMAGE_FILE_EXTENSIONS:
                    data['ext'] = ext
                    filepath = format_str.format(**data)
                    filename = os.path.basename(filepath)
                    filepath_cap = os.path.join(os.path.dirname(filepath), filename.capitalize())
                    if os.path.isfile(filepath): 
                        self.stdout.write('OK. Found image file "%s"' % (filepath or filepath_cap ))
                        break
                    elif os.path.isfile(filepath_cap):
                        self.stdout.write('ERROR. "%s" not a file or couldnt be open. Try caps in filename' % filepath)
                        filepath = filepath_cap
                        break
                    else:
                        self.stdout.write('ERROR. "%s" not a file or couldnt be open. Try another extension' % filepath)
                        
                self.stdout.write('Try to get image file "%s"' % filepath)
                
                if os.path.isfile(filepath):
                    with open(filepath) as f:
                        file_obj = File(f, name=filename)
                        if file_obj:
                            if not self.dry_run:
                                self.stdout.write('Try to make Image from file "%s"' % filepath)
                                image = Image.objects.create(owner=user,
                                                         original_filename=filename,
                                                         file=file_obj)
                                if image:
                                    self.stdout.write('Image "%s" created' % image.__str__())
                                    images_created = images_created + 1
                                    setattr(obj, image_field, image)
                                    self.stdout.write(u'WARNING: Try to save instance "%s" with image "%s"' % (obj, image))
                                    obj.save()
                                    if getattr(obj, image_field) > 0:
                                        objects_saved = objects_saved + 1
                                        self.stdout.write('Successful')
                                        self.stdout.write('------------------------------------------------------')
                                        
                                else:
                                    self.stdout.write('ERROR. Cant create image from "%s" file' % filepath)   
                                
                            else:
                                self.stdout.write('DRY-RUN: Try to make Image from file "%s"' % filepath)
                                
                            
                        else:
                            self.stdout.write('ERROR. While opening "%s" file' % filepath)
                else:
                    self.stdout.write('ERROR. File not found or not a file "%s". Skipping' % filepath)
                    #instance = ModelName(icon=image)
                    #instance.save()
                
            self.stdout.write('Finished. Total images created: %d. Objects saved: %d' % (images_created, objects_saved))        
            break
        else:
            raise CommandError('No model specified.')