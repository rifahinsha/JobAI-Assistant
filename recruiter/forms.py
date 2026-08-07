from django import forms

from jobs.models import Job


class RecruiterJobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'company', 'location',
            'about_role', 'key_responsibilities', 'required_skills', 'what_we_offer',
            'contact_email', 'url',
        ]
        labels = {
            'about_role': 'About the Role',
            'key_responsibilities': 'Key Responsibilities',
            'required_skills': 'Required Skills',
            'what_we_offer': 'What We Offer',
            'contact_email': 'Contact Email',
            'url': 'External Application Link (optional)',
        }
        help_texts = {
            'contact_email': "Applicants and JobAI will use this address for follow-up questions.",
        }
        widgets = {
            'about_role': forms.Textarea(attrs={'rows': 5, 'placeholder': 'What the team does and what this role is about...'}),
            'key_responsibilities': forms.Textarea(attrs={'rows': 6, 'placeholder': 'One responsibility per line...'}),
            'required_skills': forms.Textarea(attrs={'rows': 5, 'placeholder': 'One required skill per line...'}),
            'what_we_offer': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Salary range, benefits, perks, remote policy...'}),
            'contact_email': forms.EmailInput(attrs={'placeholder': 'hiring@company.com'}),
        }