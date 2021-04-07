# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
from django.db.models import Q
# from app.ocm.ocm_v2 import run 
from authentication.models import User
from .models import TradeAccount
from .forms import UserForm, TradeAccountForm
import pandas as pd
from authentication.forms import SignUpForm
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
    context = {}
    context['segment'] = 'index'
    # users = User.objects.exclude(Q(is_superuser = 1))
    users = User.objects.filter()
    totalUser = User.objects.filter(Q(role = 1)).count()
    totalManager = User.objects.filter(Q(role = 2)).count()
    totalBlock = User.objects.filter(Q(role = 0)).count()
    totalAdmin = User.objects.filter(Q(is_superuser = 1)).count()
    # /// Set All Managers to CSV
    role = Q(role=2)
    managers = User.objects.filter(Q(role))
    managers_name = [ manager.username for manager in managers ]
    managers_pd = pd.DataFrame({'Name': managers_name}, columns=['Name']) 
    managers_pd.to_csv('E:\\Python\\ocm_project\\app\\ocm_data\\Managers\\managers.csv', mode='w', header=True, index=False)
    # /// Set All Trade Accounts to CSV
    accounts = TradeAccount.objects.filter()
    keys = [ account.key for account in accounts ]
    values = [ account.value for account in accounts ]
    keyvalues = [ {"id": str(account.id), "key": account.key, "value": account.value} for account in accounts ]
    trade_accounts = pd.DataFrame({'Key': keys, 'Value': values}, columns=['Key','Value']) 
    trade_accounts.to_csv('E:\\Python\\ocm_project\\app\\ocm_data\\TradeAccounts\\trade_accounts.csv', mode='w', header=True, index=False)
    # /// Current User
    account_filter = Q(id = request.user.trade_account)
    current_user_trade_account = TradeAccount.objects.filter(account_filter)
    user_key = current_user_trade_account[0].key
    user_value = current_user_trade_account[0].value
    current_user = pd.DataFrame({'Key': [user_key], 'Value': [user_value]}, columns=['Key','Value']) 
    current_user.to_csv('E:\\Python\\ocm_project\\app\\ocm_data\\TradeAccounts\\current_user_trade_account.csv', mode='w', header=True, index=False)

    form = SignUpForm()
    context = {'users':users, "accounts": keyvalues,  'addform':form, 'totalUser':totalUser, 'totalManager':totalManager, 'totalBlock':totalBlock, 'totalAdmin':totalAdmin }
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

def edit(request, id):  
    user = User.objects.get(id=id)  
    return render(request,'edit.html', {'user':user})  

def update(request, id):  
    user = User.objects.get(id=id)  
    form = UserForm(request.POST, instance = user)  
    if form.is_valid():  
        form.save()  
        # ///
        role = Q(role=2)
        managers = User.objects.filter(Q(role))
        managers_name = [ manager.username for manager in managers ]
        managers_pd = pd.DataFrame({'Name': managers_name}, columns=['Name']) 
        managers_pd.to_csv('E:\\Python\\ocm_project\\app\\ocm_data\\Managers\\managers.csv', mode='w', header=True, index=False)
        # /// 
        return redirect("/")  
    return render(request, 'edit.html', {'user': user, 'err':form.is_valid}) 
    
def destroy(request, id):  
    user = User.objects.get(id=id)  
    user.delete()  
    # ///
    role = Q(role=2)
    managers = User.objects.filter(Q(role))
    managers_name = [ manager.username for manager in managers ]
    managers_pd = pd.DataFrame({'Name': managers_name}, columns=['Name']) 
    managers_pd.to_csv('E:\\Python\\ocm_project\\app\\ocm_data\\Managers\\managers.csv', mode='w', header=True, index=False)
    # /// 
    return redirect("/")  

def add_trade_account(request):
    msg = None
    success = False
    if request.method == "POST":
        form = TradeAccountForm(request.POST)
        if form.is_valid():
            key = form.cleaned_data.get("key")
            value = form.cleaned_data.get("value")
            tradeAccount = TradeAccount(value=value, key=key)
            tradeAccount.save()
            success = True
            accounts = TradeAccount.objects.filter()
            keys = [ account.key for account in accounts ]
            values = [ account.value for account in accounts ]
            trade_accounts = pd.DataFrame({'Key': keys, 'Value': values}, columns=['Key','Value']) 
            trade_accounts.to_csv('E:\\Python\\ocm_project\\app\\ocm_data\\TradeAccounts\\trade_accounts.csv', mode='w', header=True, index=False)
            return redirect("/")
        else:
            msg = 'Account is not valid'    
    else:
        form = TradeAccountForm()
    return render(request, "accounts/trade_account.html", {"form": form, "msg" : msg, "success" : success })
