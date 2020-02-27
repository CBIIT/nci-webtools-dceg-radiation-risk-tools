
from django.shortcuts import render
from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _

from .forms import ContactForm

def contact(request):
    user_message = None
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            send_mail(subject, message, sender, (settings.MANAGERS[0][1],))
            user_message = _('Thank you. We will respond as soon as possible.')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form, 'manager_email': settings.MANAGERS[0][1], 'user_message' : user_message })