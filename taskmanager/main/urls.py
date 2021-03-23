from django.urls import path, re_path
from django.conf.urls import url
from . import views
urlpatterns = [
    path('',views.index,name='home'),
    path('about',views.about,name='about'),
    path('create',views.create,name='create'),
    path('calc',views.calc,name='calc'),
    path('installation',views.installation,name='installation'),
    path('errv',views.errv,name='errv'),
    path('login', views.loginPage, name="login"),
    path('register', views.registerPage, name="register"),
    path('logout', views.logoutUser, name="logout")

]
