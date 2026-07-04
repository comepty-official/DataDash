from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('files/', views.files_view, name='files'),
    path('files/folder/<uuid:folder_id>/', views.files_view, name='files_folder'),
    path('files/upload/', views.upload_file, name='upload_file'),
    path('files/create-folder/', views.create_folder, name='create_folder'),
    path('files/delete/<uuid:file_id>/', views.delete_file, name='delete_file'),
    path('files/delete-folder/<uuid:folder_id>/', views.delete_folder, name='delete_folder'),
    path('files/rename/<uuid:file_id>/', views.rename_file, name='rename_file'),
    path('files/rename-folder/<uuid:folder_id>/', views.rename_folder, name='rename_folder'),
    path('files/download/<uuid:file_id>/', views.download_file, name='download_file'),
    path('files/favorite/<uuid:file_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('photos/', views.photos_view, name='photos'),
    path('shared/', views.shared_view, name='shared'),
    path('shared-with-me/', views.shared_with_me_view, name='shared_with_me'),
    path('trash/', views.trash_view, name='trash'),
    path('trash/restore/<uuid:file_id>/', views.restore_file, name='restore_file'),
    path('trash/restore-folder/<uuid:folder_id>/', views.restore_folder, name='restore_folder'),
    path('trash/delete/<uuid:file_id>/', views.permanent_delete_file, name='permanent_delete_file'),
    path('trash/empty/', views.empty_trash, name='empty_trash'),
    path('favorites/', views.favorites_view, name='favorites'),
    path('recent/', views.recent_view, name='recent'),
    path('settings/', views.settings_view, name='settings'),
    path('settings/delete-account/', views.delete_account, name='delete_account'),
    path('search/', views.search_view, name='search'),
]
