
from django import forms

class QuoteForm(forms.Form):
    name = forms.CharField(max_length=120)
    phone = forms.CharField(max_length=30)
    email = forms.EmailField(required=False)
    service = forms.CharField(max_length=120)
    message = forms.CharField(widget=forms.Textarea, required=False)
    # honeypot - should be hidden on the page
    company = forms.CharField(required=False)