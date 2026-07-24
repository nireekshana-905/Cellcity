from django.contrib import admin
from .models import Brand, Product, ProductSpecification, Order, Feedback, Address

# Admin Panel Title
admin.site.site_header = "🚀 Cell City AI Admin Panel"
admin.site.site_title = "Cell City AI"
admin.site.index_title = "Welcome to Cell City Dashboard"


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'brand',
        'price',
        'battery',
        'camera',
        'launch_year',
        'stock_quantity',
        'is_available'
    )

    search_fields = (
        'name',
        'brand__name',
        'processor'
    )

    list_filter = (
        'brand',
        'launch_year',
        'is_available'
    )

    ordering = ('name',)


@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'name',
        'value'
    )

    search_fields = (
        'product__name',
        'name'
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id',
        'user',
        'total_cost',
        'order_date',
        'is_cancelled'
    )

    list_filter = (
        'is_cancelled',
        'order_date'
    )

    search_fields = (
        'order_id',
        'user__username'
    )


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'email',
        'created_at'
    )

    search_fields = (
        'name',
        'email'
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        'customer',
        'city',
        'state',
        'country'
    )

    search_fields = (
        'customer__username',
        'city'
    )

