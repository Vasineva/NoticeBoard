from django.views.generic import CreateView, ListView, DetailView
from django.urls import reverse_lazy
from .models import Advertisement
from .forms import AdvertisementForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
import uuid

@csrf_exempt
def upload_media(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']

        # Генерируем уникальное имя файла
        filename = f"{uuid.uuid4()}-{uploaded_file.name}"
        relative_path = os.path.join('uploads', filename)

        # Сохраняем файл в /media/uploads/
        default_storage.save(relative_path, ContentFile(uploaded_file.read()))

        # Возвращаем абсолютный URL (MEDIA_URL + путь)
        file_url = settings.MEDIA_URL + relative_path.replace("\\", "/")

        return JsonResponse({'location': file_url})

    return JsonResponse({'error': 'Нет файла для загрузки'}, status=400)

class AdvertisementListView(ListView):
    model = Advertisement
    ordering = ['-created_at']
    template_name = 'advertisement_list.html'
    context_object_name = 'advertisements'
    paginate_by = 2

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