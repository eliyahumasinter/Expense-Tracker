from datetime import datetime
from django.shortcuts import render, redirect

from users.models import Profile
from .models import Entry, EntryTag
from .forms import AddEntryFormFunc, UpdateEntryFormFunc, AddEntryTagForm, AddEntryForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django.db.models import Sum
import itertools
from django.http import JsonResponse
import random, json
from django.core import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from ExpenseTracker.secrets import *
import requests

class DataListView(LoginRequiredMixin, ListView):  # home
    model = Entry
    template_name = 'data/home.html'
    context_object_name = 'data'
    ordering = ['-date_posted']
    # paginate_by = 25

    def get_queryset(self):
        return Entry.objects.filter(user=self.request.user.profile)

    def get_context_data(self, **kwargs):
        context = super(DataListView, self).get_context_data(**kwargs)
        context['AddEntryForm'] = AddEntryFormFunc(self.request.user.profile)
        context['AddTagForm'] = AddEntryTagForm()
        context['tagtotal'] = getTagTotal(user=self.request.user.profile)
        context['total'] = getTotal(user=self.request.user.profile)
        return context

    def post(self, request, *args, **kwargs):  # Post request
        entryform = AddEntryForm(request.POST)
        if entryform.is_valid():
            data = entryform.cleaned_data
            title = data['title']
            price = data['price']
            tags = data['tags']
            currency = request.user.profile.default_currency
            notes = "You may add notes about this entry"
            user = request.user.profile
            entry = Entry(title=title, price=price, user=user, currency=currency, notes=notes)
            entry.save()
            entry.tags.set(tags)

        tagform = AddEntryTagForm(request.POST)
        if tagform.is_valid():
            data = tagform.cleaned_data
            tag = data['tag']
            user = request.user.profile
            entry = EntryTag(tag=tag, user=request.user.profile)
            entry.save()

        return redirect("data-home")


class DataDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Entry

    def test_func(self):
        entry = self.get_object()
        if self.request.user.profile == entry.user:
            return True
        else:
            return False


class DataDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Entry
    success_url = '/'

    def test_func(self):
        entry = self.get_object()
        if self.request.user.profile == entry.user:
            return True
        else:
            return False


class DataUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Entry

    fields = ['title', 'price', 'currency', 'notes', 'tags']
    success_url = '/'

    def get_queryset(self):
        return Entry.objects.filter(user=self.request.user.profile)

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        entry = Entry.objects.filter(id=self.object.id).first()
        tagids = entry.tags.values_list('id')
        tagids = set(entry[0] for entry in tagids)
        context = super(DataUpdateView, self).get_context_data(**kwargs)
        context['entry'] =  Entry.objects.filter(id=self.object.id).first()
        context['form'] = UpdateEntryFormFunc(self.request.user.profile, entry.title, entry.price, tagids, entry.currency)
        return context

    def test_func(self):
        entry = self.get_object()
        if self.request.user.profile == entry.user:
            return True
        else:
            return False


class TagDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = EntryTag
    template_name = 'data/tag_detail.html'
    context_object_name = 'tag'

    total = 0

    def get_context_data(self, *args, **kwargs):
        context = super(TagDetailView, self).get_context_data(*args, **kwargs)
        context['total'] = 0
        for entry in (context['object'].entry_set.all()):
            context['total'] += convertCurrency(entry.price, entry.currency)
        context['total'] = round(context['total'], 2)
        context['chartids'] = json.loads(tagdetaildata(self.request, context['object'].pk).content)['entriesovertime']       
        return context


    def test_func(self):
        entry = self.get_object()
        if self.request.user.profile == entry.user:
            return True
        else:
            return False


def getTagTotal(user, timeperiod=None): #Implement the timeperiod
    tagtotal = {}  # tag:total_cost
    tags = EntryTag.objects.filter(user=user)
    for tag in tags:
        for i in tag.entry_set.all():
            try:
                tagtotal[tag.tag][0] += convertCurrency(i.price, i.currency)
                tagtotal[tag.tag][1] += 1
            except:
                tagtotal[tag.tag] = [convertCurrency(i.price, i.currency),1]

    tagtotal = {k: v for k, v in sorted(tagtotal.items(), key=lambda item: item[1], reverse=True)} #sort by tag value
    return (tagtotal) #{tag:[totalamountspent, frequency]}
                    
def getTotal(user, timeperiod=None):
    total = 0
    entries = Entry.objects.filter(user=user)
    for entry in entries:
        total += convertCurrency(entry.price, entry.currency)
    return total
                
def mostFrequentTag(taglist):
	largest = 0
	topkey = None
	for key, val in taglist.items():
		if val[1] > largest:
			largest= val[1]
			topkey = key
	if topkey:
		return (topkey, largest)
	else:
		return False #if no entries have been provided

class ChartData(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        labels = ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange']
        myvalues = [random.randint(1,10) for i in range(6)]
        data = {
            "mylabels":labels,
            "myvalues": myvalues
        }
        return Response(data)
    


def charts(request, timeperiod):
    now = datetime.now()
    thismonth = now.replace(day=1)
    entriesfrompastmonth=request.user.profile.entry_set.filter(date_posted__range=[str(thismonth), str(now)])
    totalspentpastmonth=entriesfrompastmonth.aggregate(Sum('price'))
    entriesfrompastmonth = serializers.serialize('json', entriesfrompastmonth)
    
    tagtotals = getTagTotal(user=request.user.profile)
    mostfrequenttag = mostFrequentTag(tagtotals)
    data = {
        "entriesfrompastmonth": entriesfrompastmonth,
        "totalspentpastmonth": totalspentpastmonth,
        "tagtotals":tagtotals,
        "mostfrequenttag":mostfrequenttag
    }

    # For each tag, I want to be able to see how much was spent on that tag overtime, which months/weeks had the highest usage
    # Rank each tag by most spent
    # Rank each tag by frequency of use

    return JsonResponse({"data":data})
    #return render(request, "data/charts.html", context=context)

def tagdetaildata(request, pk):
    tag = request.user.profile.entrytag_set.filter(pk=pk).first()
    totalEntries = len(tag.entry_set.all())
    entriesPerYear = {}
    for entry in tag.entry_set.all().order_by("date_posted"):
        if entry.date_posted.year not in entriesPerYear:
            entriesPerYear[entry.date_posted.year]={'total':1}
        else:
            entriesPerYear[entry.date_posted.year]['total']+=1
            
        if entry.date_posted.strftime("%b") not in entriesPerYear[entry.date_posted.year]:
            entriesPerYear[entry.date_posted.year][entry.date_posted.strftime("%b")] = 1
        else:
             entriesPerYear[entry.date_posted.year][entry.date_posted.strftime("%b")] += 1

    year = datetime.now().year
    months = {}
    costOfEntries = {}
    for entry in tag.entry_set.all().order_by("date_posted"):
        if entry.date_posted.strftime("%b %d, %Y") not in costOfEntries:
            costOfEntries[entry.date_posted.strftime("%b %d, %Y")] = convertCurrency(entry.price, entry.currency)
            months[entry.date_posted.strftime("%b %Y")] = entry.price
        else:
            costOfEntries[entry.date_posted.strftime("%b %d, %Y")] += convertCurrency(entry.price, entry.currency)
            months[entry.date_posted.strftime("%b %Y")] += entry.price
            
   
    data = {
        "totalentries": totalEntries,
        "entriesovertime": entriesPerYear ,
        "costofentries": costOfEntries,
        "months": months
    }

    return JsonResponse(data)



def convertCurrency(price, currency):
    #url = f"https://freecurrencyapi.net/api/v2/latest?apikey={curencyapikey}"
    #response = json.loads(requests.get(url).content)['data']

    if currency == "USD":
        return price
    else:
        return round((1/currency_data[currency])*price, 2)
        