from django import forms
from .models import UserFile, Folder, SharedFile

# --- Helper Classes for Multiple File Uploads ---

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


# --- Forms ---

class FileUploadForm(forms.ModelForm):
    # Overriding the file field to support HTML5 'multiple' select
    file = MultipleFileField(
        widget=MultipleFileInput(attrs={'class': 'form-control', 'multiple': True}),
        required=True
    )

    class Meta:
        model = UserFile
        fields = ('file',)


class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ('name', 'color')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Folder name'}),
            'color': forms.Select(
                choices=[
                    ('#6366f1', 'Indigo'),
                    ('#8b5cf6', 'Violet'),
                    ('#ec4899', 'Pink'),
                    ('#f43f5e', 'Rose'),
                    ('#f97316', 'Orange'),
                    ('#eab308', 'Yellow'),
                    ('#22c55e', 'Green'),
                    ('#06b6d4', 'Cyan'),
                    ('#3b82f6', 'Blue'),
                ],
                attrs={'class': 'form-select'}
            ),
        }


class RenameForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'New name'})
    )


class ShareFileForm(forms.ModelForm):
    class Meta:
        model = SharedFile
        fields = ('shared_with_email', 'permission', 'is_public', 'expires_at')
        widgets = {
            'shared_with_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'permission': forms.Select(attrs={'class': 'form-select'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'expires_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }