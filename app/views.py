from django.shortcuts import render, redirect, get_object_or_404
from .models import Author, Blog, Subscriber
from django.contrib import messages
from .forms import BlogForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp import login as otp_login
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
import base64

def get_user_name(request):
    user = request.user
    if user.is_authenticated:
        return user.get_full_name() or user.username
    return 'Guest'

def index(request):
    context = { 'name': get_user_name(request) }
    return render(request, 'index.html', context)

def about(request):
    context = { 'name': get_user_name(request) }
    return render(request, 'about.html', context)

def contact(request):
    context = { 'name': get_user_name(request) }
    return render(request, 'contact.html', context)

def bloglist(request):
    blogs = Blog.objects.all()
    context = { 'blogs': blogs }
    return render(request, 'blog_list.html', context)

def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    context = { 'blog': blog }
    return render(request, 'blog_detail.html', context)

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
    author, _ = Author.objects.get_or_create(
        user=request.user,
        defaults={
            'first_name': request.user.first_name or request.user.username,
            'last_name': '',
            'email': request.user.email,
        }
    )
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = author
            tz_offset = request.POST.get('tz_offset')
            if blog.published_date and tz_offset:
                offset_minutes = int(tz_offset)
                blog.published_date = blog.published_date + timedelta(minutes=-offset_minutes)
            blog.save()
            return redirect('blog_list')
    else:
        now = timezone.localtime(timezone.now())
        initial = {'published_date': now.strftime('%Y-%m-%dT%H:%M')}
        form = BlogForm(initial=initial)
    return render(request, 'add_blog.html', { 'form': form })


@receiver(post_save, sender=User)
def create_author_for_new_user(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'author'):
        Author.objects.get_or_create(
            user=instance,
            defaults={
                'first_name': instance.first_name or instance.username,
                'last_name': '',
                'email': instance.email,
            }
        )

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
