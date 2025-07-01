from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full p-2 rounded bg-gray-100 border border-black focus:bg-white focus:outline-none'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full p-2 rounded bg-gray-100 border border-black focus:bg-white focus:outline-none'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full p-2 rounded bg-gray-100 border border-black focus:bg-white focus:outline-none'
        })
    )
