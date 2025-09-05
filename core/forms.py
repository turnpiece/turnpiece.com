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
    
    # Honeypot field - hidden from users but visible to bots
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'style': 'display:none;',
            'tabindex': '-1',
            'autocomplete': 'off'
        })
    )
    
    def clean_website(self):
        """Check if honeypot field was filled (indicates bot)"""
        website = self.cleaned_data.get('website')
        if website:
            raise forms.ValidationError("Bot detected")
        return website