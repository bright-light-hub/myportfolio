from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, Http404
from django.db.models import Q
from .models import Project, Skill, BlogPost, Resume, PersonalInfo
from .forms import ContactForm

def home(request):
    featured_projects = Project.objects.filter(featured=True)[:3]
    skills = Skill.objects.all()[:8]  # Show top 8 skills
    try:
        personal_info = PersonalInfo.objects.first()
    except PersonalInfo.DoesNotExist:
        personal_info = None
    
    context = {
        'featured_projects': featured_projects,
        'skills': skills,
        'personal_info': personal_info,
    }
    return render(request, 'home.html', context)

def about(request):
    try:
        personal_info = PersonalInfo.objects.first()
    except PersonalInfo.DoesNotExist:
        personal_info = None
    
    context = {
        'personal_info': personal_info,
    }
    return render(request, 'about.html', context)

def projects(request):
    project_list = Project.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        project_list = project_list.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tech_stack__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        project_list = project_list.filter(status=status_filter)
    
    context = {
        'projects': project_list,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Project.STATUS_CHOICES,
    }
    return render(request, 'projects.html', context)

def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    related_projects = Project.objects.exclude(slug=slug)[:3]
    
    context = {
        'project': project,
        'related_projects': related_projects,
    }
    return render(request, 'project_detail.html', context)

def skills(request):
    technical_skills = Skill.objects.filter(category='technical')
    soft_skills = Skill.objects.filter(category='soft')
    tools = Skill.objects.filter(category='tools')
    languages = Skill.objects.filter(category='languages')
    
    context = {
        'technical_skills': technical_skills,
        'soft_skills': soft_skills,
        'tools': tools,
        'languages': languages,
    }
    return render(request, 'skills.html', context)

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save message to database
            message_obj = form.save()
            
            # Send email
            try:
                send_mail(
                    subject=f"Portfolio Contact: {form.cleaned_data['subject']}",
                    message=f"""
                    New message from your portfolio website:
                    
                    Name: {form.cleaned_data['name']}
                    Email: {form.cleaned_data['email']}
                    Subject: {form.cleaned_data['subject']}
                    
                    Message:
                    {form.cleaned_data['message']}
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )
                messages.success(request, 'Your message has been sent successfully!')
            except Exception as e:
                messages.warning(request, 'Message saved but email could not be sent. Please check email configuration.')
            
            return redirect('contact')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
    }
    return render(request, 'contact.html', context)

def resume(request):
    try:
        active_resume = Resume.objects.filter(is_active=True).first()
    except Resume.DoesNotExist:
        active_resume = None
    
    context = {
        'resume': active_resume,
    }
    return render(request, 'resume.html', context)

def download_resume(request):
    try:
        active_resume = Resume.objects.filter(is_active=True).first()
        if active_resume and active_resume.file:
            response = HttpResponse(active_resume.file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{active_resume.title}.pdf"'
            return response
    except Resume.DoesNotExist:
        pass
    
    raise Http404("Resume not found")

def blog_list(request):
    posts = BlogPost.objects.filter(status='published')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    
    context = {
        'posts': posts,
        'search_query': search_query,
    }
    return render(request, 'blog/blog_list.html', context)

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    related_posts = BlogPost.objects.filter(status='published').exclude(slug=slug)[:3]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'blog/blog_detail.html', context)


