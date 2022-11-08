from django.contrib import admin

from .models import Product, Category


class ProductAdmin(admin.StackedInline):
    model = Product
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class CatAdmin(admin.ModelAdmin):
    inlines = [ProductAdmin]
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class Adminj(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
