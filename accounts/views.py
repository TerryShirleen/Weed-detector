from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from .forms import *
from django.contrib.auth.models import User
from datetime import datetime
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from accounts.admin import *
from .models import *
from django.contrib import messages
from django.core.mail import EmailMessage
from django_otp.plugins.otp_totp.models import TOTPDevice
import random, time




# create views below
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')

            # Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists. Please choose a different username.')
                return redirect('register')

            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email address already exists. Please use a different email address.')
                return redirect('register')

            # If username and email are unique, proceed with registration
            user = form.save(commit=False)
            profile_status = ProfileStatus.objects.get(name="REGISTRATION PENDING")
            profile = Profile(user=user, status=profile_status, date_created=datetime.now(), date_modified=datetime.now())
            user.save()
            profile.save()

            # SEND THE REGISTRATION EMAIL TO THE USER
            subject = "Weed Detector Registration Alert"

            message = f"""
            <html>
            <body>
                <p>Dear {username},</p>

                <p>Thank you for registering with Weed Detector! We're thrilled to have you on board.</p>

                <p>Your account is currently pending approval. Please wait for our team to review your information. Once approved, you'll receive an email notification, and you can then start using the Weed Detector application.</p>

                <p>If you have any questions or concerns, feel free to reach out to our support team at <a href="mailto:support@weeddetector.co.ke">support@weeddetector.co.ke</a>.</p>

                <p>Regards,<br>The Weed Detector Team</p>
            </body>
            </html>
            """
            email = EmailMessage(subject, message, to=[email])
            email.content_subtype = "html" 
            email.send()

            messages.success(request, 'Registered Successfully. Please check your E-mail')
            return redirect('login')

    else:
        form = RegisterForm()

    context = {
        'form': form,
    }

    return render(request, 'registration/register.html', context)

def generate_and_send_otp(request, user):
    otp_value = str(random.randint(100000, 999999))
    # Save OTP to the user's profile
    profile = user.profile
    totp_device, created = TOTPDevice.objects.get_or_create(user=user)
    totp_device.key = otp_value
    totp_device.save()

    profile = Profile.objects.get(user=user)
    profile.otp_device = totp_device
    profile.save()

    # Send OTP via email
    subject = "One-Time Password (OTP) for Weed Detector"
    message = f"Dear {user.first_name},\n\nYour One-Time Password (OTP) for Weed Detector is: {otp_value}\n\nPlease use this OTP to complete your login.\n\nRegards,\nThe Weed Detector Team"
    user.email_user(subject, message)

    messages.success(request, 'OTP sent to your email. Please check and enter the OTP.')

    return {
        'username': user.username,
        'device_id': totp_device.id,
        'secret':totp_device.key
    }

def otp_verification(request):
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            username = request.session.get('username')
            device_id = request.session.get('device_id')
            otp = form.cleaned_data['otp']
            user = User.objects.get(username=username)
            totp_device = TOTPDevice.objects.get(user=user)
            stored_device_id = totp_device.id
            try:
                totp_device = TOTPDevice.objects.get(id=device_id, user=user)
                if totp_device.key==otp and stored_device_id ==device_id:
                    login(request, user)
                    messages.success(request, 'OTP verification successful!')
                    time.sleep(5)
                    return redirect('index')
                else:
                    messages.error(request, 'Invalid OTP. Please try again.')
            except TOTPDevice.DoesNotExist:
                messages.error(request, 'Invalid device or user.')
        else:
            messages.error(request, 'Invalid form submission. Please try again.')
    else:
        form = OTPVerificationForm()

    return render(request, 'registration/otp_verification.html', {'form': form})

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f'Logged in as {username}')
            return redirect('index')

        elif user is not None:
            try:
                profile = user.profile
            except Profile.DoesNotExist:
                profile = None

            if profile and profile.status not in ['DEACTIVAED', 'LOCKED', 'REGISTRATION PENDING']:
                # Generate and send OTP
                otp_device = generate_and_send_otp(request, user)
                request.session['username'] = otp_device['username']
                request.session['device_id'] = otp_device['device_id']

                if otp_device:
                    return redirect('otp_verification')
                else:
                    messages.error(request, 'Failed to generate and send OTP. Please try again.')
            else:
                messages.error(request, f'Please check if you have been approved...')
    context = {}
    return render(request, 'registration/login.html', context)


def index (request):
    try:
        users = User.objects.all()
        form = ImageUploadForm(request.POST)
    except:
       users =[]
       form = []
    context = {
        'users':users,
        'form':form
    }
    return render(request, 'accounts/index.html', context)

@login_required(login_url='login')
def verified_users(request):
    try:
        verified_users = Profile.objects.filter(status=ProfileStatus.objects.get(name="ACTIVATED"))
    except:
        verified_users = []
    context = {
        'verified_users':verified_users
    }
    return render(request,'accounts/verified_users.html', context)

def all_users(request):
    try:
        users = User.objects.all()
    except:
        users = []
    context = {
        'users':users
    }
    return render(request,'accounts/users.html', context)


@login_required(login_url='login')
def dashboard(request):
    try:
        all_profiles = Profile.objects.all()
        total_approved = Profile.objects.filter(status=ProfileStatus.objects.get(name="ACTIVATED")).count()
    except:
        all_profiles = []
    context = {
        'users': User.objects.exclude(profile__status=ProfileStatus.objects.get(name="ACTIVATED")).exclude(is_superuser=True),
        'total_users':  User.objects.all().count(),
        'approved_users': Profile.objects.filter(status=ProfileStatus.objects.get(name="ACTIVATED")),
        'all_profiles': all_profiles,
        'total_approved':total_approved
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='login')
def profile(request, username):
    title = username+'s'" Profile"
    profile_details = User.objects.get(username=username)
    try:
        profile_detail = Profile.get_by_id(profile_details.id)
    except:
        profile_detail = Profile.filter_by_id(profile_details.id)
    context = {
        'profile_details': profile_details,
        'profile_detail': profile_detail,
        'title': title

    }
    return render(request, 'profile/profile.html', context)


@login_required(login_url='/accounts/login/')
def edit_profile(request, username):
    title = f"Edit {username}'s Profile"
    try:
        profile_detail = Profile.objects.get(user__username__iexact=username)
    except Profile.DoesNotExist:
        profile_detail = None
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile_detail)
        if form.is_valid():
            edit = form.save(commit=False)
            edit.user = request.user
            edit.date_modified = datetime.now()
            edit.save()
            messages.success(request, 'You successfully updated your profile')
            return redirect('profile', username=username)
        else:
            messages.error(request, 'Error occurred, check if all the fields are filled')
    else:
        form = ProfileForm(instance=profile_detail)

    context = {
        'profile_detail': profile_detail,
        'form': form,
        'title': title,
    }
    return render(request, 'profile/edit_profile.html', context)


@login_required(login_url='login')
def profile(request, username):
    title = username+'s'" Profile"
    profile_details = User.objects.get(username=username)
    try:
        profile_detail = Profile.get_by_id(profile_details.id)
    except:
        profile_detail = Profile.filter_by_id(profile_details.id)
    context = {
        'profile_details': profile_details,
        'profile_detail': profile_detail,
        'title': title

    }
    return render(request, 'profile/profile.html', context)

@login_required(login_url='login')
def user_approve(request, id):   
    users = User.objects.all()
    user = User.objects.get(id=id)
    profile = Profile.objects.filter(user__id=user.id)
    profile.update(status=ProfileStatus.objects.get(name="ACTIVATED"), date_modified=datetime.now(),is_approved=True)

    # Send OTP via email
    subject = "Account Approval"
    message = f"Dear {user.first_name},\n\nYour account has been approved.You may now Login.\n\nRegards,\nThe Weed Detector Team"
    user.email_user(subject, message)

    messages.success(request, 'Account Approved Successfully.')


    context = {
        'profile': Profile.objects.get(user__id=user.id),
        'users':User.objects.all(),
        'users':User.objects.get(id=id),
        'profiles': Profile.objects.filter(status=ProfileStatus.objects.get(name="ACTIVATED"))
    }
    return render(request, 'accounts/user_detail.html', context)

@login_required(login_url ='login')
def user_detail(request, id):
    try:
        users = User.objects.get(id=id)
        profile = Profile.objects.get(user=users)
    except:
        users = []
        profile = []

    context = {
        'users': users,
        'profiles': Profile.objects.filter(status= ProfileStatus.objects.get(name="ACTIVATED")),
        'profile': profile
    }
    return render(request, 'accounts/user_detail.html',context)


def logoutUser(request):
    logout(request)
    messages.success(request, 'You have logged out. Thank you for using our services.')
    return redirect('index')

# function to render the upload form

def upload_image(request):
    if request.method =="POST":
        form = ImageUploadForm(request.POST)
        if form.is_valid():
            pass

        else:
            messages.error(request, 'Invalid form submission.')
    else:
        form = ImageUploadForm()

    return render(request, 'accounts/upload_image.html', {'form': form})