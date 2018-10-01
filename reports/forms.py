from django import forms
from .models import ReportModel
from hosts.models import HostModel


class ReportForm(forms.ModelForm):
    host = forms.ModelChoiceField(HostModel.objects.order_by('hostName'),widget = forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model = ReportModel
        exclude = ('createBy',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'scanProject': forms.Select(attrs={'class': 'form-control'}),
            'scanTask': forms.Select(attrs={'class': 'form-control'}),
            'host': forms.Select(attrs={'class': 'form-control'}),
            'format': forms.Select(attrs={'class': 'form-control'}),
        }


class ReportIDForm(forms.ModelForm):
    class Meta:
        model = ReportModel
        fields= ['id']
