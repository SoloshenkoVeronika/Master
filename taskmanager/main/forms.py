from .models import Installation,ERRV
from django.forms import ModelForm, TextInput,Textarea
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# class TaskForm(ModelForm):
#     class Meta:
#         model = Task
#         fields = ["title","task"]
#         widgets = {
#             "title":TextInput(attrs={
#                 'class':'form-control',
#                 'placeholder':"Enter title"
#         }),
#             "task":Textarea(attrs={
#                 'class':'form-control',
#                 'placeholder':"Enter des"
#         }),
#         }

class InstallationForm(ModelForm):
    class Meta:
        model = Installation
        fields = ["title","latitude","longitude","r_time","number_of_people","prob_accident"]
        widgets = {
            "title":TextInput(attrs={
                'class':'form-control',
                'placeholder':"Enter title"
            }),
            "latitude":TextInput(attrs={
                'class':'form-control',
                'placeholder':"Enter latitude"
            }),
            "longitude":TextInput(attrs={
                'class':'form-control',
                'placeholder':"Enter longitude"
            }),
            "r_time":TextInput(attrs={
                'class':'form-control',
                'placeholder':"Enter r_time"
            }),
            "number_of_people":TextInput(attrs={
                'class':'form-control',
                'placeholder':"Enter number of people"
            }),
            "prob_accident":TextInput(attrs={
                'class':'form-control',
                'placeholder':"Enter probability of accident"
            }),
        }


class ERRVForm(ModelForm):
    class Meta:
        model = ERRV
        fields = ["title","latitude","longitude","prob"]
        widgets = {
            "title":TextInput(attrs={
                'class':'form-control',
                'placeholder':"Enter title"
            }),
            "latitude":TextInput(attrs={
                'class':'form-control',
                'placeholder':"Enter latitude"
            }),
            "longitude":TextInput(attrs={
                'class':'form-control',
                'placeholder':"Enter longitude"
            }),
            "prob":TextInput(attrs={
                'class':'form-control',
                'placeholder':"Enter prob"
            }),

        }