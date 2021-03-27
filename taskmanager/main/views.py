from msilib import Binary

from django.shortcuts import render,redirect
from django.urls import reverse

from .forms import InstallationForm,ERRVForm

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

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from django.contrib.auth.decorators import login_required

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
# Create your views here.

import shutil

import pyutilib.subprocess.GlobalData
pyutilib.subprocess.GlobalData.DEFINE_SIGNAL_HANDLERS_DEFAULT = False

def index(request):
    installations = Installation.objects.order_by('id')
    return render(request,'main/index.html',{'title':'Main page','installations': installations})

def about(request):
    installations = Installation.objects.order_by('id')
    # errvs = ERRV.objects.order_by('id')
    full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "recources")
    filename_results = "Model3terrv.sol"
    FileFullPathResults = os.path.join(full_path, filename_results)
    with open(FileFullPathResults, 'r') as f:
        for x in f:
            errvs = ERRV.objects.filter(id=int(x))
    # errvs = ERRV.objects.filter(id=2)
    errvs= ERRV.objects.filter(type_solution=201)
    #errvs = ERRV.objects.order_by('id')
    context = {
        'installations': installations,
        'errvs': errvs,
        'title':'about'
    }
    print("I=",installations)
    return render(request,'main/about.html',context)


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

def errv(request):
    answer = ''
    error = ''
    if  request.method == 'POST':
        form = ERRVForm(request.POST)
        if form.is_valid():
            form.save()
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

def m_avtime(request):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!m_risk")
    error = ''
    if  request.method == 'POST':

        grid = request.POST.get("grid", "")
        if len(grid) == 0:
            error = 'Number is not valide'
        else:
            model1(grid)
            model2()
            errvs= ERRV.objects.filter(type_solution=202)
            installations = Installation.objects.order_by('id')
        context = {
            'installations': installations,
            'error':error,
            'errvs': errvs,
            'title': "Minimizing average time"
        }
        return render(request,'main/avtime.html',context)
    else:
        context = {
            'title': "Minimizing average time"
        }
        return render(request,'main/avtime.html',context)

def m_wstime(request):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!m_risk")
    error = ''
    if  request.method == 'POST':

        grid = request.POST.get("grid", "")
        if len(grid) == 0:
            error = 'Number is not valide'
        else:
            model1(grid)
            model3()
            errvs= ERRV.objects.filter(type_solution=203)
            installations = Installation.objects.order_by('id')
        context = {
            'installations': installations,
            'errvs':errvs,
            'error':error,
            'title': "Worst-time minimization"
        }
        return render(request,'main/wstime.html',context)

    else:
        context = {
            'title': "Worst-time minimization"
        }
        return render(request,'main/wstime.html',context)

def m_risk(request):
    print("______________m_risk_____))))))))))))))))))))))))))))))")
    if  request.method == 'POST':
        grid = request.POST.get("grid", "")
        count_errv = model1(grid)
        full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "recources")
        filename = "Modelpotpos.dat"
        FileFullPath = os.path.join(full_path, filename)

        with open(FileFullPath) as f:
            m= [line.split() for line in f]
        print(m)
        print("type=",type(m))
        list = []
        errvs = ERRV()
        for i in range(int(count_errv)):
            errvs = ERRV(title="O4_" +str(m[i][0]), latitude=m[i][1],longitude=m[i][2],prob=0.001,type_solution=1001)
            list.append(i)
        print("m=",errvs)


        context = {
            'nv':list,
            'el':errvs.get_lat(),
            'title': "Risk22"
        }
        #return render(request,'main/risk2.html',context)
        return HttpResponseRedirect('risk2',context)

        #return redirect ('risk2',context)
    else:
        context = {
            'title': "Risk1"
        }
        return render(request,'main/risk.html',context)

def m_risk3(request):
    print("______________m_risk3))))))))))))))))))))))))))))))")
    if  request.method == 'POST':
        wr = request.POST.get("wr", "")
        wt = request.POST.get("wt", "")
        er = request.POST.get("er", "")
        risk1 = 0.1
        risk21 = 0.1
        risk22 = 0.3
        risk31 = 0.1
        risk32 = 0.2
        risk33 = 0.3
        risk4 = 0.5

        risk_list = []
        risk2 = 1 - (1-float(risk21))*(1-float(risk22))
        risk3 = 1 - (1-float(risk31))*(1-float(risk32))*(1-float(risk33))
        risk_sum = 1-(1-float(risk1))*(1-float(risk2))*(1-float(risk3))*(1-float(risk4))
        risk_list.append(risk_sum)
        risk_list.append(4)
        full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "recources")
        filename = "Probability0.txt"
        FileFullPath = os.path.join(full_path, filename)
        with open(FileFullPath, 'w') as f:
            for i in risk_list:
                f.write(str(i)+"\n")

        print("risk_list=",risk_list)

        model_risk(wr,wt)
        #model_risk(wr,wt)
        print("er=",er)
        context = {
            #'installations':installations,
            'title': "About"
        }
        return render(request,'main/risk2.html',context)
    else:
        context = {
            'title': "Risk2"
        }
        return render(request,'main/risk2.html',context)


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

        context = {}
        return render(request, 'main/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')