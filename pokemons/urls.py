from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include(('show.urls', 'show'), namespace="show")),
    path('admin/', admin.site.urls),
    path('load/', include(('load.urls', 'load'), namespace="load")),
    path('show/', include(('show.urls', 'load'), namespace="show"))
]
