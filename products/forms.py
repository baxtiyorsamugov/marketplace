from django import forms
from products.models import Product, Category, ProductVariant
from django.forms import inlineformset_factory


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'category', 'subcategory']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # по умолчанию — ни одной подкатегории
        self.fields['subcategory'].queryset = Category.objects.none()
        self.fields['subcategory'].required = False

        if 'category' in self.data:
            # POST: пользователь только что выбрал категорию
            try:
                cat_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = Category.objects.filter(parent_id=cat_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.category_id:
            # GET редактирование существующего товара — подгружаем его подкатегории
            self.fields['subcategory'].queryset = Category.objects.filter(parent_id=self.instance.category_id)


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
