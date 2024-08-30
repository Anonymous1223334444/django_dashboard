from django.contrib import admin
from core import models


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('amount', 'date', 'description', 'owner', 'category')
    search_field = ('amount', 'date', 'description', 'owner', 'category')

    list_per_page = 5

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_field = ('name',)

    list_per_page = 5

admin.site.register(models.Expense, ExpenseAdmin)
admin.site.register(models.Category, CategoryAdmin)