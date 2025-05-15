from django import forms
from .models import Review


class SellerResponseForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['seller_response', 'approved']


class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [
        (5, "5"),
        (4, "4"),
        (3, "3"),
        (2, "2"),
        (1, "1"),
    ]
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "star-rating"}),
        label=""
    )

    class Meta:
        model = Review
        fields = ("rating", "text")
