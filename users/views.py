from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import UserRegisterForm,UserUpdateForm,ProfileUpdateForm
from django.contrib.auth.decorators import login_required
import os

def register(request):
    if request.method=="POST":
        form=UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get('username')
            messages.success(request,f"Account Created for {username}")
            return redirect('login')
    else:
        form=UserRegisterForm()
    return render(request,"users/register.html", {'form':form})

@login_required
def profile(request):
    if request.method=="POST":
        u_form=UserUpdateForm(request.POST, instance=request.user)
        p_form=ProfileUpdateForm(request.POST, 
                                 request.FILES, 
                                 instance=request.user.profile)
        old_image = request.user.profile.image
        if u_form.is_valid() and p_form.is_valid():
            if 'image' in request.FILES:
                if old_image and os.path.basename(old_image.name) != "default.jpg":
                    old_image_path = old_image.path
                    if os.path.exists(old_image_path):
                        try:
                            os.remove(old_image_path)
                        except Exception:
                            pass
            u_form.save() 
            p_form.save()
            messages.success(request,f"Your account has been updated")
            return redirect('profile')
    else:
        u_form=UserUpdateForm(instance=request.user)
        p_form=ProfileUpdateForm(instance=request.user.profile)
    
    context={
        'u_form':u_form,
        "p_form":p_form,
    }

    return render(request,'users/profile.html',context)