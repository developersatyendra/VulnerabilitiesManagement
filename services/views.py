from django.shortcuts import render
from django.views.generic import TemplateView
from dashboard.views import RenderSideBar
from .forms import ServiceForm


class ServicesView(TemplateView):
    template = 'services/services.html'

    def get(self, request, *args, **kwargs):
        form = ServiceForm()
        formEdit = ServiceForm(id='edit')
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
            'formEdit': formEdit,
        }
        return render(request, self.template, context)


class ServiceDetailView(TemplateView):
    template = 'services/service_detailed.html'

    def get(self, request, *args, **kwargs):
        form = ServiceForm()
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
        }
        return render(request, self.template, context)


class ServiceRelevantVulnView(TemplateView):
    template = 'services/service_relevantvuln.html'

    def get(self, request, *args, **kwargs):
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
        }
        return render(request, self.template, context)


class ServiceRunOnHostView(TemplateView):
    template = 'services/service_runonhost.html'

    def get(self, request, *args, **kwargs):
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
        }
        return render(request, self.template, context)