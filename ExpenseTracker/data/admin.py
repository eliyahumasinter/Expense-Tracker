from django.contrib import admin

# Register your models here.
from .models import Entry, EntryTag


#Note needed for many to many relationship
# class EntryTagAdmin(admin.StackedInline):
#     model = EntryTag


# @admin.register(Entry)
# class EntryAdmin(admin.ModelAdmin):
#     inlines = [EntryTagAdmin]

#     class Meta:
#         model = Entry


# @admin.register(EntryTag)
# class EntryTagAdmin(admin.ModelAdmin):
#     pass


admin.site.register(Entry)
admin.site.register(EntryTag)
