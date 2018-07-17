from django import forms
from .models import ServiceModel


class ServiceForm(forms.ModelForm):

    class Meta:
        model = ServiceModel
        exclude = ('createBy','submitter')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service Name'}),
            'port': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Port'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descriptions'}),
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


class ServiceIDForm(forms.ModelForm):
    class Meta:
        model = ServiceModel
        fields = ['id']
