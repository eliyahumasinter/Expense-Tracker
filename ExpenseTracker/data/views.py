from django.shortcuts import render, redirect
from .models import Entry, EntryTag
from .forms import AddEntryForm
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
#from django.http import HttpResponse


class DataListView(ListView):  # home
    model = Entry
    template_name = 'data/home.html'
    context_object_name = 'data'
    ordering = ['-date_posted']
    #paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super(DataListView, self).get_context_data(**kwargs)
        context['form'] = AddEntryForm()
        return context

    def post(self, request, *args, **kwargs):  # Post request
        form = AddEntryForm(request.POST)
        if form.is_valid():
            form.save()
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
