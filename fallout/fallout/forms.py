
from django import forms
from django.utils.translation import ugettext_lazy as _

class ContactForm(forms.Form):
    subject = forms.CharField(label=_('Subject'), max_length=100, required=True, widget=forms.TextInput(attrs={'size':55}))
    message = forms.CharField(label=_('Comment'), required=True, widget=forms.Textarea(attrs={'cols': '50', 'rows': '7'}))
    sender = forms.EmailField(label=_('Your e-mail address'), required=True, widget=forms.TextInput(attrs={'size':55}))
