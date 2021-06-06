from msilib import Binary
import tablib
from django.shortcuts import render,redirect
from django.urls import reverse

from .forms import InstallationForm,ERRVForm,ExampleForm
from .models import Installation,ERRV,Waves
from django.shortcuts import get_object_or_404, render
import shutil
import sys
import os.path
from .optimization import *
from pyomo.environ import *
from pyomo.opt import SolverFactory
# assert(shutil.which("cbc") or os.path.isfile("cbc"))
# from __future__ import division
from pyomo.environ import *
from pyomo.opt import SolverFactory
import numpy as np
import math
#from django.shortcuts import render, render_to_response
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template.loader import get_template
from django.template import Context
from django.views.generic.base import TemplateView
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
import pandas as pd
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from folium.plugins import MarkerCluster
import pandas as pd
from django.contrib.auth.decorators import login_required
#import geopandas as gpd
from shapely.geometry import Polygon
import folium
from pyomo.environ import *
from pyomo.opt import SolverFactory
from .forms import  CreateUserForm
import numpy as np
import math
from django.core import serializers
import os, re, math
import json
from django import forms
from itertools import combinations
from django.http import HttpResponse
import pandas as pd
import datetime as dt
from shapely.geometry import Polygon
from scipy.stats import weibull_min
# Create your views here.
import csv
import os
import shutil
import time
import pyutilib.subprocess.GlobalData
pyutilib.subprocess.GlobalData.DEFINE_SIGNAL_HANDLERS_DEFAULT = False

number_ERRV = 0
ins_fix_list_g = []

def index(request):
    context={'title':'Main page'}
    return render(request,'main/index.html',context)

@login_required(login_url='login')
def home(request):
    context={'title':'Main page'}
    return render(request,'main/home.html',context)

@login_required(login_url='login')
def about(request):
    installations = Installation.objects.order_by('id')

    full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "recources")
    filename_results = "Model3terrv.sol"
    FileFullPathResults = os.path.join(full_path, filename_results)
    with open(FileFullPathResults, 'r') as f:
        for x in f:
            errvs = ERRV.objects.filter(id=int(x))

    errvs= ERRV.objects.filter(type_solution__in=[201,210,202,203,204,205])
    print("errvs=",errvs)
    #errvs = ERRV.objects.order_by('id')
    # print("Delete=",request.GET.get('DeleteButton'))
    if (request.GET.get('DeleteButtonI')):
        Installation.objects.filter(id = request.GET.get('DeleteButtonI')).delete()
    if (request.GET.get('DeleteButtonE')):
        ERRV.objects.filter(id = request.GET.get('DeleteButtonE')).delete()

    m = folium.Map([62.354457, 2.377184], zoom_start=6)

    lat_list_inst = []
    lon_list_inst = []
    elev_list_inst = []
    name_list_inst = []
    for e in Installation.objects.all():
        lat_list_inst.append(e.latitude)
        lon_list_inst.append(e.longitude)
        elev_list_inst.append(1)
        name_list_inst.append(e.title)

    lat_inst = pd.Series(lat_list_inst)
    lon_inst = pd.Series(lon_list_inst)
    elevation_inst = pd.Series(elev_list_inst)
    name_inst = pd.Series(name_list_inst)

    #Function to change colors
    def color_change(elev):
        if(elev == 1 ):
            return('#3f7fff') #0017ff  3f7fff
        elif(elev == 201):
            return('#ffda25')
        elif(elev == 202):
            return('#ff7a2f') #ff7a2f
        elif(elev == 203):
            return('#55cb68') #55cb68
        elif(elev == 204):
            return('#bf6bc7')
        elif(elev == 205):
            return('#f8b5f5')
        elif(elev == 210):
            return('#fcffd0')


    lat_list_errv = []
    lon_list_errv = []
    elev_list_errv = []
    name_list_errv = []
    for e in ERRV.objects.all():
        lat_list_errv.append(e.latitude)
        lon_list_errv.append(e.longitude)
        name_list_errv.append(e.title)
        if(e.type_solution == 201.0):
            elev_list_errv.append(201)
        elif (e.type_solution == 210.0):
              elev_list_errv.append(210)
        elif (e.type_solution == 202.0):
                elev_list_errv.append(202)
        elif (e.type_solution == 203.0):
                elev_list_errv.append(203)
        elif (e.type_solution == 204.0):
                elev_list_errv.append(204)
        elif (e.type_solution == 205.0):
                elev_list_errv.append(205)

    lat_errv = pd.Series(lat_list_errv)
    lon_errv = pd.Series(lon_list_errv)
    elevation_errv = pd.Series(elev_list_errv)
    name_errv = pd.Series(name_list_errv)
    # _____________ Circle____________________
    data2 = pd.read_csv("main\\recources\\Data_Map_ERRV.txt")
    lat2 = data2['LAT']
    lon2 = data2['LON']
    elevation2 = data2['ELEV']

    # Function to change colors
    # def radius_change(elev):
    #     if(elev == 3 ):
    #         return 62050
    #     elif(elev == 5):
    #         return 124100
    #     elif(elev == 6):
    #         return 155125
    #
    # for lat2, lon2, elevation2 in zip(lat2, lon2, elevation2):
    #     folium.Circle(location=[lat2, lon2], radius = radius_change(elevation2), fill_color='red',  fill_opacity = 0.05).add_to(m)
    # _____________ Circle____________________

#Plot Markers
    for lat, lon, elevation, name_inst in zip(lat_inst, lon_inst, elevation_inst,name_inst):
        folium.CircleMarker(location=[lat, lon], radius = 5, popup=str(name_inst), fill_color=color_change(elevation),color=color_change(elevation),  fill_opacity = 1).add_to(m)

    for lat, lon, elevation,name_errv in zip(lat_errv, lon_errv, elevation_errv,name_errv):
        folium.CircleMarker(location=[lat, lon], radius = 5, popup=str(name_errv), fill_color=color_change(elevation),color=color_change(elevation),  fill_opacity = 1).add_to(m)

    m=m._repr_html_() #updated
    context = {
        'installations': installations,
        'errvs': errvs,
        'title':'Map',
        'my_map': m,
    }
    return render(request,'main/about.html',context)

@login_required(login_url='login')
def installation(request):
    answer = ''
    error = ''
    if  request.method == 'POST':
        form = InstallationForm(request.POST)
        if form.is_valid():
            form.save()
            answer = 'The installation has been added to the databases'

        else:
            error = 'Form is not valide'
    installations = Installation.objects.order_by('id')
    form = InstallationForm()
    context = {
        'installations': installations,
        'form': form,
        'answer':answer,
        'error':error,
        'title':'Installations'
    }
    return render(request,'main/installation.html',context)

@login_required(login_url='login')
def updateInstallation(request, pk):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!111pk===",pk)
    installation = Installation.objects.get(id=pk)
    print("!!!!!!!!!order===",installation)
    form = InstallationForm(instance=installation)

    if request.method == 'POST':
        form = InstallationForm(request.POST, instance=installation)
        if form.is_valid():
            form.save()
            installations = Installation.objects.order_by('id')
            errvs= ERRV.objects.filter(type_solution__in=[201,210,202,203,204,205])
            context = {
                'installations': installations,
                'errvs': errvs,
                'title':'About'
            }
            return render(request, 'main/about.html',context)

    context = {'form':form}
    return render(request, 'main/installation.html', context)

@login_required(login_url='login')
def updateERRV (request, pk):
    errv = ERRV.objects.get(id=pk)
    form = ERRVForm(instance=errv)

    if request.method == 'POST':
        form = ERRVForm(request.POST, instance=errv)
        if form.is_valid():
            form.save()
            installations = Installation.objects.order_by('id')
            errvs= ERRV.objects.filter(type_solution__in=[201,210,202,203,204,205])
            context = {
                'installations': installations,
                'errvs': errvs,
                'title':'About'
            }
            return render(request, 'main/about.html',context)

    context = {'form':form}
    return render(request, 'main/errv.html', context)

@login_required(login_url='login')
def errv(request):
    answer = ''
    error = ''
    if  request.method == 'POST':
        form = ERRVForm(request.POST)
        if form.is_valid():
            form.save()
            if 'Current' in request.POST:
                # form.type_solution
                print("Current")
                # Installation.objects.filter(id = ).delete()
            elif  'Potential' in request.POST:
                print("Potential")
                    # Installation.objects.filter(id = request.GET.get('DeleteButtonI')).delete()
            answer = 'ERRV has been added to the databases'
        else:
            error = 'Form is not valide'

    errvs= ERRV.objects.filter(type_solution=201)
    form = ERRVForm()
    context = {
        'form': form,
        'answer':answer,
        'error':error,
        'errvs': errvs,
        'title':'ERRV'
    }
    return render(request,'main/errv.html',context)

@login_required(login_url='login')
def calc(request):
    if  request.method == 'POST':
        grid = request.POST.get("grid", "")
        if 'average_time' in request.POST:
            model1(grid)
            model2()
        elif 'worst_time' in request.POST:
            model1(grid)
            model3()
        elif 'Risks' in request.POST:
            return render(request,'main/risk.html')

        # print("request=!!!!!!!!!!!!!!!!!",request.POST.get("grid", ""))
        # print("grid_get=",grid)
        # model1(grid)
        # model2()
        # model3()
        installations = Installation.objects.order_by('id')
        errvs = ERRV.objects.order_by('id')
        # full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "recources")
        # filename_results = "Model3terrv.sol"
        # FileFullPathResults = os.path.join(full_path, filename_results)
        # with open(FileFullPathResults, 'r') as f:
        #     for x in f:
        #         errvs = ERRV.objects.filter(id=int(x))
        # # errvs = ERRV.objects.filter(id=2)
        # errvs = ERRV.objects.order_by('id')
        # print("===",errvs)

        return render(request,'main/about.html',{'title':'about','installations': installations,'errvs': errvs})
    else:
        form = 'Yes'
        context = {
            'form': form
        }
        return render(request,'main/calc.html')

@login_required(login_url='login')
def m_avtime(request):
    print("_________________Average_time____________________")
    error = ''
    installations = Installation.objects.order_by('id')
    if  request.method == 'POST':
        flag_grid=0
        type_errv = 0
        ins_fix_list = 0
        flag_model4 = 0
        grid = request.POST.get("grid", "")
        display_type = request.POST.get("display_type", None)
        ins_fix_flag = request.POST.get("ins_fix", None)

        if ins_fix_flag in ["F"]:
            ins_fix_list = request.POST.get("inst_list", "")
        if display_type in ["DB"]:
            type_errv = 1
        elif display_type == "GR":
            type_errv = 2
            if grid == '':
                flag_grid = 1

        if (type_errv == 2 and flag_grid == 1):
            error = 'Number is not valide'
            context = {
                'installations': installations,
                'error':error,
                'title': "Minimizing average time"
            }
        else:
            start_time = time.time()
            model1(grid,type_errv,ins_fix_list)
            model2(ins_fix_list,flag_model4)
            print("--- %s seconds ---" % (time.time() - start_time))
            # errvs= ERRV.objects.filter(type_solution=202)
            # installations = Installation.objects.order_by('id')

            #creation of map comes here + business logic
            m = folium.Map([62.354457, 2.377184], zoom_start=6)

            #Load Data
            data = pd.read_csv('main\\recources\\Data_Map.txt')
            lat = data['LAT']
            lon = data['LON']
            elevation = data['ELEV']
            name = data['NAME']

            #Function to change colors
            def color_change(elev):
                if(elev == 1 ):
                    return('blue')
                elif(elev == 2):
                    return('yellow')
                elif(elev == 3):
                    return('red')
                elif(elev == 100):
                    return('purple')

            #Function to change colors
            def radius_change(elev):
                if(elev == 3 ):
                    return 62050
                elif(elev == 5):
                    return 124100
                elif(elev == 6):
                    return 155125

                    #Function to change colors
            def radius_size(elev):
                if(elev == 1 ):
                    return 2
                elif(elev == 2):
                    return 1
                elif(elev == 3 or elev == 100):
                    return 3

            data2 = pd.read_csv("main\\recources\\Data_Map_ERRV.txt")
            lat2 = data2['LAT']
            lon2 = data2['LON']
            elevation2 = data2['ELEV']

            for lat2, lon2, elevation2 in zip(lat2, lon2, elevation2):
                folium.Circle(location=[lat2, lon2], radius = radius_change(elevation2), fill_color='red',  fill_opacity = 0.05).add_to(m)

            #Plot Markers
            for lat, lon, elevation,name in zip(lat, lon, elevation,name):
                folium.CircleMarker(location=[lat, lon], radius = radius_size(elevation), popup=str(name), fill_color=color_change(elevation),color=color_change(elevation),  fill_opacity = 0.9).add_to(m)

            m=m._repr_html_() #updated


            context = {
                    'installations': installations,
                    'error':error,
                    'my_map': m,
                    # 'errvs': errvs,
                    'title': "Minimizing average time"
                }
        return render(request,'main/avtime.html',context)
    else:
        context = {
            'installations': installations,
            'title': "Minimizing average time"
        }
        return render(request,'main/avtime.html',context)

@login_required(login_url='login')
def m_wstime(request):
    print("_________________Worst time____________________")
    error = ''
    installations = Installation.objects.order_by('id')
    if  request.method == 'POST':
        flag_grid=0
        type_errv = 0
        ins_fix_list = 0
        flag_model4 = 0
        grid = request.POST.get("grid", "")
        display_type = request.POST.get("display_type", None)
        ins_fix_flag = request.POST.get("ins_fix", None)

        if ins_fix_flag in ["F"]:
            ins_fix_list = request.POST.get("inst_list", "")
        if display_type in ["DB"]:
            type_errv = 1
        elif display_type == "GR":
            type_errv = 2
            if grid == '':
                flag_grid = 1

        if (type_errv == 2 and flag_grid == 1):
            error = 'Number is not valide'
            context = {
                'installations': installations,
                'error':error,
                'title': "Minimizing average time"
            }
        else:
            model1(grid,type_errv,ins_fix_list)
            model3(ins_fix_list,flag_model4)
            # errvs= ERRV.objects.filter(type_solution=203)
            installations = Installation.objects.order_by('id')
            m = folium.Map([62.354457, 2.377184], zoom_start=6)

            #Load Data
            data = pd.read_csv('main\\recources\\Data_Map.txt')
            lat = data['LAT']
            lon = data['LON']
            elevation = data['ELEV']
            name = data['NAME']

            #Function to change colors
            def color_change(elev):
                if(elev == 1 ):
                    return('blue')
                elif(elev == 2):
                    return('yellow')
                elif(elev == 3):
                    return('red')
                elif(elev == 100):
                    return('purple')

            #Function to change colors
            def radius_change(elev):
                if(elev == 3 ):
                    return 62050
                elif(elev == 5):
                    return 124100
                elif(elev == 6):
                    return 155125

                    #Function to change colors
            def radius_size(elev):
                if(elev == 1 or elev == 100):
                    return 2
                elif(elev == 2):
                    return 1
                elif(elev == 3):
                    return 3

            data2 = pd.read_csv("main\\recources\\Data_Map_ERRV.txt")
            lat2 = data2['LAT']
            lon2 = data2['LON']
            elevation2 = data2['ELEV']

            for lat2, lon2, elevation2 in zip(lat2, lon2, elevation2):
                folium.Circle(location=[lat2, lon2], radius = radius_change(elevation2), popup=str(elevation2)+" m", fill_color='red',  fill_opacity = 0.05).add_to(m)

            #Plot Markers
            for lat, lon, elevation,name in zip(lat, lon, elevation,name):
                folium.CircleMarker(location=[lat, lon], radius = radius_size(elevation), popup=str(name), fill_color=color_change(elevation),color=color_change(elevation), fill_opacity = 0.9).add_to(m)

            m=m._repr_html_() #updated


            context = {
                'installations': installations,
                # 'errvs':errvs,
                'my_map': m,
                'error':error,
                'title': "Worst-time minimization"
            }
        return render(request,'main/wstime.html',context)

    else:
        context = {
            'installations': installations,
            'title': "Worst-time minimization"
        }
        return render(request,'main/wstime.html',context)

@login_required(login_url='login')
def m_risk(request):
    print("______________Risk_1_______________")

    #     grid = request.POST.get("grid", "")
    #     count_errv = model1(grid)
    #     full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "recources")
    #     filename = "Modelpotpos.dat"
    #     FileFullPath = os.path.join(full_path, filename)
    #
    #     with open(FileFullPath) as f:
    #         m= [line.split() for line in f]
    #     print(m)
    #     print("type=",type(m))
    #     list = []
    #     errvs = ERRV()
    #     for i in range(int(count_errv)):
    #         errvs = ERRV(title="O4_" +str(m[i][0]), latitude=m[i][1],longitude=m[i][2],prob=0.001,type_solution=1001)
    #         list.append(i)
    #     print("m=",errvs)
    #
    #
    #     context = {
    #         'nv':list,
    #         'el':errvs.get_lat(),
    #         'title': "Risk22"
    #     }
    #     #return render(request,'main/risk2.html',context)
    #     return HttpResponseRedirect('risk2',context)
    #
    #     #return redirect ('risk2',context)
    # else:
    #     context = {
    #         'title': "Risk1"
    #     }
    #     return render(request,'main/risk.html',context)

    error = ''
    installations = Installation.objects.order_by('id')
    flag_model4 = 1
    if  request.method == 'POST':
        print("JJLJKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK")
        flag_grid=0
        type_errv = 0
        ins_fix_list = 0
        grid = request.POST.get("grid", "")
        print("grid=",grid)
        display_type = request.POST.get("display_type", None)
        ins_fix_flag = request.POST.get("ins_fix", None)

        if ins_fix_flag in ["F"]:
            ins_fix_list = request.POST.get("inst_list", "")
            global ins_fix_list_g
            ins_fix_list_g = ins_fix_list
        if display_type in ["DB"]:
            type_errv = 1
        elif display_type == "GR":
            type_errv = 2
            if grid == '':
                flag_grid = 1

        if (type_errv == 2 and flag_grid == 1):
            error = 'Number is not valide'
            context = {
                'installations': installations,
                'error':error,
                'title': "Minimizing average time"
            }
        else:
            global number_ERRV
            number_ERRV = model1(grid,type_errv,ins_fix_list)
            context = {
                'installations': installations,
                'error':error,
                'title': "Risk model"
            }

        return HttpResponseRedirect('risk2',context)
    else:

        context = {
                'installations': installations,
                'title': "Risk model"
            }
        return render(request,'main/risk.html',context)

@login_required(login_url='login')
def risk2(request):
    print("______________Risk2_____________________________________")
    installations = Installation.objects.order_by('id')
    flag_model4 = 0
    error = ''
    list_numner_vessels = []
    print("!!!number_ERRV=",number_ERRV)
    for i in range(number_ERRV):
        list_numner_vessels.append(number_ERRV)

    print("list_numner_vessels=",list_numner_vessels)

    if  request.method == 'POST':
        pp = request.POST.get("pp", "")

        age = request.POST.getlist("age")
        # risk1 = 0.1
        # risk21 = 0.1
        # risk22 = 0.3
        # risk31 = 0.1
        # risk32 = 0.2
        # risk33 = 0.3
        # risk4 = 0.5
        #
        # risk_list = []
        # risk2 = 1 - (1-float(risk21))*(1-float(risk22))
        # risk3 = 1 - (1-float(risk31))*(1-float(risk32))*(1-float(risk33))
        # risk_sum = 1-(1-float(risk1))*(1-float(risk2))*(1-float(risk3))*(1-float(risk4))
        # risk_list.append(risk_sum)
        # risk_list.append(4)
        # full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "recources")
        # filename = "Probability0.txt"
        # FileFullPath = os.path.join(full_path, filename)
        # with open(FileFullPath, 'w') as f:
        #     for i in risk_list:
        #         f.write(str(i)+"\n")
        #
        # print("risk_list=",risk_list)
        #
        # model_risk(wr,wt)
        # #model_risk(wr,wt)
        print("pp=",pp," ",age," ")
        context = {
            #'installations':installations,
            'title': "About"
        }

        test_list = [int(i) for i in age]
        errv_ages = tuple(test_list)


        crush_prob_res = crush_prob(pp,errv_ages)
        model4(ins_fix_list_g,flag_model4)

        #creation of map comes here + business logic
        m = folium.Map([62.354457, 2.377184], zoom_start=6)

        #Load Data
        data = pd.read_csv('main\\recources\\Data_Map.txt')
        lat = data['LAT']
        lon = data['LON']
        elevation = data['ELEV']
        name = data['NAME']

        #Function to change colors
        def color_change(elev):
            if(elev == 1 ):
                return('blue')
            elif(elev == 2):
                return('yellow')
            elif(elev == 3):
                return('red')
            elif(elev == 100):
                return('purple')

        #Function to change colors
        def radius_change(elev):
            if(elev == 3 ):
                return 62050
            elif(elev == 5):
                return 124100
            elif(elev == 6):
                return 155125

                #Function to change colors
        def radius_size(elev):
            if(elev == 1 ):
                return 2
            elif(elev == 2):
                return 1
            elif(elev == 3 or elev == 100):
                return 3

        data2 = pd.read_csv("main\\recources\\Data_Map_ERRV.txt")
        lat2 = data2['LAT']
        lon2 = data2['LON']
        elevation2 = data2['ELEV']

        for lat2, lon2, elevation2 in zip(lat2, lon2, elevation2):
            folium.Circle(location=[lat2, lon2], radius = radius_change(elevation2), popup=str(elevation2)+" m", fill_color='red',  fill_opacity = 0.05).add_to(m)

        #Plot Markers
        for lat, lon, elevation,name in zip(lat, lon, elevation,name):
            folium.CircleMarker(location=[lat, lon], radius = radius_size(elevation), popup=str(name), fill_color=color_change(elevation),color=color_change(elevation),  fill_opacity = 0.9).add_to(m)

        m=m._repr_html_() #updated


        context = {
            'installations': installations,
            'error':error,
            'my_map': m,
            # 'errvs': errvs,
            'title': "Risk based model"
        }

        return render(request,'main/risk.html',context)
    else:
        context = {
            'numner_vessels':list_numner_vessels,
            'title': "Risk2"
        }
        return render(request,'main/risk2.html',context)

@login_required(login_url='login')
def multi(request):
    print("_________________Multi____________________")
    error = ''
    installations = Installation.objects.order_by('id')
    flag_model4 = 1
    if  request.method == 'POST':
        flag_grid=0
        type_errv = 0
        ins_fix_list = 0
        grid = request.POST.get("grid", "")
        display_type = request.POST.get("display_type", None)
        ins_fix_flag = request.POST.get("ins_fix", None)

        if ins_fix_flag in ["F"]:
            ins_fix_list = request.POST.get("inst_list", "")
            global ins_fix_list_g
            ins_fix_list_g = ins_fix_list
        if display_type in ["DB"]:
            type_errv = 1
        elif display_type == "GR":
            type_errv = 2
            if grid == '':
                flag_grid = 1

        if (type_errv == 2 and flag_grid == 1):
            error = 'Number is not valide'
            context = {
                'installations': installations,
                'error':error,
                'title': "Minimizing average time"
            }
        else:
            global number_ERRV
            number_ERRV = model1(grid,type_errv,ins_fix_list)


            context = {
                'installations': installations,
                'error':error,
                'title': "Multi-objective model222"
            }
            return HttpResponseRedirect('multi2',context)

    else:
        context = {
            'installations': installations,
            'title': "Multi-objective model"
        }
        return render(request,'main/multi.html',context)

@login_required(login_url='login')
def multi2(request):
    print("______________Multi2_____________________________________")
    installations = Installation.objects.order_by('id')
    flag_model4 = 1
    error = ''
    list_numner_vessels = []
    print("!!!number_ERRV=",number_ERRV)
    for i in range(number_ERRV):
        list_numner_vessels.append(number_ERRV)

    print("list_numner_vessels=",list_numner_vessels)

    if  request.method == 'POST':
        pp = request.POST.get("pp", "")
        wa = request.POST.get("wa", "")
        ww = request.POST.get("ww", "")
        wr = request.POST.get("wr", "")
        age = request.POST.getlist("age")
        # risk1 = 0.1
        # risk21 = 0.1
        # risk22 = 0.3
        # risk31 = 0.1
        # risk32 = 0.2
        # risk33 = 0.3
        # risk4 = 0.5
        #
        # risk_list = []
        # risk2 = 1 - (1-float(risk21))*(1-float(risk22))
        # risk3 = 1 - (1-float(risk31))*(1-float(risk32))*(1-float(risk33))
        # risk_sum = 1-(1-float(risk1))*(1-float(risk2))*(1-float(risk3))*(1-float(risk4))
        # risk_list.append(risk_sum)
        # risk_list.append(4)
        # full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "recources")
        # filename = "Probability0.txt"
        # FileFullPath = os.path.join(full_path, filename)
        # with open(FileFullPath, 'w') as f:
        #     for i in risk_list:
        #         f.write(str(i)+"\n")
        #
        # print("risk_list=",risk_list)
        #
        # model_risk(wr,wt)
        # #model_risk(wr,wt)
        print("pp=",pp," ", wa, " ",ww, " ",wr, " ",age," ")
        context = {
            #'installations':installations,
            'title': "About"
        }

        test_list = [int(i) for i in age]
        errv_ages = tuple(test_list)


        crush_prob_res = crush_prob(pp,errv_ages)
        model2(ins_fix_list_g,flag_model4)
        print("________________))))))))))))))))+++++++++++++++_____________(((((((((((((()))))))0")
        model3(ins_fix_list_g,flag_model4)
        model4(ins_fix_list_g,flag_model4)
        model5(ins_fix_list_g,wa,ww,wr)
        #creation of map comes here + business logic
        m = folium.Map([62.354457, 2.377184], zoom_start=6)

        #Load Data
        data = pd.read_csv('main\\recources\\Data_Map.txt')
        lat = data['LAT']
        lon = data['LON']
        elevation = data['ELEV']
        name = data['NAME']

        #Function to change colors
        def color_change(elev):
            if(elev == 1 ):
                return('blue')
            elif(elev == 2):
                return('yellow')
            elif(elev == 3):
                return('red')
            elif(elev == 100):
                return('purple')

        #Function to change colors
        def radius_change(elev):
            if(elev == 3 ):
                return 62050
            elif(elev == 5):
                return 124100
            elif(elev == 6):
                return 155125

                #Function to change colors
        def radius_size(elev):
            if(elev == 1 ):
                return 2
            elif(elev == 2):
                return 1
            elif(elev == 3 or elev == 100):
                return 3

        data2 = pd.read_csv("main\\recources\\Data_Map_ERRV.txt")
        lat2 = data2['LAT']
        lon2 = data2['LON']
        elevation2 = data2['ELEV']

        for lat2, lon2, elevation2 in zip(lat2, lon2, elevation2):
            folium.Circle(location=[lat2, lon2], radius = radius_change(elevation2), popup=str(elevation2)+" m", fill_color='red',  fill_opacity = 0.05).add_to(m)

        #Plot Markers
        for lat, lon, elevation,name in zip(lat, lon, elevation,name):
            folium.CircleMarker(location=[lat, lon], radius = radius_size(elevation), popup=str(name), fill_color=color_change(elevation),color=color_change(elevation),  fill_opacity = 0.9).add_to(m)

        m=m._repr_html_() #updated


        context = {
            'installations': installations,
            'error':error,
            'my_map': m,
            # 'errvs': errvs,
            'title': "Multi-objective model"
        }

        return render(request,'main/multi.html',context)
    else:
        context = {
            'numner_vessels':list_numner_vessels,
            'title': "Multi-objective model"
        }
        return render(request,'main/multi2.html',context)

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)

                return redirect('login')


        context = {'form':form}
        return render(request, 'main/register.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password =request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {
            'title':'title'
        }
        return render(request, 'main/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def map(request):

    #creation of map comes here + business logic
    m = folium.Map([62.354457, 2.377184], zoom_start=6)

    lat_list_inst = []
    lon_list_inst = []
    elev_list_inst = []
    for e in Installation.objects.all():
        lat_list_inst.append(e.latitude)
        lon_list_inst.append(e.longitude)
        elev_list_inst.append(1)

    lat_inst = pd.Series(lat_list_inst)
    lon_inst = pd.Series(lon_list_inst)
    elevation_inst = pd.Series(elev_list_inst)

    #Function to change colors
    def color_change(elev):
        if(elev == 1 ):
            return('#3f7fff')
        elif(elev == 201):
            return('#ffda25')
        elif(elev == 202):
            return('#ff7a2f')
        elif(elev == 203):
            return('#55cb68')
        elif(elev == 204):
            return('#f8b5f5')
        elif(elev == 205):
            return('#bf6bc7')
        elif(elev == 210):
            return('#fcffd0')


    lat_list_errv = []
    lon_list_errv = []
    elev_list_errv = []
    for e in ERRV.objects.all():
        lat_list_errv.append(e.latitude)
        lon_list_errv.append(e.longitude)
        if(e.type_solution == 201.0):
            elev_list_errv.append(201)
        elif (e.type_solution == 210.0):
            elev_list_errv.append(210)
        elif (e.type_solution == 202.0):
            elev_list_errv.append(202)
        elif (e.type_solution == 203.0):
            elev_list_errv.append(203)
        elif (e.type_solution == 204.0):
            elev_list_errv.append(204)
        elif (e.type_solution == 205.0):
            elev_list_errv.append(205)

    lat_errv = pd.Series(lat_list_errv)
    lon_errv = pd.Series(lon_list_errv)
    elevation_errv = pd.Series(elev_list_errv)
    print("lat_errv=",lat_errv)
    print("lon_errv=",lon_errv)
    print("elevation_errv=",elevation_errv)


    #Plot Markers
    for lat, lon, elevation in zip(lat_inst, lon_inst, elevation_inst):
        folium.CircleMarker(location=[lat, lon], radius = 5, popup=str(lat)+" m", fill_color=color_change(elevation),color=color_change(elevation),  fill_opacity = 1).add_to(m)

    for lat, lon, elevation in zip(lat_errv, lon_errv, elevation_errv):
        folium.CircleMarker(location=[lat, lon], radius = 5, popup=str(elevation)+" m", fill_color=color_change(elevation),color=color_change(elevation),  fill_opacity = 1).add_to(m)

    m=m._repr_html_() #updated
    context = {'my_map': m}

    return render(request,'main/map.html',context)

    # context = {
    #     'title':'Map'
    # }
    # #creation of map comes here + business logic
    # m = folium.Map([62.354457, 2.377184], zoom_start=6)
    #
    #
    # #Load Data
    # data = pd.read_csv('main\\recources\\Data_Map.txt')
    # # lat = data['LAT']
    # #lon = data['LON']
    # elevation = data['ELEV']
    #
    # lat_list = []
    # lon_list = []
    # for e in Installation.objects.all():
    #     lat_list.append(e.latitude)
    #     lon_list.append(e.longitude)
    #
    #
    # lat = pd.Series(lat_list)
    # lon = pd.Series(lon_list)
    #
    # #Function to change colors
    # def color_change(elev):
    #     if(elev == 1 ):
    #         return('green')
    #     elif(elev == 2):
    #         return('yellow')
    #     elif(elev == 3):
    #         return('green')
    #
    # #Function to change colors
    # def radius_change(elev):
    #     if(elev == 3 ):
    #         return 62050
    #     elif(elev == 5):
    #         return 124100
    #     elif(elev == 6):
    #         return 155125
    #
    #
    # data2 = pd.read_csv("main\\recources\\Data_Map_ERRV.txt")
    # lat2 = data2['LAT']
    # lon2 = data2['LON']
    # elevation2 = data2['ELEV']
    #
    # for lat2, lon2, elevation2 in zip(lat2, lon2, elevation2):
    #     folium.Circle(location=[lat2, lon2], radius = radius_change(elevation2), popup=str(elevation2)+" m", fill_color='green',  fill_opacity = 0.2).add_to(m)
    #
    # #Plot Markers
    # for lat, lon, elevation in zip(lat, lon, elevation):
    #     folium.CircleMarker(location=[lat, lon], radius = 5, popup=str(lat)+" m", fill_color=color_change(elevation),  fill_opacity = 0.9).add_to(m)
    #
    # #Plot Markers
    # # for lat, lon, elevation in zip(lat, lon, elevation):
    # #     folium.Circle(location=[lat, lon], radius = radius_change(elevation), popup=str(elevation)+" m", fill_color=color_change(elevation),  fill_opacity = 0.2).add_to(m)
    #
    # m=m._repr_html_() #updated
    # context = {'my_map': m}
    #
    #
    # #return render(request, 'polls/show_folium_map.html', context)
    # return render(request,'main/map.html',context)

@login_required(login_url='login')
def riskv2(request):
    print("Riskv2")
    return render(request,'main/riskv2.html')