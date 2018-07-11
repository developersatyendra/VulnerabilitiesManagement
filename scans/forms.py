from django import forms
from .models import ScanTaskModel
from projects.models import ScanProjectModel


class ScanForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
        label='Name',
        help_text='Name of Scanning Task',
        required=True,
    )
    isProcessed = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class':'form-check-input'}),
        label='Is Processed',
        help_text='If this task is processed',
        initial=True,
    )

    startTime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        label="Start Time",
        help_text="Start time of this task",
    )
    endTime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        label="Finished Time",
        help_text="Finished time of this task"
    )
    fileAttachment = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'custom-file-input'}),
        label="File attachment",
        help_text="File attachment",
    )
    scanProject = forms.ModelChoiceField(
        queryset=ScanProjectModel.objects.all().order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Scan Project',
        help_text='Scan Project',
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

    # def save(self, commit=True,instance=None):
    #     if self.is_valid():
    #         scanTask = ScanTaskModel.objects.get(name=self.data['scanTask'])
    #         hostScanned = HostModel.objects.get(pk=self.data['hostScanned'])
    #         service = ServiceModel.objects.get(pk=self.data['service'])
    #         levelRisk = self.data['levelRisk']
    #         summary = self.data['summary']
    #         description = self.data['description']
    #         if instance is None:
    #             instance = VulnerabilityModel()
    #         instance.levelRisk = levelRisk
    #         instance.summary = summary
    #         instance.description = description
    #         instance.scanTask = scanTask
    #         instance.hostScanned = hostScanned
    #         instance.service = service
    #         if commit == True:
    #             instance.save()
    #         return instance
    #     else:
    #         return -1


# class ScanIDForm(forms.ModelForm):
#     class Meta:
#         model = ScanTaskModel
#         fields = ['id']
