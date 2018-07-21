from django import forms
from .models import HostModel


class HostForm(forms.ModelForm):

    class Meta:
        model = HostModel
        exclude = ('createBy',)
        widgets = {
            'ipAdr': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IP Address'}),
            'hostName': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Host Name'}),
            'platform': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Platform'}),
            'osName': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Operating System'}),
            'osVersion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'OS Version'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descriptions', 'rows':'5'}),
        }
        labels = {
            'ipAdr': 'IP Address',
            'hostName': 'Host Name',
            'platform': 'Platform',
            'osName': 'Operation System',
            'osVersion': 'OS Version',
            'description': 'Descriptions',
        }
        help_texts = {
            'ipAdr': 'IP Address of This Host.',
            'hostName': 'Host Name of This Host',
            'platform': 'Platform of Operating System',
            'osName': 'Name of Operation System',
            'osVersion': 'Version of Operating System',
            'description': 'Descriptions',
        }
        error_messages = {
            'ipAdr': {
                'required': 'Ip Address is required',
                'unique': 'Host with this IP address already exists'
            },
            'hostName': {
                'required': 'Hostname is required',
                'unique': 'Host with this Hostname already exists'
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

class HostIDForm(forms.ModelForm):
    class Meta:
        model = HostModel
        fields = ['id']