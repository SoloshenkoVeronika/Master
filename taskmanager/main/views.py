from msilib import Binary

from django.shortcuts import render,redirect
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
    errvs = ERRV.objects.order_by('id')
    print("===",errvs)

    return render(request,'main/about.html',{'title':'about','installations': installations,'errvs': errvs})

def create(request):
    # error = ''
    # if  request.method == 'POST':
    #     form = TaskForm(request.POST)
    #     if form.is_valid():
    #         form.save()
    #         return redirect('home')
    #     else:
    #         error = 'Form is not valide'
    #
    #
    # form = TaskForm()
    # context = {
    #     'form': form,
    #     'error':error
    # }
    return render(request,'main/create.html')


def installation(request):
    error = ''
    if  request.method == 'POST':
        form = InstallationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            error = 'Form is not valide'


    form = InstallationForm()
    context = {
        'form': form,
        'error':error
    }
    return render(request,'main/installation.html',context)

def errv(request):
    error = ''
    if  request.method == 'POST':
        form = ERRVForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            error = 'Form is not valide'


    form = ERRVForm()
    context = {
        'form': form,
        'error':error
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
            model1(grid)
            model_risk()

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