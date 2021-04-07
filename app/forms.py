from django import forms  
from authentication.models import User
from .models import TradeAccount

class UserForm(forms.ModelForm):  
    class Meta:  
        model = User  
        fields = ['username', 'email', 'role', 'trade_account'] #https://docs.djangoproject.com/en/3.0/ref/forms/widgets/
        widgets = { 
            'username': forms.TextInput(attrs={ 'class': 'form-control' }), 
            'email': forms.EmailInput(attrs={ 'class': 'form-control' }),
            'role': forms.TextInput(attrs={ 'class': 'form-control' }),
            'trade_account': forms.Select(attrs={ 'class': 'form-control' }),
            # 'password': forms.TextInput(attrs={ 'class': 'form-control', 'type':'password' }),
        }
class TradeAccountForm(forms.Form):
    value = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Name",                
                "class": "form-control",
                "require":"true"
            }
        ))
    key = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Key",                
                "class": "form-control",
                "require":"true"
            }
        ))
    class Meta:
        model = TradeAccount
        fields = ('key', 'value')
