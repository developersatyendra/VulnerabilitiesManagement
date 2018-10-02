from django import forms
from .models import ScanTaskModel


class ScanForm(forms.ModelForm):
    startTime = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M:%S.%fZ",],
        widget=forms.TextInput(attrs={'class': 'form-control', 'type':'hidden',}),
        label="Start Time",
        help_text="Start time of this task",
        required=True,
    )
    endTime = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M:%S.%fZ",],
        widget=forms.TextInput(attrs={'class': 'form-control', 'type':'hidden',}),
        label="Finished Time",
        help_text="Finished time of this task",
        required=True,
    )

    class Meta:
        model = ScanTaskModel
        exclude = ('scanBy', 'submitter')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'isProcessed': forms.CheckboxInput(attrs={'class': 'form-check-input', 'value': 'True'}),
            'scanProject':forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descriptions', 'rows': '5'}),
            'fileAttachment': forms.FileInput(attrs={'style': "display: none;"}),
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


class ScanAddForm(forms.ModelForm):
    startTime = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M:%S.%fZ",],
        widget=forms.TextInput(attrs={'class': 'form-control', 'type':'hidden',}),
        label="Start Time",
        help_text="Start time of this task",
        required=True,
    )
    endTime = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M:%S.%fZ",],
        widget=forms.TextInput(attrs={'class': 'form-control', 'type':'hidden',}),
        label="Finished Time",
        help_text="Finished time of this task",
        required=True,
    )

    class Meta:
        model = ScanTaskModel
        exclude = ('scanBy', 'submitter', 'fileAttachment')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'isProcessed': forms.CheckboxInput(attrs={'class': 'form-check-input', 'value': 'True'}),
            'scanProject':forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descriptions', 'rows': '5'}),
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


class ScanAttachmentForm(forms.ModelForm):
    class Meta:
        model = ScanTaskModel
        fields = ['id', 'fileAttachment']
        widgets = {
            'fileAttachment': forms.FileInput(attrs={'style': "display: none;"}),
        }


class ScanIDForm(forms.ModelForm):
    class Meta:
        model = ScanTaskModel
        fields= ['id']
