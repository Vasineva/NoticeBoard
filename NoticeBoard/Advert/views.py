from django.views.generic import (CreateView, ListView, DetailView,
                                  DeleteView, UpdateView, TemplateView)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from .models import Advertisement, Response, User
from .forms import AdvertisementForm, ResponseForm
import os
import uuid
import random
import string
from django.core.mail import send_mail


# функция загружает медиафайлы на сервер
@csrf_exempt
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
    template_name = 'Advertisement/advertisement_list.html'
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
    template_name = 'Advertisement/advertisement_detail.html'
    context_object_name = 'advertisement'

    # Все медиафайлы Отклики
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        advertisement = self.get_object()

        # Медиафайлы
        context['media_files'] = advertisement.media.all()

        # Только подтвержденные отклики
        context['accepted_responses'] = advertisement.responses.filter(is_accepted=True)

        context['response_form'] = ResponseForm()

        return context

#создания нового объявления
class AdvertisementCreateView(LoginRequiredMixin, CreateView):
    model = Advertisement
    form_class = AdvertisementForm
    template_name = 'Advertisement/advertisement_create.html'
    success_url = reverse_lazy('advertisement_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

#редактирования объявления
class AdvertisementUpdateView(LoginRequiredMixin, UpdateView):
    model = Advertisement
    form_class = AdvertisementForm
    template_name = 'Advertisement/advertisement_create.html'  # Используем тот же шаблон, что и для создания
    context_object_name = 'advertisement'
    success_url = reverse_lazy('advertisement_list')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Проверяем, является ли текущий пользователь автором объявления
        if obj.author != self.request.user:
            raise PermissionDenied("Вы не автор этого объявления.")
        return obj

# Удалить обявления
class AdvertisementDeleteView(LoginRequiredMixin, DeleteView):
    model = Advertisement
    template_name = 'Advertisement/advertisement_delete.html'
    context_object_name = 'advertisement'
    success_url = reverse_lazy('advertisement_list')

    def get_object(self, queryset=None):
        # Получаем объект объявления
        obj = super().get_object(queryset)
        # Проверяем, является ли текущий пользователь автором объявления
        if obj.author != self.request.user:
            raise PermissionDenied("Вы не автор этого объявления.")
        return obj

#обрабатывает отправку откликов на объявления
@require_POST
@login_required
def respond_to_ad(request, pk):
    advertisement = get_object_or_404(Advertisement, pk=pk)
    form = ResponseForm(request.POST)

    if form.is_valid():
        response = form.save(commit=False)
        response.advertisement = advertisement
        response.author = request.user
        response.save()

        # Перенаправляем на страницу с сообщением об успешном отклике
        return render(request, 'response_confirmation.html', {
            'advertisement': advertisement
        })

    return JsonResponse({'error': 'Ошибка при отправке отклика'}, status=400)

#отображает отклики текущего пользователя на его объявления.
@method_decorator(login_required, name='dispatch')
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
            responses = Response.objects.filter(
                advertisement_id=selected_ad_id,
                advertisement__author=self.request.user
            ).order_by('is_accepted', '-created_at')
        else:
            responses = Response.objects.filter(
                advertisement__author=self.request.user
            ).order_by('is_accepted', '-created_at')

        context.update({
            'advertisements': advertisements,
            'responses': responses,
            'selected_ad_id': selected_ad_id,
        })
        return context

# Устанавливает отклик как подтвержденный
@login_required
def accept_response(request, pk):
    response = get_object_or_404(Response, pk=pk, advertisement__author=request.user)
    response.is_accepted = True
    response.save()
    return redirect('my_responses')

#Удаляет отклик
@login_required
def delete_response(request, pk):
    response = get_object_or_404(Response, pk=pk, advertisement__author=request.user)
    response.delete()
    return redirect('my_responses')

#Страница пользователя
class IndexView(LoginRequiredMixin, ListView):
    model = Advertisement
    template_name = 'index.html'
    context_object_name = 'advertisements'
    paginate_by = 20
    ordering = ['-created_at']

    def get_queryset(self):
        # Фильтрация объявлений по автору (только для текущего пользователя)
        return Advertisement.objects.filter(author=self.request.user).order_by('-created_at')

# Генерация одноразового кода
def generate_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

# форма регистрации
def usual_login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']

        request.session['email'] = email
        request.session['username'] = username
        request.session['password'] = password

        code = generate_code()
        request.session['reg_code'] = code

        send_mail(
            'Код подтверждения регистрации',
            f'Ваш код: {code}',
            'vasinevakatirina@yandex.ru',
            [email],
        )

        return redirect('confirm_code')
    return render(request, 'signup.html')

# подтверждение кода
def login_with_code_view(request):
    if request.method == 'POST':
        entered_code = request.POST['code']
        real_code = request.session.get('reg_code')

        if entered_code == real_code:
            username = request.session.get('username')
            email = request.session.get('email')
            password = request.session.get('password')

            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)

            # очистка
            request.session.pop('reg_code', None)
            request.session.pop('username', None)
            request.session.pop('email', None)
            request.session.pop('password', None)

            return redirect('my_profile')
        else:
            return render(request, 'code.html', {'error': 'Неверный код'})
    return render(request, 'code.html')