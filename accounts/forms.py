from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import password_validation
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.models import Group


###########################################
#   Change My Password
#

class CustomChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus': True, 'class': 'form-control', 'placeholder': 'Old password'}),
    )
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}),
    )


###########################################
#   My Form Information
#

class AccountInfoForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }


###########################################
#   My Form Update Information
#

class AccountUpdateMyInfoForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }


###########################################
#   Account Creation
#

class AccountCreationForm(forms.ModelForm):
    PERMS_VIEWONLY = 0
    PERMS_SUBMITTER = 1
    PERMS_MANAGER = 2

    PERMS_LEVEL = (
        (PERMS_VIEWONLY, 'View Only'),
        (PERMS_SUBMITTER, 'Submitter'),
        (PERMS_MANAGER, 'Manager')
    )
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    isActive = forms.ChoiceField(
        label=_('Status'),
        choices=(
            (0, 'Active'),
            (1, 'Deactive'),
        ),
        initial=1,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    permission = forms.ChoiceField(
        label=_("Permission"),
        choices=PERMS_LEVEL,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}),
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2


    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
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

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = self.cleaned_data["isActive"]
        groupManager = Group.objects.get(name='manager')
        groupSubmitter = Group.objects.get(name='submitter')
        if self.cleaned_data['permission'] == self.PERMS_MANAGER:
            groupManager.user_set.add(user)
            groupSubmitter.user_set.reverse(user)
        elif self.cleaned_data['permission'] == self.PERMS_SUBMITTER:
            groupSubmitter.user_set.add(user)
            groupManager.user_set.remove(user)
        groupManager.save()
        groupSubmitter.save()
        if commit:
            user.save()
        return user


###########################################
#   Account Edit Form
#

class AccountEditForm(forms.ModelForm):
    PERMS_VIEWONLY = 0
    PERMS_SUBMITTER = 1
    PERMS_MANAGER = 2

    PERMS_LEVEL = (
        (PERMS_VIEWONLY, 'View Only'),
        (PERMS_SUBMITTER, 'Submitter'),
        (PERMS_MANAGER, 'Manager')
    )
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    isActive = forms.ChoiceField(
        label=_('Status'),
        choices=(
            (0, 'Active'),
            (1, 'Deactive'),
        ),
        initial=1,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    permission = forms.ChoiceField(
        label=_("Permission"),
        choices=PERMS_LEVEL,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username', 'readonly':True}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
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

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = self.cleaned_data["isActive"]
        groupManager = Group.objects.get(name='manager')
        groupSubmitter = Group.objects.get(name='submitter')
        if self.cleaned_data['permission'] == self.PERMS_MANAGER:
            groupManager.user_set.add(user)
            groupSubmitter.user_set.reverse(user)
        elif self.cleaned_data['permission'] == self.PERMS_SUBMITTER:
            groupSubmitter.user_set.add(user)
            groupManager.user_set.remove(user)
        groupManager.save()
        groupSubmitter.save()
        if commit:
            user.save()
        return user


###########################################
#   Account Reset password Form
#

class AccountResetPasswordForm(forms.Form):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}),
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

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