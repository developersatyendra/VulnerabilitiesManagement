from django import forms
from .models import ServiceModel


class ServiceForm(forms.ModelForm):

    class Meta:
        model = ServiceModel
        exclude = ('createBy','submitter')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service Name'}),
            'port': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Port'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descriptions', 'rows':'5'}),
        }
        labels = {
            'name': 'Service Name',
            'port': 'Port',
            'description': 'Descriptions',
        }
        help_texts = {
            'name': 'This is service name.',
            'port': 'Network port of this service.',
            'description': 'Descriptions of this service.',
        }
        error_messages = {
            'name': {
                'required': 'Service Name is required',
                'unique': 'Service with this name already exists'
            },
            'port': {
                'required': 'Port is required',
                'unique': 'Service with this network port already exists'
            },
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

class ServiceIDForm(forms.ModelForm):
    class Meta:
        model = ServiceModel
        fields = ['id']
