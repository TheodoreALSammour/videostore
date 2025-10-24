from django import forms
from .models import Video

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = [
            "MovieID",
            "MovieTitle",
            "Actor1Name",
            "Actor2Name",
            "DirectorName",
            "MovieGenre",
            "ReleaseYear",
        ]
        widgets = {
            "MovieTitle": forms.TextInput(attrs={"placeholder": "e.g., Inception"}),
            "Actor1Name": forms.TextInput(attrs={"placeholder": "Lead actor"}),
            "Actor2Name": forms.TextInput(attrs={"placeholder": "Supporting actor"}),
            "DirectorName": forms.TextInput(attrs={"placeholder": "Director"}),
            "ReleaseYear": forms.NumberInput(attrs={"min": 1888, "max": 2100}),
        }
