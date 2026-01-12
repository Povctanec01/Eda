from django import forms
from .models import Card



class StaffRegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Имя пользователя",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="Подтвердите пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        choices=[('chef', 'Повар'), ('admin', 'Администратор')],
        label="Роль",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            raise forms.ValidationError("Пароли не совпадают")
        return cleaned_data

    def save(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password1']
        role = self.cleaned_data['role']
        user = User.objects.create_user(username=username, password=password)
        user.profile.role = role
        user.profile.save()
        return user

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
