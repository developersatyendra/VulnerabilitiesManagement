from django.shortcuts import render
from django.views.generic import TemplateView
from dashboard.views import RenderSideBar
from .forms import ScanForm, ScanAddForm


class ScansView(TemplateView):
    template = 'scans/scans.html'

    def get(self, request, *args, **kwargs):
        form = ScanAddForm()
        formEdit = ScanAddForm(id='edit')
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
            'formEdit': formEdit,
        }
        return render(request, self.template, context)


class ScansDetailView(TemplateView):
    template = 'scans/scan_detailed.html'

    def get(self, request, *args, **kwargs):
        form = ScanForm()
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
        }
        return render(request, self.template, context)

class ScanHostsView(TemplateView):
    template = 'scans/scan_hosts.html'

    def get(self, request, *args, **kwargs):
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
        }
        return render(request, self.template, context)