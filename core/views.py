from django.shortcuts import render
from django.core.mail import send_mail
from .forms import ContactForm

def contact_view(request):
    submitted = False
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # Replace below with actual email config
            send_mail(
                subject=f"Support message from {cd['name']}",
                message=cd['message'],
                from_email=cd['email'],
                recipient_list=["you@example.com"],
            )
            submitted = True
            form = ContactForm()  # clear form after submission
    else:
        form = ContactForm()
    return render(request, "core/contact.html", {"form": form, "submitted": submitted})
