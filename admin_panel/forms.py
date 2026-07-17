from django import forms
from jobs.models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title','company','location','description','url']
        widgets = {'description':forms.Textarea(attrs={'rows':5})}