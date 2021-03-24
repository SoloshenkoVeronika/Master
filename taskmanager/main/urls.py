from django.urls import path, re_path
from django.conf.urls import url
from . import views
urlpatterns = [
    path('',views.index,name='home'),
    path('about',views.about,name='about'),
    path('calc',views.calc,name='calc'),
    path('installation',views.installation,name='installation'),
    path('errv',views.errv,name='errv'),
    path('login', views.loginPage, name="login"),
    path('register', views.registerPage, name="register"),
    path('logout', views.logoutUser, name="logout"),
    path('risk', views.m_risk, name="risk"),
    path('avtime', views.m_avtime, name="avtime"),
    path('wstime', views.m_wstime, name="wstime")

]
