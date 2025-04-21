from django import forms
from django.core.exceptions import ValidationError
from .models import Advertisement, CATEGORY_CHOICES, Response, Mailing
from tinymce.widgets import TinyMCE

class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['title', 'content', 'category']

    title = forms.CharField(label='Заголовок', max_length=255, min_length=5)
    category = forms.ChoiceField(
        label='Категория',
        choices=[('', '--выберите категорию--')] + CATEGORY_CHOICES,
        required=True
    )
    content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if Advertisement.objects.filter(title=title).exists():
            raise ValidationError('Запись с таким заголовком уже существует.')
        return title

    def clean(self):
        cleaned_data = super().clean()

        # Проверка на количество медиафайлов
        images = cleaned_data.get('content', '').count('<img')
        videos = cleaned_data.get('content', '').count('<video')

        if images > 2:
            raise ValidationError('Вы можете загрузить не более 2 изображений.')
        if videos > 2:
            raise ValidationError('Вы можете загрузить не более 2 видео.')

         # Проверка на уникальность контента
        content = cleaned_data.get('content', '')
        if Advertisement.objects.filter(content=content).exists():
            raise ValidationError('Объявление с таким содержанием уже существует.')

        return cleaned_data

class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Ваш отклик...'}),
        }

class RegistrationForm(forms.Form):
    email = forms.EmailField()
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput())

class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['title', 'message']

