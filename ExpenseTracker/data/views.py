from datetime import datetime
from django.shortcuts import render, redirect
from .models import Entry, EntryTag
from .forms import AddEntryFormFunc, UpdateEntryFormFunc, AddEntryTagForm, AddEntryForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django.db.models import Sum
import itertools
from django.http import JsonResponse
import random
from django.core import serializers
from rest_framework.views import APIView
from rest_framework.response import Response

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
        context['total'] = Entry.objects.filter(
            user=self.request.user.profile).aggregate(Sum('price'))
        return context

    def post(self, request, *args, **kwargs):  # Post request
        entryform = AddEntryForm(request.POST)
        if entryform.is_valid():
            data = entryform.cleaned_data
            title = data['title']
            price = data['price']
            tags = data['tags']
            user = request.user.profile
            entry = Entry(title=title, price=price, user=user)
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
        context['form'] = UpdateEntryFormFunc(self.request.user.profile, entry.title, entry.price, tagids)
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
            context['total'] += entry.price
        context['total'] = round(context['total'], 2)
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
                tagtotal[tag.tag][0] += i.price
                tagtotal[tag.tag][1] += 1
            except:
                tagtotal[tag.tag] = [i.price,1]
    tagtotal = {k: v for k, v in sorted(tagtotal.items(), key=lambda item: item[1], reverse=True)} #sort by tag value
    return (tagtotal) #{tag:[totalamountspent, frequency]}

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
    print(timeperiod)
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

