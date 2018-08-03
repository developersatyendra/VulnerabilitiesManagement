from django import forms
from .models import ScanTaskModel


class ScanForm(forms.ModelForm):
    startTime = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S"],
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        label="Start Time",
        help_text="Start time of this task",
        required=False,
    )
    endTime = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S"],
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        label="Finished Time",
        help_text="Finished time of this task",
        required=False,
    )

    class Meta:
        model = ScanTaskModel
        exclude = ('scanBy', 'submitter')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'isProcessed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'startTime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'endTime': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'fileAttachment': forms.FileInput(attrs={'style':"display: none;"}),
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


class ScanIDForm(forms.ModelForm):
    class Meta:
        model = ScanTaskModel
        fields= ['id']
