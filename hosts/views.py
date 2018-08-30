from django.shortcuts import render
from django.views.generic import TemplateView
from dashboard.views import RenderSideBar
from .forms import HostForm

PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


class HostsView(TemplateView):
    template = 'hosts.html'

    def get(self, request, *args, **kwargs):
        form = HostForm()
        formEdit = HostForm(id='edit')
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
            'formEdit': formEdit,
        }
        return render(request, self.template, context)


class HostDetailView(TemplateView):
    template = 'host_detailed.html'

    def get(self, request, *args, **kwargs):
        form = HostForm()
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
        }
        return render(request, self.template, context)
