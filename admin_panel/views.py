from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from jobs.models import Job
from recruiter.models import Application
from .decorators import admin_required
from .forms import JobForm


@admin_required
def admin_index(request):
    jobs = Job.objects.all()
    applications = Application.objects.all()

    context = {
        'job_count': jobs.count(),
        'user_count': User.objects.count(),
        'application_count': applications.count(),
        'shortlisted_count': applications.filter(status=Application.STATUS_SHORTLISTED).count(),
        'recent_jobs': jobs.order_by('-created_at')[:5],
    }
    return render(request, 'admin_index.html', context)


@admin_required
def job_list(request):
    jobs = Job.objects.all().order_by('-created_at')
    applicant_counts = {
        row['job']: row['count']
        for row in Application.objects.values('job').annotate(count=Count('id'))
    }
    for job in jobs:
        job.applicant_count = applicant_counts.get(job.id, 0)
    return render(request, 'job_list.html', {'jobs': jobs})


@admin_required
def job_create(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job created.')
            return redirect('admin_panel:job_list')
    else:
        form = JobForm()
    return render(request, 'job_form.html', {'form': form, 'action': 'Create'})


@admin_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated.')
            return redirect('admin_panel:job_list')
    else:
        form = JobForm(instance=job)
    return render(request, 'job_form.html', {'form': form, 'action': 'Edit'})


@admin_required
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk)
    job.delete()
    return JsonResponse({"Status": "Deleted"})


@admin_required
def applicants(request, pk):
    job = get_object_or_404(Job, pk=pk)
    apps = job.applications.select_related('applicant', 'applicant__profile').order_by('-applied_at')
    return render(request, 'admin_applicants.html', {'job': job, 'applications': apps})


@admin_required
@require_POST
def update_application_status(request, pk):
    application = get_object_or_404(Application, pk=pk)
    status = request.POST.get('status')
    if status not in dict(Application.STATUS_CHOICES):
        return JsonResponse({"error": "Invalid status."}, status=400)
    application.status = status
    application.save(update_fields=['status', 'updated_at'])
    return JsonResponse({"status": "updated", "new_status": application.get_status_display()})


@admin_required
def shortlisted_candidates(request):
    apps = (
        Application.objects.filter(status=Application.STATUS_SHORTLISTED)
        .select_related('job', 'applicant', 'applicant__profile')
        .order_by('-updated_at')
    )
    return render(request, 'admin_shortlisted.html', {'applications': apps})