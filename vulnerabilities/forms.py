from django import forms
from .models import VulnerabilityModel


LEVEL_RISK = (
    (0, "Informational"),
    (1, "Low"),
    (2, "Medium"),
    (3, "High"),
)


class VulnForm(forms.ModelForm):

    class Meta:
        model = VulnerabilityModel
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descriptions', 'rows': '5'}),
            'observation': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Observation', 'rows': '5'}),
            'recommendation': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Recommendation', 'rows': '5'}),
            'cve': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CVE'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
            'levelRisk': forms.NumberInput(attrs={'step': "0.1", 'class': 'form-control', 'placeholder': 'Level Risk'}),
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


class VulnIDForm(forms.ModelForm):
    class Meta:
        model = VulnerabilityModel
        fields = ['id']