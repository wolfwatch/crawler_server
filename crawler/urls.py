"""
the urlpatterns' list routes URLs to views. for mor information please see:
    docs.djangoproject.com/en/2.1/topics/http/urls/
EX:
Function views
    1. add an inport: from my_app import views
    2. add a URL to urlpatterns: path('', views.home, name='home')

Class-based views
    1. Add an import: from other_app.views import Home
    2. Add a URL to urlpatterns: path('', Home.as_view(), name = 'home')

Including another URLconf
    1. Import the include() function: from djaongo.ruls import include, path
    2. add a URL to urlpatterns: path('blog/', include('blod.urls'))
"""

from django.urls import include, path
from django.contrib import admin

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('result/', views.result, name='result'),
    path('admin/', admin.site.urls),
    path('odm', views.home, name='home')
]