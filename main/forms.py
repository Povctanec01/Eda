# main/forms.py
from django import forms
from .models import Card, CardBuys, Allergen, ProductRemaining


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['title', 'description', 'meal_type', 'price', 'allergens']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Название блюда', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'placeholder': 'Описание', 'rows': 4, 'class': 'form-control'}),
            'meal_type': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={  # Добавить этот виджет
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0'
            }),
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
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price < 0:
            raise forms.ValidationError("Цена не может быть отрицательной")
        return price

class CardFormBuys(forms.ModelForm):
    class Meta:
        model = CardBuys
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Название блюда', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'placeholder': 'Описание', 'rows': 4, 'class': 'form-control'}),
        }

class ProductRemainingForm(forms.ModelForm):
    class Meta:
        model = ProductRemaining
        fields = ['name', 'quantity', 'unit', 'min_quantity']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Картофель'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'unit': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                ('кг', 'Килограммы'),
                ('г', 'Граммы'),
                ('л', 'Литр'),
                ('шт', 'Штуки'),
                ('уп', 'Упаковка'),
            ]),
            'min_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
        }
        labels = {
            'name': 'Название продукта',
            'quantity': 'Текущее количество',
            'unit': 'Единица измерения',
            'min_quantity': 'Минимальный запас',
        }