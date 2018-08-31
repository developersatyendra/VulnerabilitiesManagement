from django.shortcuts import render
from django.views.generic import TemplateView
from dashboard.views import RenderSideBar
from .forms import VulnForm


PAGE_DEFAULT = 1
NUM_ENTRY_DEFAULT = 50


class VulnerabilitiesView(TemplateView):
    template = 'vulns/vulns.html'

    def get(self, request, *args, **kwargs):
        form = VulnForm()
        formEdit = VulnForm(id='edit')
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
            'formEdit': formEdit,
        }
        return render(request, self.template, context)


class VulnerabilityDetailView(TemplateView):
    template = 'vulns/vuln_detailed.html'

    def get(self, request, *args, **kwargs):
        form = VulnForm()
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
        }
        return render(request, self.template, context)