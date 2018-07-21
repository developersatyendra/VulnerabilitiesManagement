from django import forms
from .models import ScanTaskModel
from projects.models import ScanProjectModel


# class ScanForm(forms.Form):
#     name = forms.CharField(
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
#         label='Name',
#         help_text='Name of Scanning Task',
#         required=True,
#     )
#     isProcessed = forms.BooleanField(
#         widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         label='Is Processed',
#         help_text='If this task is processed',
#         initial=True,
#         required=False
#     )
#
#     startTime = forms.DateTimeField(
#         input_formats=["%Y-%m-%dT%H:%M"],
#         widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
#         label="Start Time",
#         help_text="Start time of this task",
#     )
#     endTime = forms.DateTimeField(
#         input_formats=["%Y-%m-%dT%H:%M"],
#         widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
#         label="Finished Time",
#         help_text="Finished time of this task"
#     )
#     fileAttachment = forms.FileField(
#         widget=forms.FileInput(),
#         label="File attachment",
#         help_text="File attachment",
#         required=False,
#     )
#     scanProject = forms.ModelChoiceField(
#         queryset=ScanProjectModel.objects.all().order_by('name'),
#         widget=forms.Select(attrs={'class': 'form-control'}),
#         label='Scan Project',
#         help_text='Scan Project',
#         empty_label='None',
#         initial=0
#     )
#     description = forms.CharField(
#         widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows':'5'}),
#         label='Description',
#         help_text='Description of Vulnerability',
#         required=False,
#     )
#
#     def __init__(self, *args, **kwargs):
#         if 'id' in kwargs:
#             id = kwargs['id']
#             del kwargs['id']
#             super().__init__(*args, **kwargs)
#             for field in self.fields:
#                 fieldID = 'id_' + field + '_' + id
#                 self.fields[field].widget.attrs['id'] = fieldID
#         else:
#             super().__init__(*args, **kwargs)
#
#     def save(self, commit=True, instance=None):
#         if self.is_valid():
#             scanProject = ScanProjectModel.objects.get(id=self.data['scanProject'])
#             name = self.data['name']
#             if 'isProcessed' in self.data:
#                 if self.data['isProcessed'] is not True and self.data['isProcessed']=='on':
#                     isProcessed = True
#             else:
#                 isProcessed = False
#             startTime = self.data['startTime']
#             endTime = self.data['endTime']
#             # fileAttachment = self.data['fileAttachment']
#             description = self.data['description']
#             if instance is None:
#                 instance = ScanTaskModel()
#             instance.name = name
#             instance.isProcessed = isProcessed
#             instance.startTime = startTime
#             instance.endTime = endTime
#             # instance.fileAttachment = fileAttachment
#             instance.scanProject = scanProject
#             instance.description = description
#             if commit == True:
#                 instance.save()
#             return instance
#         else:
#             return -1


class ScanForm(forms.ModelForm):
    startTime = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"],
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        label="Start Time",
        help_text="Start time of this task",
    )
    endTime = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"],
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        label="Finished Time",
        help_text="Finished time of this task",
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
