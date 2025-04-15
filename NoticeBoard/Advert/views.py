from django.views.generic import (CreateView, ListView, DetailView,
                                  DeleteView, UpdateView, TemplateView)
from .models import Advertisement, Response, User
from .forms import AdvertisementForm, ResponseForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
import uuid
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
import secrets
from django.core.mail import send_mail
from django.contrib.auth import login
from django.utils import timezone
from datetime import timedelta








@csrf_exempt
# функция загружает медиафайлы на сервер
def upload_media(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']

        # Определяем расширение файла и его тип
        file_extension = uploaded_file.name.split('.')[-1].lower()

        # Проверяем тип файла (изображение или видео)
        if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
            media_type = 'image'
        elif file_extension in ['mp4', 'mov', 'avi', 'mkv']:
            media_type = 'video'
        else:
            return JsonResponse({'error': 'Unsupported file type'}, status=400)

        # Генерируем уникальное имя файла
        filename = f"{uuid.uuid4()}-{uploaded_file.name}"
        relative_path = os.path.join('uploads', media_type, filename)  # Сохраняем в подпапки для типа

        # Сохраняем файл в /media/uploads/
        default_storage.save(relative_path, ContentFile(uploaded_file.read()))

        # Возвращаем абсолютный URL (MEDIA_URL + путь)
        file_url = settings.MEDIA_URL + relative_path.replace("\\", "/")

        return JsonResponse({'location': file_url, 'media_type': media_type})

    return JsonResponse({'error': 'No file uploaded'}, status=400)


#список объявлений
class AdvertisementListView(ListView):
    model = Advertisement
    ordering = ['-created_at']
    template_name = 'advertisement_list.html'
    context_object_name = 'advertisements'
    paginate_by = 20

    #фильтрация по категории
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset

    # текущая выбранная категория для отображения в шаблоне
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import CATEGORY_CHOICES
        context['categories'] = CATEGORY_CHOICES
        context['current_category'] = self.request.GET.get('category')
        return context

# подробную информацию о конкретном объявлении.
class AdvertisementDetailView(DetailView):
    model = Advertisement
    template_name = 'advertisement_detail.html'
    context_object_name = 'advertisement'

    # Все медиафайлы Отклики
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        advertisement = self.get_object()

        # Медиафайлы
        context['media_files'] = advertisement.media.all()

        # Только подтвержденные отклики
        context['accepted_responses'] = advertisement.responses.filter(is_accepted=True)

        return context

#создания нового объявления
class AdvertisementCreateView(LoginRequiredMixin, CreateView):
    model = Advertisement
    form_class = AdvertisementForm
    template_name = 'advertisement_create.html'
    success_url = reverse_lazy('advertisement_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

#редактирования объявления
class AdvertisementUpdateView(LoginRequiredMixin, UpdateView):
    model = Advertisement
    form_class = AdvertisementForm
    template_name = 'advertisement_create.html'  # Используем тот же шаблон, что и для создания
    context_object_name = 'advertisement'
    success_url = reverse_lazy('advertisement_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Проверяем, является ли текущий пользователь автором объявления
        if obj.author != self.request.user:
            raise PermissionDenied("Вы не автор этого объявления.")
        return obj

class AdvertisementDeleteView(LoginRequiredMixin, DeleteView):
    model = Advertisement
    template_name = 'advertisement_delete.html'
    context_object_name = 'advertisement'
    success_url = reverse_lazy('advertisement_list')

    def get_object(self, queryset=None):
        # Получаем объект объявления
        obj = super().get_object(queryset)
        # Проверяем, является ли текущий пользователь автором объявления
        if obj.author != self.request.user:
            raise PermissionDenied("Вы не автор этого объявления.")
        return obj

@require_POST
@login_required
#обрабатывает отправку откликов на объявления
def respond_to_ad(request, pk):
    advertisement = get_object_or_404(Advertisement, pk=pk)
    form = ResponseForm(request.POST)
    if form.is_valid():
        response = form.save(commit=False)
        response.advertisement = advertisement
        response.author = request.user
        response.save()

        return JsonResponse({
            'content': response.content,
            'author': response.author.username,
            'created_at': response.created_at.strftime('%d %b %Y'),
        })
    return JsonResponse({'error': 'Ошибка при отправке отклика'}, status=400)

@method_decorator(login_required, name='dispatch')
#отображает отклики текущего пользователя на его объявления.
class MyResponsesView(TemplateView):
    template_name = 'my_responses.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        advertisements = Advertisement.objects.filter(author=self.request.user)

        selected_ad_id = self.request.GET.get('ad_id')
        try:
            selected_ad_id = int(selected_ad_id)
        except (TypeError, ValueError):
            selected_ad_id = None

        if selected_ad_id:
            responses = Response.objects.filter(advertisement_id=selected_ad_id, advertisement__author=self.request.user)
        else:
            responses = Response.objects.filter(advertisement__author=self.request.user)

        context.update({
            'advertisements': advertisements,
            'responses': responses,
            'selected_ad_id': selected_ad_id,
        })
        return context

@login_required
# Устанавливает отклик как подтвержденный
def accept_response(request, pk):
    response = get_object_or_404(Response, pk=pk, advertisement__author=request.user)
    response.is_accepted = True
    response.save()
    return redirect('my_responses')

@login_required
#Удаляет отклик
def delete_response(request, pk):
    response = get_object_or_404(Response, pk=pk, advertisement__author=request.user)
    response.delete()
    return redirect('my_responses')

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

def generate_code():
    return secrets.token_urlsafe(4)

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not email or not username or not password:
            return render(request, 'authorization.html', {'error': 'Все поля обязательны'})

        if User.objects.filter(email=email).exists():
            return render(request, 'authorization.html', {'error': 'E-mail уже зарегистрирован'})

        # Сохраняем временные данные в сессии
        request.session['registration_data'] = {
            'email': email,
            'username': username,
            'password': password,
        }

        code = generate_code()
        request.session['verification_code'] = code
        request.session['code_created_at'] = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

        send_mail(
            'Подтверждение регистрации',
            f'Ваш код: {code}',
            'vasinevakatirina@yandex.ru',
            [email],
            fail_silently=False,
        )

        return render(request, 'code.html')

    return render(request, 'authorization.html')

def confirm_code_view(request):
    if request.method == 'POST':
        code_input = request.POST.get('code')
        code_session = request.session.get('verification_code')
        code_time_str = request.session.get('code_created_at')
        registration_data = request.session.get('registration_data')

        if not registration_data or not code_session or not code_time_str:
            return render(request, 'code.html', {'error': 'Регистрация не найдена или код не создан'})

        code_time = timezone.datetime.strptime(code_time_str, '%Y-%m-%d %H:%M:%S')
        if timezone.now() - code_time > timedelta(minutes=5):
            return render(request, 'code.html', {'error': 'Код устарел'})

        if code_input != code_session:
            return render(request, 'code.html', {'error': 'Неверный код'})

        # Всё ок — создаем пользователя
        user = User.objects.create_user(
            username=registration_data['username'],
            email=registration_data['email'],
            password=registration_data['password']
        )
        login(request, user)

        # Очищаем сессию
        for key in ['registration_data', 'verification_code', 'code_created_at']:
            request.session.pop(key, None)

        return redirect('my_profile')

    return render(request, 'code.html')

