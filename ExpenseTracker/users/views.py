from email.policy import default
from zlib import DEF_BUF_SIZE
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from datetime import datetime, date
from django.db.models import Sum
from data.views import charts
from .forms import UpdateCurrencyForm

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            messages.success(
                request, f'You account has been created. You can now login')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})
import json


@login_required
def profile(request):
    if request.method == "POST":
        change_currency_form = UpdateCurrencyForm(request.POST, instance=request.user.profile)
        if change_currency_form.is_valid():
            change_currency_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
            
        # default_currency=request.POST['default_currency']
        # print(default_currency)
    else:
        change_currency_form = UpdateCurrencyForm(instance=request.user.profile)

        now = datetime.now()
        thismonth = now.replace(day=1)
        entriesfrompastmonth=request.user.profile.entry_set.filter(date_posted__range=[str(thismonth), str(now)])
        totalspentpastmonth=entriesfrompastmonth.aggregate(Sum('price'))  
        totalspent = request.user.profile.entry_set.aggregate(Sum('price'))  
        #jsondata = json.loads(charts(request,'hey').content)
        context = {
            "entriesfrompastmonth": entriesfrompastmonth,
            "totalspentpastmonth": totalspentpastmonth,
            "totalspent":totalspent,
            'change_currency_form': change_currency_form
            #"X":jsondata['data']
        }
        return render(request, 'users/profile.html', context=context)
