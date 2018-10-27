from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView


# Create your views here.
class DashboardView(TemplateView):
    def get(self, request, *args, **kwargs):
        sidebarHtml = RenderSideBar(request)
        sidebarActive = 'dashboard'
        context = {'sidebarActive': sidebarActive, 'sidebar': sidebarHtml}
        return render(request, 'dashboard/dashboard.html', context)


class SidebarBtn(object):
    isActive = False
    name = 'Item'
    href = ''
    iconRef = ''
    childBtn = None
    permissions = []

    def __init__(self, isActive, name, href, iconRef, permissions = [], childBtn=None):
        self.isActive = isActive
        self.name = name
        self.href = href
        self.iconRef = iconRef
        self.permissions = permissions
        self.childBtn = childBtn

    def __str__(self):
        return self.name

    def CheckPermissions(self, user):
        ret_val = True
        for perm in self.permissions:
            ret_val = ret_val and user.has_perm(perm)
        return ret_val


def RenderSideBar(request):
    sidebar = [
        SidebarBtn(False, ' Dashboard', reverse_lazy('dashboard:dashboard'), 'fa fa-dashboard fa-fw'),
        SidebarBtn(False, ' Scan', None, 'fa fa-search fa-fw', childBtn= [
            SidebarBtn(False, ' Scan Projects', reverse_lazy('projects:projects'), 'fa fa-clipboard fa-fw'),
            SidebarBtn(False, ' Scan Tasks', reverse_lazy('scans:scans'), 'fa fa-search fa-fw'),
        ]),
        SidebarBtn(False, ' Hosts', reverse_lazy('hosts:hosts'), 'fa fa-desktop fa-fw'),
        SidebarBtn(False, ' Vulnerabilities', reverse_lazy('vulnerabilities:vulnerabilities'),
                   'fa fa-exclamation-triangle fa-fw'),
        SidebarBtn(False, ' Services', reverse_lazy('services:services'), 'fa fa-cogs fa-fw'),
        SidebarBtn(False, ' Reports', None, 'fa fa-file-pdf-o fa-fw', childBtn= [
            SidebarBtn(False, ' Project Reports', reverse_lazy('reports:projectReport'), 'fa fa-clipboard fa-fw'),
            SidebarBtn(False, ' Scan Reports', reverse_lazy('reports:scanReport'), 'fa fa-search fa-fw'),
            SidebarBtn(False, ' Host Reports', reverse_lazy('reports:hostReport'), 'fa fa-desktop fa-fw'),
        ]),
        SidebarBtn(False, ' Submit', reverse_lazy('submit:submit'), 'fa fa-upload fa-fw'),
        SidebarBtn(False, ' Settings', reverse_lazy('settings:settings'), 'fa fa-sliders fa-fw',childBtn= [
            SidebarBtn(False, ' My Account', reverse_lazy('settings:MyAccount'), 'fa fa-user fa-fw'),
            SidebarBtn(False, ' Account Management', reverse_lazy('settings:AccountManagement'), 'fa fa-users fa-fw', permissions=['user.can_view_user', 'user.can_add_user', 'user.can_change_user']),
        ]),
    ]
    sidebarHtml = ''

    for btn in sidebar:
        if btn.childBtn:
            ndBtnHtml = ''
            for btnSub in btn.childBtn:
                if btnSub.CheckPermissions(request.user):
                    btnSubHref = str(btnSub.href).lower()
                    fullPathUrl = str(request.get_full_path())
                    if btnSubHref in fullPathUrl:
                        # btn.isActive = True
                        btnSub.isActive = True
                    ndBtnHtml = ndBtnHtml + "<li>\
                                <a href=\"{0}\" {1}><i class=\"{2}\"></i>{3}</a>\
                            </li>".format(btnSub.href, 'class=\"active\"' if btnSub.isActive else '', btnSub.iconRef, btnSub.name)
            if ndBtnHtml != '':
                sidebarHtml = sidebarHtml + \
                        "<li>\
                            <a href=\"{0}\"><i class=\"{1}\"></i> {2}<span class=\"fa arrow\"></span></a>\
                            <ul class=\"nav nav-second-level {3}\">\
                            {4}</ul>\
                            <!-- /.nav-second-level -->\
                        </li>".format(btn.href, btn.iconRef, btn.name, 'collapse in' if btn.isActive else 'collapse', ndBtnHtml)
        else:
            if btn.CheckPermissions(request.user):
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