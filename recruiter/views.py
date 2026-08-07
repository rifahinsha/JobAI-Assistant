from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from jobs.models import Job
from .decorators import recruiter_required
from .forms import RecruiterJobForm
from .models import Application

ALLOWED_CV_EXTENSIONS=('.pdf', '.doc', '.docx')
MAX_CV_SIZE_BYTES = 5 * 1024 * 1024


@recruiter_required
def dashboard(request):
    jobs = Job.objects.filter(posted_by=request.user)
    applications = Application.objects.filter(job__posted_by=request.user)

    context = {
        'job_count': jobs.count(),
        'applicant_count': applications.count(),
        'shortlisted_count': applications.filter(status=Application.STATUS_SHORTLISTED).count(),
        'recent_jobs': jobs.order_by('-created_at')[:5],
        'recent_applications': applications.select_related('job', 'applicant')[:5],
    }
    return render(request, 'recruiter_index.html', context)


@recruiter_required
def job_list(request):
    jobs = Job.objects.filter(posted_by=request.user).order_by('-created_at')
    applicant_counts = {
        row['job']: row['count']
        for row in Application.objects.filter(job__posted_by=request.user)
        .values('job')
        .annotate(count=Count('id'))
    }
    for job in jobs:
        job.applicant_count = applicant_counts.get(job.id, 0)
    return render(request, 'recruiter_job_list.html', {'jobs': jobs})


@recruiter_required
def job_create(request):
    if request.method == 'POST':
        form = RecruiterJobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, 'Job posted.')
            return redirect('recruiter:job_list')
    else:
        form = RecruiterJobForm()
    return render(request, 'recruiter_job_form.html', {'form': form, 'action': 'Post'})


@recruiter_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk, posted_by=request.user)
    if request.method == 'POST':
        form = RecruiterJobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated.')
            return redirect('recruiter:job_list')
    else:
        form = RecruiterJobForm(instance=job)
    return render(request, 'recruiter_job_form.html', {'form': form, 'action': 'Edit'})


@recruiter_required
@require_POST
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk, posted_by=request.user)
    job.delete()
    return JsonResponse({"status": "deleted"})


@recruiter_required
def applicants(request, pk):
    job = get_object_or_404(Job, pk=pk, posted_by=request.user)
    apps = job.applications.select_related('applicant', 'applicant__profile').order_by('-applied_at')
    return render(request, 'recruiter_applicants.html', {'job': job, 'applications': apps})


@recruiter_required
def shortlisted_candidates(request):
    apps = (
        Application.objects.filter(job__posted_by=request.user, status=Application.STATUS_SHORTLISTED)
        .select_related('job', 'applicant', 'applicant__profile')
        .order_by('-updated_at')
    )
    return render(request, 'recruiter_shortlisted.html', {'applications': apps})


@recruiter_required
@require_POST
def update_application_status(request, pk):
    application = get_object_or_404(Application, pk=pk, job__posted_by=request.user)
    status = request.POST.get('status')
    if status not in dict(Application.STATUS_CHOICES):
        return JsonResponse({"error": "Invalid status."}, status=400)
    application.status = status
    application.save(update_fields=['status', 'updated_at'])
    return JsonResponse({"status": "updated", "new_status": application.get_status_display()})


@login_required(login_url='login')
@require_POST
def apply_job(request, pk):
    job = get_object_or_404(Job, pk=pk)

    if job.posted_by_id == request.user.id:
        messages.error(request, "You can't apply to your own job posting.")
        return redirect('job_openings')

    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.info(request, f"You've already applied to {job.title}.")
        return redirect('job_openings')

    cv = request.FILES.get('cv')
    if not cv:
        messages.error(request, "Please attach your CV to apply.")
        return redirect('job_openings')

    if not cv.name.lower().endswith(ALLOWED_CV_EXTENSIONS):
        messages.error(request, "CV must be a PDF or Word document (.pdf, .doc, .docx).")
        return redirect('job_openings')

    if cv.size > MAX_CV_SIZE_BYTES:
        messages.error(request, "CV file is too large (max 5 MB).")
        return redirect('job_openings')

    try:
        Application.objects.get_or_create(
            job=job,
            applicant=request.user,
            defaults={'cover_note': request.POST.get('cover_note', ''), 'cv': cv}
        )
    except IntegrityError:
        messages.info(request, f"You've already applied to {job.title}.")
        return redirect('job_openings')

    
    messages.success(request, f"Applied to {job.title}.")
    return redirect('job_openings')