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
    path('risk', views.m_risk, name='risk'),
    path('risk2', views.m_risk3, name='risk2'),
    path('avtime', views.m_avtime, name="avtime"),
    path('wstime', views.m_wstime, name="wstime"),
    path('index',views.index,name='index'),
    path('map',views.map,name='map'),
    path('update_installation/<str:pk>/', views.updateInstallation, name="update_installation"),
    path('update_errv/<str:pk>/', views.updateERRV, name="update_errv"),

]
