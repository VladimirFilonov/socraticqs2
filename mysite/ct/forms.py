from django import forms
from ct.models import Response, Course, Unit, Concept, Lesson, ConceptLink, STATUS_CHOICES
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
## from crispy_forms.bootstrap import StrictButton


class ResponseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ResponseForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-responseForm'
        self.helper.form_class = 'form-vertical'
        self.helper.add_input(Submit('submit', 'Save'))
    class Meta:
        model = Response
        fields = ['text', 'confidence']
        labels = dict(text=_('Your answer'))

class SelfAssessForm(forms.Form):
    selfeval = forms.ChoiceField(choices=(('', '----'),) + Response.EVAL_CHOICES)
    status = forms.ChoiceField(choices=(('', '----'),) + STATUS_CHOICES)
    emlist = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                       required=False)


class ResponseListForm(forms.Form):
    ndisplay = forms.ChoiceField(choices=(('25', '25'), ('50', '50'),
                                          ('100', '100')))
    sortOrder = forms.ChoiceField(choices=(('-atime', 'Most recent first'),
                                           ('atime', 'Least recent first'),
                                           ('-confidence', 'Most confident first'),
                                           ('confidence', 'Least confident first'))) 

class UnitTitleForm(forms.ModelForm):
    submitLabel = 'Update'
    def __init__(self, *args, **kwargs):
        super(UnitTitleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-unitTitleForm'
        self.helper.form_class = 'form-vertical'
        self.helper.add_input(Submit('submit', self.submitLabel))
    class Meta:
        model = Unit
        fields = ['title']

class NewUnitTitleForm(UnitTitleForm):
    submitLabel = 'Add'

class CourseTitleForm(forms.ModelForm):
    submitLabel = 'Update'
    def __init__(self, *args, **kwargs):
        super(CourseTitleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-courseTitleForm'
        self.helper.form_class = 'form-vertical'
        self.helper.add_input(Submit('submit', self.submitLabel))
    class Meta:
        model = Course
        fields = ['title', 'access']

class NewCourseTitleForm(CourseTitleForm):
    submitLabel = 'Add'

class ConceptForm(forms.ModelForm):
    submitLabel = 'Update'
    def __init__(self, *args, **kwargs):
        super(ConceptForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-conceptForm'
        self.helper.form_class = 'form-vertical'
        self.helper.add_input(Submit('submit', self.submitLabel))
    class Meta:
        model = Concept
        fields = ['title', 'description']

class NewConceptForm(ConceptForm):
    submitLabel = 'Add'

class ConceptSearchForm(forms.Form):
    search = forms.CharField(label='Search for concepts containing')

class ConceptLinkForm(forms.ModelForm):
    submitLabel = 'Update'
    def __init__(self, *args, **kwargs):
        super(ConceptLinkForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-conceptLinkForm'
        self.helper.form_class = 'form-vertical'
        self.helper.add_input(Submit('submit', self.submitLabel))
    class Meta:
        model = ConceptLink
        fields = ['relationship']

class LessonForm(forms.ModelForm):
    submitLabel = 'Update'
    url = forms.CharField(required=False)
    def __init__(self, *args, **kwargs):
        super(LessonForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-lessonForm'
        self.helper.form_class = 'form-vertical'
        self.helper.add_input(Submit('submit', self.submitLabel))
    class Meta:
        model = Lesson
        fields = ['title', 'kind', 'text', 'medium', 'url', 'changeLog']
        labels = dict(kind=_('Lesson Type'), medium=_('Delivery medium'),
                      changeLog=_('Comment on your revisions'))

class NewLessonForm(LessonForm):
    submitLabel = 'Add'

class LessonSearchForm(forms.Form):
    ## def __init__(self, *args, **kwargs):
    ##     super(LessonSearchForm, self).__init__(*args, **kwargs)
    ##     self.helper = FormHelper(self)
    ##     self.helper.form_id = 'id-lessonSearchForm'
    ##     self.helper.form_method = 'get'
    ##     self.helper.form_class = 'form-inline'
    ##     self.helper.field_template = 'bootstrap3/layout/inline_field.html'
    ##     self.helper.add_input(StrictButton('Search', css_class='btn-default'))
    sourceDB = forms.ChoiceField(choices=(('wikipedia', 'Wikipedia'),),
                                 label='Search Courselets.org and')
    search = forms.CharField(label='for material containing')
    

