from django.shortcuts import render, redirect
from .models import Blog, Subscriber
from django.contrib import messages
from .forms import BlogForm
from django.contrib.auth.decorators import login_required
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp import login as otp_login
import qrcode
from io import BytesIO
import base64

def index(request):
    context = { 'name': 'John Doe' }
    return render(request, 'index.html', context)

def about(request):
    context = { 'name': 'John Doe' }
    return render(request, 'about.html', context)

def contact(request):
    context = { 'name': 'John Doe' }
    return render(request, 'contact.html', context)

def bloglist(request):
    blogs = Blog.objects.all()
    context = { 'blogs': blogs }
    return render(request, 'blog_list.html', context)

def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, 'Email address is required.')
        elif Subscriber.objects.filter(email=email).exists():
            messages.error(request, 'This email is already subscribed.')
        else:
            subscriber = Subscriber(email=email)
            subscriber.save()
            messages.success(request, 'You have been subscribed successfully.')
        return redirect('subscribe')
    return render(request, 'subscribe.html')

@login_required
def add_blog(request):
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save()
            return redirect('blog_list')
    else:
        form = BlogForm()
    return render(request, 'add_blog.html', { 'form': form })

@login_required
def profile(request):
    totp_devices = TOTPDevice.objects.filter(user=request.user, confirmed=True)
    qr_code_data = None
    if not totp_devices.exists():
        device, created = TOTPDevice.objects.get_or_create(
            user=request.user,
            name='default',
            defaults={'confirmed': False}
        )
        if not device.confirmed:
            config_url = device.config_url
            qr = qrcode.make(config_url)
            buf = BytesIO()
            qr.save(buf, format='PNG')
            qr_code_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    context = {
        'totp_devices': totp_devices,
        'qr_code_data': qr_code_data,
    }
    return render(request, 'profile.html', context)

@login_required
def enable_2fa(request):
    device, created = TOTPDevice.objects.get_or_create(
        user=request.user,
        name='default',
        defaults={'confirmed': False}
    )
    if request.method == 'POST':
        token = request.POST.get('token')
        if device.verify_token(token):
            device.confirmed = True
            device.save()
            messages.success(request, 'Two-factor authentication enabled.')
            return redirect('profile')
        else:
            messages.error(request, 'Invalid token. Please try again.')
    config_url = device.config_url
    qr = qrcode.make(config_url)
    buf = BytesIO()
    qr.save(buf, format='PNG')
    qr_code_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    return render(request, 'enable_2fa.html', {'qr_code_data': qr_code_data, 'device': device})


@login_required
def verify_2fa(request):
    if request.method == 'POST':
        token = request.POST.get('token', '')
        devices = TOTPDevice.objects.filter(user=request.user, confirmed=True)
        if not devices.exists():
            messages.error(request, 'No 2FA devices configured.')
            return redirect('profile')
        for device in devices:
            if device.verify_token(token):
                otp_login(request, device)
                messages.success(request, 'Two-factor authentication verified.')
                return redirect('index')
        messages.error(request, 'Invalid verification code. Please try again.')
    return render(request, 'verify_2fa.html')
