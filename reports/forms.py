from django import forms
from .models import ReportModel
from hosts.models import HostModel
from scans.models import ScanTaskModel
from projects.models import ScanProjectModel


class ReportForm(forms.ModelForm):
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


class ReportFormHost(forms.ModelForm):
    host = forms.ModelChoiceField(HostModel.objects.order_by('hostName'), widget=forms.Select(attrs={'class': 'form-control'}), required=True)
    class Meta:
        model = ReportModel
        exclude = ('createBy', 'scanProject', 'scanTask')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'host': forms.Select(attrs={'class': 'form-control'}),
            'format': forms.Select(attrs={'class': 'form-control'}),
        }


class ReportFormScan(forms.ModelForm):
    scanTask = forms.ModelChoiceField(ScanTaskModel.objects.order_by('name'), widget = forms.Select(attrs={'class': 'form-control'}), required=True)
    class Meta:
        model = ReportModel
        exclude = ('createBy', 'host', 'scanProject')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'scanTask': forms.Select(attrs={'class': 'form-control'}),
            'format': forms.Select(attrs={'class': 'form-control'}),
        }


class ReportFormProject(forms.ModelForm):
    scanProject = forms.ModelChoiceField(ScanProjectModel.objects.order_by('name'), widget = forms.Select(attrs={'class': 'form-control'}), required=True)
    class Meta:
        model = ReportModel
        exclude = ('createBy', 'host', 'scanTask')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'scanProject': forms.Select(attrs={'class': 'form-control'}),
            'format': forms.Select(attrs={'class': 'form-control'}),
        }


class ReportIDForm(forms.ModelForm):
    class Meta:
        model = ReportModel
        fields= ['id']
