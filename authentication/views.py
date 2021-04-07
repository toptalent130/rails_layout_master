
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.forms.utils import ErrorList
from django.http import HttpResponse
from .forms import LoginForm, SignUpForm
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer
from .models import query_users_by_args

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def list(self, request, **kwargs):
        try:
            user = query_users_by_args(**request.query_params)
            serializer = UserSerializer(user['items'], many=True)
            result = dict()
            result['data'] = serializer.data
            result['draw'] = user['draw']
            result['recordsTotal'] = user['total']
            result['recordsFiltered'] = user['count']
            return Response(result, status=status.HTTP_200_OK, template_name=None, content_type=None)

        except Exception as e:
            return Response(e, status=status.HTTP_404_NOT_FOUND, template_name=None, content_type=None)

def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:    
                msg = 'Invalid credentials ' + str(username)  + ' ' + str(password) + '' + str(user) 
        else:
            msg = 'Error validating the form'    
    return render(request, "accounts/login.html", {"form": form, "msg" : msg})

def register_user(request):
    msg = None
    success = False
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            success = True
            return redirect("/login/")
        else:
            msg = 'Form is not valid'    
    else:
        form = SignUpForm()
    return render(request, "accounts/register.html", {"form": form, "msg" : msg, "success" : success })
def add_user(request):
    msg     = None
    success = False
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            msg = 'User created'
            success = True
            return redirect("/")
        else:
            msg = 'Form is not valid'    
    else:
        form = SignUpForm()

    return render(request, "accounts/add_user.html", {"form": form, "msg" : msg, "success" : success })

