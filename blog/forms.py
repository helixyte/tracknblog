# blog/forms.py
from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    parent = forms.ModelChoiceField(
        queryset=Comment.objects.all(),
        widget=forms.HiddenInput,
        required=False
    )
    
    # Honeypot field - bots will fill this out, but humans shouldn't
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'style': 'display:none;',  # Hide with CSS
            'tabindex': '-1',          # Remove from tab order
            'autocomplete': 'off'      # Disable autocomplete
        })
    )
    
    class Meta:
        model = Comment
        fields = ['name', 'content', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500', 
                'placeholder': 'Your name'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500', 
                'rows': 4, 
                'placeholder': 'Write your comment...'
            }),
        }
        labels = {
            'name': 'Name',
            'content': 'Comment',
        }