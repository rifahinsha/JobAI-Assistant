from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from jobs.models import Job
from .decorators import admin_required
from .forms import JobForm


@admin_required
def admin_index(request):
    return render(request, 'admin_index.html')


@admin_required
def job_list(request):
    jobs = Job.objects.all().order_by('-created_at')
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
    return JsonResponse({"Status":"Deleted"})
