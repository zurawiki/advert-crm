from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib import admin
from filebrowser.sites import site

from mysite import views


urlpatterns = patterns("",
                       url(r"^$", TemplateView.as_view(template_name="homepage.html"), name="home"),
                       url(r"^pending$", TemplateView.as_view(template_name="pending_approval.html")),
                       url(r"^register$", views.register_advertiser),
                       url(r"^contracts/", include('contracts.urls')),
                       (r'^admin/filebrowser/', include(site.urls)),
                       (r'^grappelli/', include('grappelli.urls')),  # grappelli URLS
                       (r'^admin/', include(admin.site.urls)),  # admin site
                       url(r"^accounts/", include("account.urls")),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
