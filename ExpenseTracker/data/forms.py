from django import forms
from .models import Entry, EntryTag


def AddEntryFormFunc(id):
    class AddEntryForm(forms.ModelForm):

        title = forms.CharField()
        price = forms.FloatField()
        tags = forms.ModelMultipleChoiceField(
            queryset=EntryTag.objects.filter(user=id),
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

def UpdateEntryFormFunc(id, entrytitle, entryprice,tagids):
    class UpdateEntryForm(forms.ModelForm):
        title = forms.CharField(widget=forms.TextInput(attrs={"value":entrytitle}))
        price = forms.FloatField(widget=forms.TextInput(attrs={"value":entryprice}))
        email = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Email'}))
        tags = forms.ModelMultipleChoiceField(
            queryset=EntryTag.objects.filter(user=id),
            widget=forms.CheckboxSelectMultiple,
            required=False,
            initial=tagids)

        class Meta:
            model = Entry
            fields = ['title', 'price', 'tags']

    return UpdateEntryForm

class AddEntryTagForm(forms.ModelForm):
    tag = forms.CharField()

    class Meta:
        model = EntryTag
        fields = ['tag']
