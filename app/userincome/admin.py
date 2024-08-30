from django.contrib import admin
from userincome import models


class UserIncomeAdmin(admin.ModelAdmin):
    list_display = ('amount', 'date', 'description', 'owner', 'source')
    search_field = ('amount', 'date', 'description', 'owner', 'source')

    list_per_page = 5

class SourceAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_field = ('name',)

    list_per_page = 5

admin.site.register(models.UserIncome, UserIncomeAdmin)
admin.site.register(models.Source, SourceAdmin)