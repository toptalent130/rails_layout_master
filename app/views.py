# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import os
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
from django.db.models import Q
# from app.ocm.ocm_v2 import run 
from authentication.models import User
from .models import TradeAccount, UserTradeAccount
from .forms import UserForm, UserForm_1, TradeAccountForm
import pandas as pd
from authentication.forms import SignUpForm

from django.conf import settings
from django.core.files.storage import FileSystemStorage
@login_required(login_url="/login/")

def loadcsvtodf(directory, filename):
    my_file = Path(directory+filename)
    if my_file.is_file():
        print('File {} found.'.format(filename))
        result = pd.read_csv(my_file)
        if result.empty:
            print('File {} empty.'.format(filename))
        else:
            print('File {} values loaded.'.format(filename))
    else:
        result = pd.DataFrame() 
        print('File {} NOT found !!!'.format(filename))
    return result
@login_required(login_url="/login/")
def index(request):
    path="\\home\\stock-management-django\\app\\ocm_data\\TW\\SPX\\"  # insert the path to your directory   
    spx_list =os.listdir(path)
    uploaded_file_url=''
    if request.method == 'POST' and bool(request.FILES.get('myfile', False)) == True:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
    context = {}
    context['segment'] = 'index'
    all_users = User.objects.filter()
    all_users_count = all_users.count()
    totaluser = UserTradeAccount.objects.filter(Q(role = "User")).count()
    totalmanager = UserTradeAccount.objects.filter(Q(role = "Manager")).count()
    totalaccount = TradeAccount.objects.filter().count()
    all_users_trades = []
    for ele in UserTradeAccount.objects.filter():
        id = ele.id
        username = User.objects.filter(Q(id=ele.user_id))[0].username
        email = User.objects.filter(Q(id=ele.user_id))[0].email
        last_login = User.objects.filter(Q(id=ele.user_id))[0].last_login
        role = ele.role
        trade_account_id = ele.trade_account_id
        trade_account_key = TradeAccount.objects.filter(Q(id=ele.trade_account_id))[0].key
        trade_account_value = TradeAccount.objects.filter(Q(id=ele.trade_account_id))[0].value
        all_users_trades.append({"id":id,"username":username,"email":email,"role":role,"trade_account_key":trade_account_key,"trade_account_value":trade_account_value,"trade_account_id":trade_account_id})
    accounts = TradeAccount.objects.filter()
    current_user_all_trades = UserTradeAccount.objects.filter(Q(user_id=request.user.id))
    trade_values = ['Paper']
    trade_keys = ['x1234']
    trade_roles = ['Manager']
    for each in current_user_all_trades:
        trade_values.append(TradeAccount.objects.filter(Q(id=each.trade_account_id))[0].value)
        trade_keys.append(TradeAccount.objects.filter(Q(id=each.trade_account_id))[0].key)
        trade_roles.append(each.role)
    current_user = pd.DataFrame({'Key': trade_keys, 'Value': trade_values, 'Role': trade_roles}, columns=['Key','Value','Role']) 
    current_user.to_csv('\\home\\stock-management-django\\app\\ocm_data\\TradeAccounts\\current_user.csv', mode='w', header=True, index=False)

    context = {'spx_list': spx_list, 'uploaded_file_url': uploaded_file_url, 'all_users': all_users,'all_users_trades': all_users_trades, "accounts": accounts, 'totaluser':totaluser, 'totalmanager':totalmanager, 'totalaccount':totalaccount, 'all':all_users_count }
    context['segment'] = 'user'
    html_template = loader.get_template( 'index.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        
        load_template      = request.path.split('/')[-1]
        context['segment'] = load_template
        
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
        
    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:
    
        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))
@login_required(login_url="/login/")
def edit(request, id):  
    user = User.objects.get(id=id)  
    return render(request,'edit.html', {'user':user})  
@login_required(login_url="/login/")
def update(request, id):  
    temper = UserTradeAccount.objects.filter(id=id)
    filter_2 = []
    valid = True
    # if temper[0].trade_account_id == int(request.POST["trade_account"]) and temper[0].role == request.POST["role"]:
    #     valid = False
    # if valid == True:
    temper.update(trade_account_id=int(request.POST["trade_account"]), role=request.POST["role"])
    # if len(request.POST) == 5:
    #     form = UserTradeAccountForm(request.POST, instance = user)
    #     if form.is_valid():  
    #         form.save()  
    # else:
    #     tem = request.POST.dict()
    #     tem["trade_account"] = "[]" 
    #     form = UserForm_1(tem, instance = user)
    #     form.save()
    return redirect("/") 
@login_required(login_url="/login/")
def destroy(request, id):  
    account = UserTradeAccount.objects.get(id=id)  
    account.delete()  
    return redirect("/")  
@login_required(login_url="/login/")
def destroy_user(request, id):  
    UserTradeAccount.objects.filter(user_id=id).delete()
    User.objects.get(id=id).delete()
    return redirect("/") 
@login_required(login_url="/login/")
def destroy_account(request, id):  
    UserTradeAccount.objects.filter(trade_account_id=id).delete()
    TradeAccount.objects.get(id=id).delete()
    return redirect("/")   
@login_required(login_url="/login/")
def add_trade_account(request):
    msg = None
    success = False
    if request.method == "POST":
        form = TradeAccountForm(request.POST)
        if form.is_valid():
            key = form.cleaned_data.get("key")
            value = form.cleaned_data.get("value")
            if len(TradeAccount.objects.filter(value=value)) == 0:
                tradeAccount = TradeAccount(value=value, key=key)
                tradeAccount.save()
                success = True
                accounts = TradeAccount.objects.filter()
                keys = [ account.key for account in accounts ]
                values = [ account.value for account in accounts ]
                trade_accounts = pd.DataFrame({'Key': keys, 'Value': values}, columns=['Key','Value']) 
                trade_accounts.to_csv('\\home\\stock-management-django\\app\\ocm_data\\TradeAccounts\\trade_accounts.csv', mode='w', header=True, index=False)
                return redirect("/")
            else:
                success = False
                msg = "Account is already exist"
                form = TradeAccountForm()
                return render(request, "accounts/trade_account.html", {"form": form, "msg" : msg, "success" : success })
        else:
            msg = 'Account is not valid'    
    else:
        form = TradeAccountForm()
    return render(request, "accounts/trade_account.html", {"form": form, "msg" : msg, "success" : success })
