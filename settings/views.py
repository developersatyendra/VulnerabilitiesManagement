from django.shortcuts import render
from django.views.generic import TemplateView
from dashboard.views import RenderSideBar
from accounts.forms import *
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required


class SettingsView(TemplateView):
    def get(self, request, *args, **kwargs):
        sidebarHtml = RenderSideBar(request)
        context = {'sidebar': sidebarHtml}
        return render(request, 'dashboard/dashboard.html', context)


class MyAccountView(TemplateView):
    template = 'settings/settings_myaccount.html'

    def get(self, request, *args, **kwargs):
        sidebarHtml = RenderSideBar(request)
        form = AccountInfoForm()
        formChangePassword = CustomChangePasswordForm(User.objects.get(username=request.user))
        context = {'sidebar': sidebarHtml, 'form': form, 'formChangePassword':formChangePassword}
        return render(request, self.template, context)


class AccountManagementView(TemplateView):
    template = 'settings/settings_accountmanagement.html'

    @method_decorator(permission_required(['user.can_view_user','user.can_add_user', 'user.can_change_user'], raise_exception=True))
    def get(self, request, *args, **kwargs):
        addUserForm = AccountCreationForm()
        editUserForm = AccountEditForm(id='edit')
        resetPasswordForm = AccountResetPasswordForm(id='reset')
        sidebarHtml = RenderSideBar(request)

        context = {'sidebar': sidebarHtml,
                   'addUserForm': addUserForm,
                   'editUserForm': editUserForm,
                   'resetPasswordForm': resetPasswordForm
                   }
        return render(request, self.template, context)


class AboutView(TemplateView):
    def get(self, request, *args, **kwargs):
        sidebarHtml = RenderSideBar(request)
        context = {'sidebar': sidebarHtml}
        return render(request, 'settings/settings_about.html', context)