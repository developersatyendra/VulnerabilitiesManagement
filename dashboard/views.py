from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView


# Create your views here.
class DashboardView(TemplateView):
    def get(self, request, *args, **kwargs):
        sidebarHtml = RenderSideBar(request)
        sidebarActive = 'dashboard'
        context = {'sidebarActive': sidebarActive, 'sidebar': sidebarHtml}
        return render(request, 'dashboard.html', context)


class SidebarBtn(object):
    isActive = False
    name = 'Item'
    href = ''
    iconRef = ''
    childBtn = None

    def __init__(self, isActive, name, href, iconRef, childBtn=None):
        self.isActive = isActive
        self.name = name
        self.href = href
        self.iconRef = iconRef
        self.childBtn = childBtn

    def __str__(self):
        return self.name


def RenderSideBar(request):
    sidebar = [
        SidebarBtn(False, ' Dashboard', reverse_lazy('dashboard:dashboard'), 'fa fa-dashboard fa-fw'),
        SidebarBtn(False, ' Scan', reverse_lazy('scans:scans'), 'fa fa-search fa-fw', [
            SidebarBtn(False, ' Scan Projects', reverse_lazy('projects:projects'), 'fa fa-clipboard'),
            SidebarBtn(False, ' Scan Tasks', reverse_lazy('scans:scans'), 'fa fa-tasks fa-fw'),
        ]),
        SidebarBtn(False, ' Vulnerabilities', reverse_lazy('vulnerabilities:vulnerabilities'), 'fa fa-exclamation-triangle fa-fw'),
        SidebarBtn(False, ' Hosts', reverse_lazy('hosts:hosts'), 'fa fa-desktop fa-fw'),
        SidebarBtn(False, ' Services', reverse_lazy('services:services'), 'fa fa-cogs fa-fw'),
        SidebarBtn(False, ' Reports', reverse_lazy('reports:reports'), 'fa fa-file-pdf-o fa-fw'),
        SidebarBtn(False, ' Submit', reverse_lazy('submit:submit'), 'fa fa-upload fa-fw'),
        SidebarBtn(False, ' Settings', reverse_lazy('settings:settings'), 'fa fa-sliders fa-fw'),
    ]
    sidebarHtml = ''

    for btn in sidebar:
        if btn.childBtn:
            ndBtnHtml = ''
            for btnSub in btn.childBtn:
                btnSubHref = str(btnSub.href).lower()
                fullPathUrl = str(request.get_full_path())
                print(btnSubHref)
                print(fullPathUrl)
                if btnSubHref in fullPathUrl:
                    btn.isActive = True
                    btnSub.isActive = True
                ndBtnHtml = ndBtnHtml + "<li>\
                            <a href=\"{0}\" {1}><i class=\"{2}\"></i>{3}</a>\
                        </li>".format(btnSub.href, 'class=\"active\"' if btnSub.isActive else '', btnSub.iconRef, btnSub.name)
            sidebarHtml = sidebarHtml + \
                    "<li {0}>\
                        <a href=\"{1}\"><i class=\"{2}\"></i> {3}<span class=\"fa arrow\"></span></a>\
                        <ul class=\"nav nav-second-level {4}\">\
                        {5}</ul>\
                        <!-- /.nav-second-level -->\
                    </li>".format('class=\"active\"' if btn.isActive else "", btn.href, btn.iconRef, btn.name, 'collapse in' if btn.isActive else 'collapse', ndBtnHtml)
        else:
            btnHref = str(btn.href).lower()
            fullPathUrl = str(request.get_full_path())
            if btnHref in fullPathUrl:
                sidebarHtml = sidebarHtml + "<li><a href=\"{}\" {}><i class=\"{}\"></i> {}</a></li>".format(btn.href,
                                                                                                            'class=\"active\"',
                                                                                                            btn.iconRef,
                                                                                                            btn.name)
            else:
                sidebarHtml = sidebarHtml + "<li><a href=\"{}\"><i class=\"{}\"></i> {}</a></li>".format(btn.href,
                                                                                                         btn.iconRef,
                                                                                                         btn.name)
    return sidebarHtml