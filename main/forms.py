from django import forms
from .models import Card, CardBuys

# cards_app/forms.py
from django import forms
from .models import Card

class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['title', 'description', 'meal_type']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Название блюда'}),
            'description': forms.Textarea(attrs={'placeholder': 'Описание', 'rows': 4}),
            'meal_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_meal_type(self):
        meal_type = self.cleaned_data.get('meal_type')
        if meal_type == 'select':
            raise forms.ValidationError("Пожалуйста, выберите тип приёма пищи.")
        return meal_type


class CardFormBuys(forms.ModelForm):
    class Meta:
        model = CardBuys
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Название блюда'}),
            'description': forms.Textarea(attrs={'placeholder': 'Описание', 'rows': 4}),
        }

    def clean_meal_type(self):
        meal_type = self.cleaned_data.get('meal_type')
        if meal_type == 'select':
            raise forms.ValidationError("Пожалуйста, выберите тип приёма пищи.")
        return meal_type