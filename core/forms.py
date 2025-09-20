from django import forms


class MultipleFileInput(forms.FileInput):
    """
    A widget that allows multiple file selection.
    """
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """
    A field that can handle multiple uploaded files.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        else:
            return single_file_clean(data, initial)


class MultipleFileUploadForm(forms.Form):
    # Use the custom field that handles multiple files.
    uploaded_files = MultipleFileField(required=True)