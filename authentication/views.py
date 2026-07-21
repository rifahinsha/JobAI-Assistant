import json
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from authentication.models import Profile, SavedJob
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from admin_panel.models import Admin
from jobs.models import Job


def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'main.html')


@login_required(login_url='login')
def dashboard(request):
    return render(request, 'index.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('signup')

        myuser = User.objects.create_user(username, email, password)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()

        profile, _ = Profile.objects.get_or_create(user=myuser)
        profile.phone_number = phone_number
        profile.save()

        messages.success(request, "Account Created! Log In With Your Username and Password.")
        return redirect('login')

    return render(request, 'signup.html')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            admin=Admin.objects.get(username=username)
        except Admin.DoesNotExist:
            admin=None

        if admin is not None and admin.check_password(password):
            request.session['admin_id']=admin.id
            return redirect('admin_panel:admin_index')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'login.html')


def logout(request):
    request.session.pop('admin_id', None)
    auth_logout(request)
    messages.success(request, "Logged Out Successfully.")
    return redirect('landing')


@login_required
def profile(request):
    saved_jobs = request.user.saved_jobs.all()
    return render(request, "profile.html", {"saved_jobs": saved_jobs,})


@login_required(login_url="login")
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        remove_pic = request.POST.get('remove_pic')

        if fname:
            user.first_name = fname
        if lname:
            user.last_name = lname
        if email:
            user.email = email
        user.save()

        if phone_number:
            user.profile.phone_number = phone_number

        if remove_pic:
            user.profile.profile_pic = 'profile_pics/default.jpg'
        elif request.FILES.get('profile_pic'):
            user.profile.profile_pic = request.FILES.get('profile_pic')

        user.profile.save()

        messages.success(request, "Profile Updated successfully.")
        return redirect('profile')

    return render(request, 'edit_profile.html')


@login_required(login_url="login")
def chatbot(request):
    return render(request, 'chatbot.html')


@login_required(login_url="login")
def ats_analyzer(request):
    return render(request, 'ats_analyzer.html')


@login_required(login_url="login")
def mock_interview(request):
    return render(request, 'mock_interview.html')


@login_required(login_url="login")
def career_roadmap(request):
    return render(request, 'career_roadmap.html')


@login_required(login_url="login")
def job_openings(request):
    posted_jobs = Job.objects.all().order_by('-created_at')
    return render(request, "job_openings.html", {"posted_jobs": posted_jobs})


@login_required(login_url="login")
def saved_jobs(request):
    jobs=request.user.saved_jobs.all().order_by('-saved_at')
    return render(request,'saved_jobs.html',{"saved_jobs":jobs})


@login_required(login_url="login")
@require_POST
def unsave_job(request):
    adzuna_id=(request.POST.get("id")or"").strip()

    if not adzuna_id:
        return JsonResponse({"error": "Missing job id."}, status=400)
    deleted, _ = SavedJob.objects.filter(user=request.user, adzuna_id=adzuna_id).delete()
    if not deleted:
        return JsonResponse({"status":"not_found"},status=404)
    
    return JsonResponse({"status":"removed"})


@login_required(login_url="login")
def email_cv(request):
    return render(request, 'email_cv.html')


@login_required(login_url="login")
@require_POST
def save_job(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "Invalid request body."}, status=400)

    adzuna_id = str(data.get("id") or "").strip()
    url = data.get("url") or ""

    if not adzuna_id:
        adzuna_id = url

    if not adzuna_id:
        return JsonResponse({"error": "Job is missing an identifier."}, status=400)

    job, created = SavedJob.objects.get_or_create(
        user=request.user,
        adzuna_id=adzuna_id,
        defaults={
            "title": data.get("title") or "",
            "company": data.get("company") or "",
            "location": data.get("location") or "",
            "description": data.get("description") or "",
            "salary_min": data.get("salary_min"),
            "salary_max": data.get("salary_max"),
            "url": url,
            "created": data.get("created") or "",
        },
    )

    if not created:
        return JsonResponse({"status": "already_saved"})

    return JsonResponse({"status":"saved"})


@login_required(login_url="login")
def posted_jobs(request):
    return redirect('job_openings')