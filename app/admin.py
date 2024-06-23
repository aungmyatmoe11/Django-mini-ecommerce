from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.auth.models import Group
from .models import Product, Category, Customer, Cart, Order


# Register your models here.
# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     def image_tag(self, obj):
#         return format_html(
#             '<img src="{}" style="max-width:200px; max-height:200px"/>'.format(
#                 obj.image.url
#             )
#         )

#     list_display = ["name", "image_tag"]

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'phone']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'products', 'quantity']
    def products(self,obj):
        link = reverse("admin:app_product_change", args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', link, obj.product.name)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_quantity', 'total_amount', 'tracking_code', 'ordered_at']



class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id',"name", "image_tag"]
    readonly_fields = ["image_tag"]

    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:150px; max-height:150px"/>'.format(
                    obj.image.url
                )
            )
        return "-"

    image_tag.short_description = "Image Preview"

    def save_model(self, request, obj, form, change):
        if "image" in form.changed_data and obj.image:
            # Add custom save logic if needed
            pass
        super().save_model(request, obj, form, change)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id',"name", "price", "stock", "available", "image_tag"]
    readonly_fields = ["image_tag"]

    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:150px; max-height:150px"/>'.format(
                    obj.image.url
                )
            )
        return "-"

    image_tag.short_description = "Image Preview"

    def save_model(self, request, obj, form, change):
        if "image" in form.changed_data and obj.image:
            # Add custom save logic if needed
            pass
        super().save_model(request, obj, form, change)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)

admin.site.unregister(Group)