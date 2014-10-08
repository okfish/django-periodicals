"""Forms for Periodicals."""

from django import forms
from django.db.models.query import QuerySet
from django.forms.models import BaseForm, BaseModelForm, ErrorList, model_to_dict
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib.admin.sites import AdminSite
#from django.forms.models import modelform_factory as django_modelform_factory
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .models import Series, Article, ARTICLE_STATUS_CHOICES

# Trying to steal some django-treebeard methods
# to generate tree-like select options   

#@staticmethod
def is_loop_safe(for_node, possible_parent):
    if for_node is not None:
        return not (
            possible_parent == for_node
            ) or (possible_parent.is_descendant_of(for_node))
    return True

#@staticmethod
def mk_indent(level):
    return '&nbsp;&nbsp;&nbsp;&nbsp;' * (level - 1)

#@classmethod
def add_subtree(for_node, node, options):
    """ Recursively build options tree. """
    if is_loop_safe(for_node, node):
        options.append(
            (node.pk,
             mark_safe(mk_indent(node.get_depth()) + str(node))))
        for subnode in node.get_children():
            add_subtree(for_node, subnode, options)

#@classmethod
def mk_dropdown_tree(model, for_node=None):
    """ Creates a tree-like list of choices """

    options = [(0, _('-- root --'))]
    for node in model.get_root_nodes():
        add_subtree(for_node, node, options)
    return options

class ArticleCreateUpdateForm(forms.ModelForm):
    
    series = forms.TypedChoiceField(required=False,
                              coerce=int,
                              label=_("series"),
                              widget=RelatedFieldWidgetWrapper(
                                                Article._meta.get_field('series').formfield().widget,
                                                Article._meta.get_field('series').rel,
                                                AdminSite(),
                                                can_add_related=True               
                                                ),
                              )
  
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None):
        opts = self._meta
        if instance is None:
            if opts.model is None:
                raise ValueError('ArticleCreateUpdateForm has no model class specified.')
        else:
            opts.model = type(instance)
            
        if instance is None:
            # if we didn't get an instance, instantiate a new one
            instance = opts.model()
            object_data = {}
            choices_for_node = None
        else:
            object_data = model_to_dict(instance, opts.fields, opts.exclude)
            #object_data.update(self._get_position_ref_node(instance))
            choices_for_node = instance.series
        self.instance = instance
        for_node = choices_for_node
        choices = mk_dropdown_tree(Series, None)
        self.declared_fields['series'].choices = choices
        self.declared_fields['series'].selected_choices = for_node
        if initial is not None:
            object_data.update(initial)
        super(BaseModelForm, self).__init__(data, files, auto_id, prefix,
                                            object_data, error_class,
                                            label_suffix, empty_permitted)

    def _clean_cleaned_data(self):
        """ get instantiated  series for article"""
        series_id = 0

        if 'series' in self.cleaned_data:
            series_id = self.cleaned_data['series']
            del self.cleaned_data['series']

        return series_id

    def _post_clean(self):
        series_id = self._clean_cleaned_data()
        if series_id:
                series = Series.objects.get(
                    pk=series_id)
        else:
            series = None
        self.instance.series = series
        super(ArticleCreateUpdateForm, self)._post_clean()

# Intermediate form for Article admin action change_status
class ChangeStatusForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    status = forms.ChoiceField(choices=ARTICLE_STATUS_CHOICES, label=_('New status'))

# Intermediate form for Article admin action change_series
class ChangeSeriesForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    series = forms.TypedChoiceField(required=True,
                              coerce=int,
                              label=_("series"),
                              widget=RelatedFieldWidgetWrapper(
                                                Article._meta.get_field('series').formfield().widget,
                                                Article._meta.get_field('series').rel,
                                                AdminSite(),
                                                can_add_related=True               
                                                ),
                              )
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
             initial=None, error_class=ErrorList, label_suffix=':',
             empty_permitted=False, instance=None):
        super(ChangeSeriesForm, self).__init__(data, files, auto_id, prefix,
                                            initial, error_class,
                                            label_suffix, empty_permitted)
        for_node = Series.get_first_root_node()
        choices = mk_dropdown_tree(Series, for_node)
        self.fields['series'].choices = choices
        self.fields['series'].selected_choices = for_node
        
# Intermediate form for Article admin action merge_series
# for the moment just inherits ChangeSeriesForm but can be extended
class MergeSeriesForm(ChangeSeriesForm):
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
             initial=None, error_class=ErrorList, label_suffix=':',
             empty_permitted=False, instance=None):
        super(MergeSeriesForm, self).__init__(data, files, auto_id, prefix,
                                            initial, error_class,
                                            label_suffix, empty_permitted)
        self.fields['series'].label = _("to the series")
    