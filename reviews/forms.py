from django import forms
from .models import Review


class SellerResponseForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['seller_response', 'approved']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
