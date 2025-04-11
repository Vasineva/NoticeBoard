from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView
from .forms import AdvertisementForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
import uuid
from bs4 import BeautifulSoup
from django.urls import reverse_lazy
from .models import Advertisement
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied



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

class AdvertisementListView(ListView):
    model = Advertisement
    ordering = ['-created_at']
    template_name = 'advertisement_list.html'
    context_object_name = 'advertisements'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import CATEGORY_CHOICES
        context['categories'] = CATEGORY_CHOICES
        context['current_category'] = self.request.GET.get('category')
        return context

class AdvertisementDetailView(DetailView):
    model = Advertisement
    template_name = 'advertisement_detail.html'
    context_object_name = 'advertisement'

    def get_queryset(self):
        return Advertisement.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        advertisement = self.get_object()

        # Включаем медиафайлы, относящиеся к этому объявлению
        context['media_files'] = advertisement.media.all()

        # Включаем отклики, которые автор подтвердил
        context['accepted_responses'] = advertisement.responses.filter(is_accepted=True)

        return context

class AdvertisementCreateView(LoginRequiredMixin, CreateView):
    model = Advertisement
    form_class = AdvertisementForm
    template_name = 'advertisement_create.html'
    success_url = reverse_lazy('advertisement_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

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