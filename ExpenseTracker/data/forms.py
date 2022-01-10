from django import forms
from .models import Entry, EntryTag


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
