from django import forms

class ContactForm(forms.Form):
    INPUT_CLASSES = 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-gray-500 focus:border-gray-500'

    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': INPUT_CLASSES})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': INPUT_CLASSES})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': INPUT_CLASSES})
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