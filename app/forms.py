from django import forms
from .models import Author, Blog

class BlogForm(forms.ModelForm):
    author = forms.ModelChoiceField(
        queryset=Author.objects.all(),
        empty_label="Select Author",
        widget=forms.Select(attrs={'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'})
    )

    class Meta:
        model = Blog
        fields = ['title', 'author', 'content', 'published_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter blog title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 8,
                'placeholder': 'Write your blog content here...'
            }),
            'published_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500'
            }),
        }
