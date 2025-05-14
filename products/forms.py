from django import forms
from products.models import Product, ProductVariant
from django.forms import inlineformset_factory


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'category']


class VariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['color', 'size', 'price', 'stock', 'image']


VariantFormSet = inlineformset_factory(
    Product,
    ProductVariant,
    form=VariantForm,
    extra=1,            # сколько пустых строк добавить для нового варианта
    can_delete=True     # позволит отмечать вариант на удаление
)
