from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, FileResponse, Http404
from django.db.models import Q, Sum
from django.utils import timezone
from django.views.decorators.http import require_POST, require_http_methods
from django.conf import settings
import json

from .models import UserFile, Folder, SharedFile, UserStorageUsage
from .forms import FileUploadForm, FolderForm, RenameForm, ShareFileForm
from .utils import get_mime_type, update_storage_usage, check_storage_limit


@login_required
def dashboard(request):
    user = request.user
    recent_files = UserFile.objects.filter(owner=user, is_deleted=False).order_by('-created_at')[:8]
    trash_count = UserFile.objects.filter(owner=user, is_deleted=True).count()
    shared_count = SharedFile.objects.filter(shared_by=user).count()
    usage, _ = UserStorageUsage.objects.get_or_create(
        user=user, defaults={'max_bytes': settings.MAX_STORAGE_BYTES}
    )
    image_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml']
    photo_count = UserFile.objects.filter(owner=user, is_deleted=False, mime_type__in=image_types).count()
    context = {
        'recent_files': recent_files,
        'file_count': user.get_file_count(),
        'photo_count': photo_count,
        'shared_count': shared_count,
        'trash_count': trash_count,
        'storage_usage': usage,
        'page': 'dashboard',
    }
    return render(request, 'storage/dashboard.html', context)


@login_required
def files_view(request, folder_id=None):
    user = request.user
    current_folder = None
    breadcrumbs = []

    if folder_id:
        current_folder = get_object_or_404(Folder, id=folder_id, owner=user, is_deleted=False)
        f = current_folder
        while f:
            breadcrumbs.insert(0, f)
            f = f.parent

    folders = Folder.objects.filter(owner=user, parent=current_folder, is_deleted=False)
    files = UserFile.objects.filter(owner=user, folder=current_folder, is_deleted=False)

    query = request.GET.get('q', '')
    if query:
        files = UserFile.objects.filter(owner=user, is_deleted=False, name__icontains=query)
        folders = Folder.objects.filter(owner=user, is_deleted=False, name__icontains=query)

    sort = request.GET.get('sort', '-created_at')
    valid_sorts = ['name', '-name', 'created_at', '-created_at', 'size', '-size']
    if sort in valid_sorts:
        files = files.order_by(sort)

    folder_form = FolderForm()
    upload_form = FileUploadForm()
    context = {
        'folders': folders,
        'files': files,
        'current_folder': current_folder,
        'breadcrumbs': breadcrumbs,
        'folder_form': folder_form,
        'upload_form': upload_form,
        'query': query,
        'sort': sort,
        'page': 'files',
    }
    return render(request, 'storage/files.html', context)


@login_required
def upload_file(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    folder_id = request.POST.get('folder_id')
    folder = None
    if folder_id:
        folder = get_object_or_404(Folder, id=folder_id, owner=request.user)

    uploaded = []
    errors = []
    for f in request.FILES.getlist('file'):
        if not check_storage_limit(request.user, f.size):
            errors.append(f"{f.name}: Storage limit exceeded")
            continue
        user_file = UserFile.objects.create(
            owner=request.user,
            folder=folder,
            name=f.name,
            original_name=f.name,
            file=f,
            size=f.size,
            mime_type=get_mime_type(f),
        )
        uploaded.append({'id': str(user_file.id), 'name': user_file.name})

    update_storage_usage(request.user)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'uploaded': uploaded, 'errors': errors})
    if errors:
        messages.error(request, '; '.join(errors))
    else:
        messages.success(request, f'{len(uploaded)} file(s) uploaded successfully.')
    return redirect(request.POST.get('next', 'files'))


@login_required
def create_folder(request):
    if request.method != 'POST':
        return redirect('files')
    form = FolderForm(request.POST)
    parent_id = request.POST.get('parent_id')
    parent = None
    if parent_id:
        parent = get_object_or_404(Folder, id=parent_id, owner=request.user)
    if form.is_valid():
        folder = form.save(commit=False)
        folder.owner = request.user
        folder.parent = parent
        folder.save()
        messages.success(request, f'Folder "{folder.name}" created.')
    else:
        messages.error(request, 'Invalid folder name.')
    return redirect(request.POST.get('next', 'files'))


@login_required
def delete_file(request, file_id):
    f = get_object_or_404(UserFile, id=file_id, owner=request.user)
    f.soft_delete()
    update_storage_usage(request.user)
    messages.success(request, f'"{f.name}" moved to Trash.')
    return redirect(request.META.get('HTTP_REFERER', 'files'))


@login_required
def delete_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    folder.soft_delete()
    update_storage_usage(request.user)
    messages.success(request, f'"{folder.name}" moved to Trash.')
    return redirect(request.META.get('HTTP_REFERER', 'files'))


@login_required
def rename_file(request, file_id):
    f = get_object_or_404(UserFile, id=file_id, owner=request.user)
    if request.method == 'POST':
        form = RenameForm(request.POST)
        if form.is_valid():
            f.name = form.cleaned_data['name']
            f.save()
            messages.success(request, 'File renamed successfully.')
    return redirect(request.META.get('HTTP_REFERER', 'files'))


@login_required
def rename_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    if request.method == 'POST':
        form = RenameForm(request.POST)
        if form.is_valid():
            folder.name = form.cleaned_data['name']
            folder.save()
            messages.success(request, 'Folder renamed successfully.')
    return redirect(request.META.get('HTTP_REFERER', 'files'))


@login_required
def download_file(request, file_id):
    f = get_object_or_404(UserFile, id=file_id, owner=request.user, is_deleted=False)
    response = FileResponse(f.file.open('rb'), as_attachment=True, filename=f.original_name)
    return response


@login_required
def toggle_favorite(request, file_id):
    f = get_object_or_404(UserFile, id=file_id, owner=request.user)
    f.is_favorite = not f.is_favorite
    f.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'favorited': f.is_favorite})
    return redirect(request.META.get('HTTP_REFERER', 'files'))


@login_required
def photos_view(request):
    image_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml']
    query = request.GET.get('q', '')
    photos = UserFile.objects.filter(owner=request.user, is_deleted=False, mime_type__in=image_types)
    if query:
        photos = photos.filter(name__icontains=query)
    sort = request.GET.get('sort', '-created_at')
    valid_sorts = ['name', '-name', '-created_at', 'created_at', '-size', 'size']
    if sort in valid_sorts:
        photos = photos.order_by(sort)
    return render(request, 'storage/photos.html', {'photos': photos, 'query': query, 'page': 'photos'})


@login_required
def shared_view(request):
    shared = SharedFile.objects.filter(shared_by=request.user).select_related('file', 'folder', 'shared_with')
    return render(request, 'storage/shared.html', {'shared_items': shared, 'page': 'shared'})


@login_required
def shared_with_me_view(request):
    received = SharedFile.objects.filter(
        Q(shared_with=request.user) | Q(shared_with_email=request.user.email)
    ).select_related('file', 'folder', 'shared_by')
    return render(request, 'storage/shared_with_me.html', {'received_items': received, 'page': 'shared_with_me'})


@login_required
def trash_view(request):
    deleted_files = UserFile.objects.filter(owner=request.user, is_deleted=True).order_by('-deleted_at')
    deleted_folders = Folder.objects.filter(owner=request.user, is_deleted=True).order_by('-deleted_at')
    return render(request, 'storage/trash.html', {
        'deleted_files': deleted_files, 'deleted_folders': deleted_folders, 'page': 'trash'
    })


@login_required
def restore_file(request, file_id):
    f = get_object_or_404(UserFile, id=file_id, owner=request.user)
    f.restore()
    update_storage_usage(request.user)
    messages.success(request, f'"{f.name}" restored.')
    return redirect('trash')


@login_required
def restore_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    folder.restore()
    messages.success(request, f'"{folder.name}" restored.')
    return redirect('trash')


@login_required
def permanent_delete_file(request, file_id):
    f = get_object_or_404(UserFile, id=file_id, owner=request.user)
    f.file.delete(save=False)
    f.delete()
    update_storage_usage(request.user)
    messages.success(request, 'File permanently deleted.')
    return redirect('trash')


@login_required
def empty_trash(request):
    files = UserFile.objects.filter(owner=request.user, is_deleted=True)
    for f in files:
        f.file.delete(save=False)
    files.delete()
    Folder.objects.filter(owner=request.user, is_deleted=True).delete()
    update_storage_usage(request.user)
    messages.success(request, 'Trash emptied.')
    return redirect('trash')


@login_required
def favorites_view(request):
    favorites = UserFile.objects.filter(owner=request.user, is_deleted=False, is_favorite=True)
    return render(request, 'storage/favorites.html', {'favorites': favorites, 'page': 'favorites'})


@login_required
def recent_view(request):
    recent = UserFile.objects.filter(owner=request.user, is_deleted=False).order_by('-created_at')[:50]
    return render(request, 'storage/recent.html', {'recent_files': recent, 'page': 'recent'})


@login_required
def settings_view(request):
    from accounts.forms import AccountSettingsForm
    from accounts.models import LoginHistory
    user = request.user
    if request.method == 'POST':
        form = AccountSettingsForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings saved successfully.')
            return redirect('settings')
    else:
        form = AccountSettingsForm(instance=user)
    login_history = LoginHistory.objects.filter(user=user)[:10]
    usage, _ = UserStorageUsage.objects.get_or_create(user=user, defaults={'max_bytes': settings.MAX_STORAGE_BYTES})
    return render(request, 'storage/settings.html', {
        'form': form, 'login_history': login_history, 'usage': usage, 'page': 'settings'
    })


@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        from django.contrib.auth import logout
        logout(request)
        user.delete()
        messages.info(request, 'Your account has been deleted.')
        return redirect('login')
    return redirect('settings')


@login_required
def search_view(request):
    query = request.GET.get('q', '').strip()
    results_files = []
    results_folders = []
    if query:
        results_files = UserFile.objects.filter(owner=request.user, is_deleted=False, name__icontains=query)
        results_folders = Folder.objects.filter(owner=request.user, is_deleted=False, name__icontains=query)
    return render(request, 'storage/search.html', {
        'query': query, 'results_files': results_files, 'results_folders': results_folders, 'page': 'search'
    })
