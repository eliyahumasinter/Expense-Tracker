from locale import currency
from django import forms
from .models import Entry, EntryTag


def AddEntryFormFunc(user):
    class AddEntryForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(AddEntryForm, self).__init__(*args, **kwargs)
            self.fields['tags'].label = ""
        title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Title'}))
        price = forms.FloatField(widget=forms.TextInput(attrs={'placeholder': '$'}))
        tags = forms.ModelMultipleChoiceField(
            queryset=EntryTag.objects.filter(user=user),
            widget=forms.CheckboxSelectMultiple,
            required=False)

        class Meta:
            model = Entry
            fields = ['title', 'price', 'tags']

    return AddEntryForm


class AddEntryForm(forms.ModelForm):
    title = forms.CharField()
    price = forms.FloatField()
    
    tags = forms.ModelMultipleChoiceField(
        queryset=EntryTag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False)

    class Meta:
        model = Entry
        fields = ['title', 'price', 'tags']

def UpdateEntryFormFunc(user, entrytitle, entryprice, tagids):
    class UpdateEntryForm(forms.ModelForm):
        Currencies= [
        ('ILS', 'ILS'),
        ('USD', 'USD')]
        title = forms.CharField(widget=forms.TextInput(attrs={"value":entrytitle}))
        price = forms.FloatField(widget=forms.TextInput(attrs={"value":entryprice}))
        tags = forms.ModelMultipleChoiceField(
            queryset=EntryTag.objects.filter(user=user),
            widget=forms.CheckboxSelectMultiple,
            required=False,
            initial=tagids)
        currency = forms.CharField(label='Choose a currency', widget=forms.Select(choices=Currencies))
        notes = forms.CharField(widget=forms.Textarea(attrs={"ID":"entrynotes"}))
        class Meta:
            model = Entry
            fields = ['title', 'price', 'currency','tags', 'notes']

    return UpdateEntryForm

class AddEntryTagForm(forms.ModelForm):
    tag = forms.CharField()

    class Meta:
        model = EntryTag
        fields = ['tag']
