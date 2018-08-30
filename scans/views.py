from django.shortcuts import render
from django.views.generic import TemplateView
from dashboard.views import RenderSideBar
from .forms import ScanForm, ScanAddForm


class ScansView(TemplateView):
    template = 'scans.html'

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
    template = 'scan_detailed.html'

    def get(self, request, *args, **kwargs):
        form = ScanForm()
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
        }
        return render(request, self.template, context)
