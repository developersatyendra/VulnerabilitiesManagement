from django import forms
from .models import ScanProjectModel


class ProjectForm(forms.ModelForm):
    class Meta:
        model = ScanProjectModel
        exclude = ('createBy',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
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


class ProjectIDForm(forms.ModelForm):
    class Meta:
        model = ScanProjectModel
        fields= ['id']
