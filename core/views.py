import base64
import os
import json
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import UploadedFile,UserKeyPair
from .utils import sign_message, decrypt_key,verify_signature
from .forms import MultipleFileUploadForm
from django.contrib.auth.models import User
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

def home(request):
    return render(request, 'core/home.html')

def about(request):
    return render(request, 'core/about.html')

@login_required
def upload_view(request):
    if request.method == 'POST':
        form = MultipleFileUploadForm(request.POST, request.FILES)
        uploaded_files = request.FILES.getlist('uploaded_files')  # Match the input name in the HTML

        if len(uploaded_files) > 5:
            messages.error(request, "You can upload a maximum of 5 files at a time.")
            return redirect('sign-home')

        if uploaded_files and form.is_valid():  # Ensure files are provided and the form is valid
            files_saved_count = 0
            for file in uploaded_files:
                new_file = UploadedFile(
                    owner=request.user,
                    uploaded_file=file
                )
                new_file.save()
                files_saved_count += 1

            if files_saved_count > 0:
                messages.success(request, f"{files_saved_count} file(s) uploaded successfully.")

            return redirect('user_file_list')

        else:
            messages.error(request, "The form was not valid or no files were provided. Please try again.")
            return redirect('sign-home')
    
    return redirect('sign-home')

class UserFileListView(LoginRequiredMixin, ListView):
    model = UploadedFile
    template_name = 'core/user_file_list.html'
    context_object_name = 'files'

    def get_queryset(self):
        # Fetch all files for the logged-in user
        files = UploadedFile.objects.filter(owner=self.request.user)

        # Mark files as "new" if they were uploaded in the last 5 minutes
        from datetime import timedelta
        from django.utils.timezone import now
        recent_threshold = now() - timedelta(minutes=5)
        for file in files:
            file.is_new = file.upload_date >= recent_threshold

        # Sort files: new files first, then by upload date (descending)
        sorted_files = sorted(files, key=lambda f: (f.is_new, f.upload_date), reverse=True)

        return sorted_files

@login_required
def sign_file_view(request):
    if request.method == 'POST':
        try:
            file_id = request.POST.get('file_id')
            file_to_sign = get_object_or_404(UploadedFile, pk=file_id, owner=request.user)

            key_pair = UserKeyPair.objects.get(user=request.user)
            decrypted_private_key = decrypt_key(key_pair.private_key_encrypted)

            file_content = file_to_sign.uploaded_file.read()

            signature_bytes = sign_message(decrypted_private_key, file_content)
            signature_base64 = base64.b64encode(signature_bytes).decode('utf-8')

            file_to_sign.signature = signature_base64
            file_to_sign.save()

            messages.success(request, f"Successfully signed '{file_to_sign}'.")

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

        return redirect('user_file_list')
    return redirect('home')

@login_required
def download_signature_view(request, file_id):
    file_object = get_object_or_404(UploadedFile, pk=file_id, owner=request.user)

    if not file_object.signature:
        messages.error(request, "This file has not been signed yet.")
        return redirect('user_file_list')

    signature_data = {
        'signer_username': file_object.owner.username,
        'signature': file_object.signature
    }

    json_data = json.dumps(signature_data, indent=4)
    original_filename = os.path.splitext(file_object.uploaded_file.name)[0]
    signature_filename = f"{original_filename.replace(' ', '_')}.json"

    response = HttpResponse(json_data, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{signature_filename}"'
    
    return response

def verify_signature_view(request):
    if request.method == 'POST':
        original_file = request.FILES.get('original_file')
        signature_json_file = request.FILES.get('signature_file')

        if not all([original_file, signature_json_file]):
            messages.error(request, "Please provide both the original file and the signature JSON file.")
            return redirect('verify_signature')

        try:
            # 1. Find the user and get their public key
            json_content = signature_json_file.read()
            signature_data = json.loads(json_content)

            signer_username = signature_data['signer_username']
            signature_base64 = signature_data['signature'].encode('utf-8')

            signer = User.objects.get(username=signer_username)
            key_pair = UserKeyPair.objects.get(user=signer)
            public_key_bytes = key_pair.public_key.encode('utf-8')
            
            original_content = original_file.read()
            signature_bytes = base64.b64decode(signature_base64)

            is_valid = verify_signature(public_key_bytes, original_content, signature_bytes)

            if is_valid:
                messages.success(request, f"Signature is VALID. Verified as signed by '{signer_username}'.")
            else:
                messages.error(request, "Signature is INVALID. The file may have been altered or the signature is incorrect. ❌")

        except json.JSONDecodeError:
            messages.error(request, "Invalid signature file. It appears to be a corrupted JSON file.")
        except KeyError:
            messages.error(request, "Invalid signature file. The JSON file is missing 'signer_username' or 'signature'.")
        except User.DoesNotExist:
            messages.error(request, f"Error: The signer '{signer_username}' specified in the signature file was not found.")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
        
        return redirect('verify_signature')

    return render(request, 'core/verify_signature.html')

# Get files 
def encrypt(request,file_id):
    file_object = get_object_or_404(UploadedFile, pk=file_id)
    public_url = file_object.uploaded_file.url
    physical_path = file_object.uploaded_file.path

@login_required
def delete_file_view(request, file_id):
    if request.method == 'POST':
        try:
            file_to_delete = get_object_or_404(UploadedFile, pk=file_id, owner=request.user)
            file_name = str(file_to_delete)
            file_to_delete.uploaded_file.delete()
            file_to_delete.delete()

            messages.success(request, f"File '{file_name}' was deleted successfully.")

        except Exception as e:
            messages.error(request, f"An error occurred while trying to delete the file: {e}")
            
    # Redirect back to the file list regardless of the outcome
    return redirect('user_file_list')