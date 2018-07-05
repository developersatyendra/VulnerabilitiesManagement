from django import forms
from services.models import ServiceModel
from hosts.models import HostModel
from .models import VulnerabilityModel
from scans.models import ScanTaskModel


LEVEL_RISK = (
    (0, "Informational"),
    (1, "Low"),
    (2, "Medium"),
    (3, "High"),
)


class VulnForm(forms.Form):
    levelRisk = forms.ChoiceField(
        choices=LEVEL_RISK,
        widget=forms.RadioSelect,
        label='Level Risk',
        initial=0,
    )
    scanTask = forms.ModelChoiceField(
        queryset=ScanTaskModel.objects.all().order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Scan Task',
        help_text='Scan Task',
        empty_label='None',
        initial=0

    )
    summary = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Summary'}),
        label='Summary',
        help_text='Summary of Vulnerability',
    )
    hostScanned = forms.ModelChoiceField(
        queryset=HostModel.objects.all().order_by('ipAdr'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Host Scanned',
        help_text='Host Scanned',
        empty_label='None',
        initial=0
    )
    service = forms.ModelChoiceField(
        queryset=ServiceModel.objects.all().order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Service',
        help_text='Service',
        empty_label='None',
        initial=0
    )
    description = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Description'}),
        label='Description',
        help_text='Description of Vulnerability',
    )

    def save(self, commit=True):
        if self.is_valid():
            scanTask = ScanTaskModel.objects.get(name=self.data['scanTask'])
            hostScanned = HostModel.objects.get(pk=self.data['hostScanned'])
            service = ServiceModel.objects.get(pk=self.data['service'])
            vulnObj = VulnerabilityModel()
            vulnObj.levelRisk = self.data['levelRisk']
            vulnObj.summary = self.data['summary']
            vulnObj.description = self.data['description']
            vulnObj.scanTask = scanTask
            vulnObj.hostScanned = hostScanned
            vulnObj.service = service
            if commit==True:
                vulnObj.save()
                return vulnObj
            return vulnObj
        else:
            return -1


class VulnFormValidate(forms.ModelForm):
    class Meta:
        model = VulnerabilityModel
        exclude = ('createBy', 'scanTask', 'scanTask_id')


class VulnIDForm(forms.ModelForm):
    class Meta:
        model = VulnerabilityModel
        fields = ['id']