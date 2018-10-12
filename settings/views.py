from django.shortcuts import render
from django.views.generic import TemplateView
from dashboard.views import RenderSideBar
from accounts.forms import AccountInfoForm, CustomChangePasswordForm
from django.contrib.auth.models import User


class SettingsView(TemplateView):
    def get(self, request, *args, **kwargs):
        sidebarHtml = RenderSideBar(request)
        context = {'sidebar': sidebarHtml}
        return render(request, 'dashboard.html', context)


class MyAccountView(TemplateView):
    template = 'settings/settings_myaccount.html'

    def get(self, request, *args, **kwargs):
        sidebarHtml = RenderSideBar(request)
        form = AccountInfoForm()
        formChangePassword = CustomChangePasswordForm(User.objects.get(username=request.user))
        context = {'sidebar': sidebarHtml, 'form': form, 'formChangePassword':formChangePassword}
        return render(request, self.template, context)
