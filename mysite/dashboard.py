"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'mysite.dashboard.CustomIndexDashboard'
"""

from django.utils.translation import ugettext_lazy as _

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name


class MainDashboard(Dashboard):
    def init_with_context(self, context):
        user = context.get('request').user
        site_name = get_admin_site_name(context)

        self.children.append(modules.AppList(
            _('Advertising Contracts'),
            column=1,
            models=('contracts.*',),
        )
        )

        if user.is_superuser:
            self.children.append(modules.AppList(
                _('User Accounts'),
                column=1,
                collapsible=False,
                models=('account.*', 'django.contrib.auth.*', 'mysite.*'),
            )
            )

        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('Media Management'),
            column=2,
            collapsible=False,
            children=[
                {
                    'title': _('File Browser'),
                    'url': '/admin/filebrowser/browse/',
                    'external': False,
                },
            ]
        ))

        if user.is_superuser:
            self.children.append(modules.AppList(
                _('Server Administration'),
                column=2,
                collapsible=False,
                exclude=('account.*', 'django.contrib.auth.*', 'mysite.*', 'contracts.*'),
            ))



        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=5,
            collapsible=False,
            column=3,
        ))


