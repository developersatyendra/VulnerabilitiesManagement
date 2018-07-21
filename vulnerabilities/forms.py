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
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows':'5'}),
        label='Description',
        help_text='Description of Vulnerability',
    )

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

    def save(self, commit=True,instance=None):
        if self.is_valid():
            print(self.data)
            scanTask = ScanTaskModel.objects.get(pk=self.data['scanTask'])
            hostScanned = HostModel.objects.get(pk=self.data['hostScanned'])
            service = ServiceModel.objects.get(pk=self.data['service'])
            levelRisk = self.data['levelRisk']
            summary = self.data['summary']
            description = self.data['description']
            if instance is None:
                instance = VulnerabilityModel()
            instance.levelRisk = levelRisk
            instance.summary = summary
            instance.description = description
            instance.scanTask = scanTask
            instance.hostScanned = hostScanned
            instance.service = service
            if commit == True:
                instance.save()
            return instance
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