from django.shortcuts import render
from django.views.generic import TemplateView
from dashboard.views import RenderSideBar
from .forms import HostForm

PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


class HostsView(TemplateView):
    template = 'hosts/hosts.html'

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
    template = 'hosts/host_detailed.html'

    def get(self, request, *args, **kwargs):
        form = HostForm()
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
        }
        return render(request, self.template, context)


class HostScanTaskView(TemplateView):
    template = 'hosts/host_scantask.html'

    def get(self, request, *args, **kwargs):
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
        }
        return render(request, self.template, context)


class HostCurrentVulnView(TemplateView):
    template = 'hosts/host_currentvuln.html'

    def get(self, request, *args, **kwargs):
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
        }
        return render(request, self.template, context)


class HostRunningServiceView(TemplateView):
    template = 'hosts/host_runningservice.html'

    def get(self, request, *args, **kwargs):
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
        }
        return render(request, self.template, context)

class HostStatisticsView(TemplateView):
    template = 'hosts/host_statistics.html'

    def get(self, request, *args, **kwargs):
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
        }
        return render(request, self.template, context)