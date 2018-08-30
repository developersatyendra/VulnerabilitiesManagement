from django.shortcuts import render
from django.views.generic import TemplateView
from dashboard.views import RenderSideBar
from .forms import ServiceForm


class ServicesView(TemplateView):
    template = 'services.html'

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
    template = 'service_detailed.html'

    def get(self, request, *args, **kwargs):
        form = ServiceForm()
        sidebarHtml = RenderSideBar(request)
        context = {
            'sidebar': sidebarHtml,
            'form': form,
        }
        return render(request, self.template, context)
