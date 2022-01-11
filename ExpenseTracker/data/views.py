from django.shortcuts import render, redirect
from .models import Entry, EntryTag
from .forms import AddEntryForm, AddEntryTagForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from django.db.models import Sum
# from django.http import HttpResponse


class DataListView(LoginRequiredMixin, ListView):  # home
    model = Entry
    template_name = 'data/home.html'
    context_object_name = 'data'
    ordering = ['-date_posted']
    # paginate_by = 25

    def get_queryset(self):
        return Entry.objects.filter(user=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super(DataListView, self).get_context_data(**kwargs)
        context['AddEntryForm'] = AddEntryForm()
        context['AddTagForm'] = AddEntryTagForm()
        context['tagtotal'] = getTagTotal(userid=self.request.user.id)
        context['total'] = Entry.objects.aggregate(Sum('price'))
        print(context['total'], 'total pricelkajsdflkadsj')
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


class DataDetailView(DetailView):
    model = Entry


class DataDeleteView(DeleteView):
    model = Entry
    success_url = '/'


class DataUpdateView(UpdateView):
    model = Entry
    fields = ['title', 'price', 'tags']
    success_url = '/'


class TagDetailView(DetailView):
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


def getTagTotal(userid, timeperiod="All"):
    tagtotal = {}  # tag:total_cost
    tags = EntryTag.objects.filter(user=userid)
    for tag in tags:
        for i in tag.entry_set.all():
            try:
                tagtotal[tag] += i.price
            except:
                tagtotal[tag] = i.price


    return (tagtotal)
