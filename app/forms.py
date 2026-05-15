from django import forms
from .models import Blog

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'content', 'image', 'published_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-3 border-2 border-purple-200 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all',
                'placeholder': 'Enter blog title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-3 border-2 border-purple-200 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all',
                'rows': 8,
                'placeholder': 'Write your blog content here...'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'block w-full px-4 py-3 border-2 border-purple-200 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100'
            }),
            'published_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'block w-full px-4 py-3 border-2 border-purple-200 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all',
                'id': 'id_published_date'
            }),
        }
