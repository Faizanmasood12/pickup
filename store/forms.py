from django import forms
from .models import ReviewRating


class ReveiwForm(forms.ModelForm):
    """This will create the form for reveiw."""
    class Meta:
        model = ReviewRating
        fields = ['rating', 'subject', 'review']