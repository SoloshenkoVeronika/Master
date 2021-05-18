from .models import Installation,ERRV
from django.forms import ModelForm, TextInput, Textarea, MultipleChoiceField, Select, CharField, ModelChoiceField, forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.forms.widgets import NumberInput

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class InstallationForm(ModelForm):
    class Meta:
        model = Installation
        fields = ["title","latitude","longitude","r_time","number_of_people","prob_accident"]
        labels = {'text':'latitude'}
        widgets = {
            "title":TextInput(attrs={
                'class':'form-control',
                # 'placeholder':"Enter title"
            }),
            "latitude":TextInput(attrs={
                'class':'form-control',
                # 'placeholder':"Enter Latitude"
            }),
            "longitude":TextInput(attrs={
                'class':'form-control',
                # 'placeholder':"Enter Longitude"
            }),
            "r_time":TextInput(attrs={
                'class':'form-control',
                # 'placeholder':"Enter Time Requirement"
            }),
            "number_of_people":TextInput(attrs={
                'class':'form-control',
                # 'placeholder':"Enter enter the number of people on the installation"
            }),
            "prob_accident":TextInput(attrs={
                'class':'form-control',
                # 'placeholder':"Enter the probability of accident"
            }),
        }

POSITION_CHOICES= [
    ('201', 'Current position'),
    ('210', 'Potential position'),
]


class ERRVForm(ModelForm):
   class Meta:
        model = ERRV
        fields = ["title","latitude","longitude","type_solution"]
        widgets = {
            "title":TextInput(attrs={
                'class':'form-control',
                # 'placeholder':"Enter title"
            }),
            "latitude":TextInput(attrs={
                'class':'form-control',
                # 'placeholder':"Enter latitude"
            }),
            "longitude":TextInput(attrs={
                'class':'form-control',
                # 'placeholder':"Enter longitude"
            }),
            "type_solution": Select(choices  = POSITION_CHOICES)


        }

class ExampleForm(forms.Form):
    date = forms.DateField(widget=NumberInput(attrs={'type': 'date'}))
    # period = forms.TextInput(attrs={'class':'form-control' })