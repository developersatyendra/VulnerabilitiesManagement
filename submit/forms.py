from django import forms
from .models import SubmitModel
from projects.models import ScanProjectModel


class SubmitForm(forms.ModelForm):
    class Meta:
        model = SubmitModel
        fields = '__all__'
        widgets = {
            'fileSubmitted': forms.FileInput(attrs={'style':"display: none;"}),
            'scanProject':forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descriptions', 'rows':'5'}),
        }

    def __init__(self, *args, **kwargs):
        if 'id' in kwargs:
            id = kwargs['id']
            del kwargs['id']
            super().__init__(*args, **kwargs)
            for field in self.fields:
                fieldID = 'id_' + field + '_' + id
                self.fields[field].widget.attrs['id'] = fieldID
        else:
            super().__init__(*args, **kwargs)


class SubmitIDForm(forms.ModelForm):
    class Meta:
        model = SubmitModel
        fields= ['id']


class SubmitAddForm(forms.ModelForm):
    scanProject = forms.ModelChoiceField(
        queryset=ScanProjectModel.objects.all().order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Scan Task',
        help_text='Scan Task',
        empty_label='None',
        initial=0
    )
    class Meta:
        model = SubmitModel
        fields = '__all__'
        widgets = {
            'fileSubmitted': forms.FileInput(),#attrs={'style':"display: none;"}),
            'scanProject':forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descriptions', 'rows':'5'}),
        }