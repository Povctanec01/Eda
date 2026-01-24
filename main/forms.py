# main/forms.py
from django import forms
from .models import Card, CardBuys, Allergen

class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['title', 'description', 'meal_type', 'allergens']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Название блюда', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'placeholder': 'Описание', 'rows': 4, 'class': 'form-control'}),
            'meal_type': forms.Select(attrs={'class': 'form-control'}),
            'allergens': forms.SelectMultiple(attrs={
                'class': 'form-control select-allergens',
                'size': 5,
                'multiple': 'multiple'
            }),
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
            'title': forms.TextInput(attrs={'placeholder': 'Название блюда', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'placeholder': 'Описание', 'rows': 4, 'class': 'form-control'}),
        }