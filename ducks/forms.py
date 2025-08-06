from django import forms
from .models import Duck, DuckFact


class DuckFactForm(forms.ModelForm):
    class Meta:
        model = DuckFact
        fields = ["fact"]
        widgets = {
            "fact": forms.Textarea(
                attrs={
                    "class": "w-full p-2 border border-gray-300 rounded",
                    "rows": 2,
                    "placeholder": "Write a fun duck fact...",
                }
            ),
        }


class DuckForm(forms.ModelForm):
    class Meta:
        model = Duck
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full p-2 border rounded"}),
            "description": forms.Textarea(
                attrs={"class": "w-full p-2 border rounded", "rows": 3}
            ),
        }
