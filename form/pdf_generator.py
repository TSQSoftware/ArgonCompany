import os
from datetime import datetime

from PIL import Image, ExifTags
from django.core.files.base import ContentFile
from django.template import Template, Context
from django.template.loader import render_to_string
from django.templatetags.static import static

from argon_company import settings
from form.models import Form, FormAnswer
from tasks.models import Task, TaskAttachment
from worker.models import Worker


def get_image_rotation(image_path):
    try:
        image = Image.open(image_path)
        exif = image.getexif()
        if exif:
            orientation_key = next((key for key, value in ExifTags.TAGS.items() if value == "Orientation"), None)
            if orientation_key:
                orientation = exif.get(orientation_key)
                return {3: 180, 6: 270, 8: 90}.get(orientation, 0)
    except Exception as e:
        print(f"Error reading image EXIF data: {e}")
    return 0


def generate_pdf(html_file_path):
    """Generates a PDF from HTML file using Playwright (synchronous) and returns it as a byte stream."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({'width': 1920, 'height': 1080})
        page.goto(f'file://{html_file_path}')
        pdf_bytes = page.pdf(format='A4', print_background=True, scale=1.0,
                             margin={'left': '10mm', 'right': '10mm', 'top': '10mm', 'bottom': '10mm'})
        browser.close()
    return pdf_bytes


def generate_protocol_pdf(task: Task, form: Form, form_answer: FormAnswer, worker: Worker) -> TaskAttachment | None:
    """Generates a PDF and creates a TaskAttachment."""
    template_path = os.path.join(settings.BASE_DIR, f'form/templates/pdf/protocol_template_{form.id}.html')
    if not os.path.exists(template_path):
        return None

    with open(template_path, "r", encoding="utf-8") as template_file:
        template_content = template_file.read()

    client_signature = task.attachments.filter(type='client_signature').last()
    worker_signature = task.attachments.filter(type='worker_signature').last()

    template = Template(template_content)
    context_data = {
        'form_title': form_answer.form.name,
        'current_date': datetime.now().strftime("%d.%m.%Y"),
        'location': task.get_location(),
        'logo_url': static('assets/logo.png'),
        'contact_info': task.get_contact_info(),
        'task_id': task.id,
        'assigned_to': ", ".join(f'{worker.first_name} {worker.last_name}' for worker in task.workers.all()),
        'due_date': task.deadline.strftime("%d.%m.%Y") if task.deadline else 'N/A',
        'task_status': task.status,
        'client_name': task.client.name if task.client else 'N/A',
        'task_type': task.category,
        'task_notes': task.notes if task.notes else 'No additional notes',
        'completion_date': task.completion_date.strftime("%d.%m.%Y") if task.completion_date else 'N/A',
        'generated_date': datetime.now().strftime("%d.%m.%Y %H:%M"),
        'client_signature_url': (
            os.path.join(settings.MEDIA_ROOT, str(client_signature.image.url).replace(settings.MEDIA_URL, ''))
        ) if client_signature and client_signature.image else None,
        'worker_signature_url': (
            os.path.join(settings.MEDIA_ROOT, str(worker_signature.image.url).replace(settings.MEDIA_URL, ''))
        ) if worker_signature and worker_signature.image else None,
        'client_signature_rotation': get_image_rotation(os.path.join(settings.MEDIA_ROOT,
                                                                     client_signature.image.name)) if client_signature and client_signature.image else 0,
        'worker_signature_rotation': get_image_rotation(os.path.join(settings.MEDIA_ROOT,
                                                                     worker_signature.image.name)) if worker_signature and worker_signature.image else 0,
    }

    for index, answer in enumerate(form_answer.answers.all(), start=1):
        context_data[f'answer_{index}'] = answer.formatted_answer()

    context = Context(context_data)
    html_string = template.render(context)

    html_filename = f"protocol_{form_answer.id}.html"
    html_path = os.path.join(settings.MEDIA_ROOT, 'pdf_reports', html_filename)
    os.makedirs(os.path.dirname(html_path), exist_ok=True)

    with open(html_path, "w", encoding="utf-8") as html_file:
        html_file.write(html_string)

    task_attachment = TaskAttachment.objects.create(
        task=task,
        worker=worker,
        description=f"{worker.first_name} {worker.last_name}\n{form.name}",
        attachment_type="file",
        type='form',
    )

    pdf_bytes = generate_pdf(html_path)
    pdf_filename = f"protocol_{form_answer.id}/{task_attachment.id}.pdf"
    pdf_file = ContentFile(pdf_bytes, name=pdf_filename)

    task_attachment.file = pdf_file
    task_attachment.save()

    # if os.path.exists(html_path):
    # os.remove(html_path)

    return task_attachment


def generate_static_template(form_id: int) -> str:
    form = Form.objects.get(pk=form_id)
    context = {
        'form_title': form.name,
        'current_date': "{{ current_date }}",
        'location': "{{ location }}",
        'task_id': "{{ task_id }}",
        'assigned_to': "{{ assigned_to }}",
        'due_date': "{{ due_date }}",
        'task_status': "{{ task_status }}",
        'client_name': "{{ client_name }}",
        'task_type': "{{ task_type }}",
        'task_notes': "{{ task_notes }}",
        'completion_date': "{{ completion_date }}",
        'contact_info': "{{ contact_info }}",
        'generated_date': "{{ generated_date }}",
        'client_signature_url': "{{ client_signature_url }}",
        'worker_signature_url': "{{ worker_signature_url }}",
        'client_signature_rotation': "{{ client_signature_rotation }}",
        'worker_signature_rotation': "{{ worker_signature_rotation }}",
        'font_path': os.path.join(settings.STATIC_ROOT, 'fonts/'),
        'asset_path': os.path.join(settings.STATIC_ROOT, 'assets/'),
        'category_groups': [],
    }

    categories = {}
    uncategorized = []

    for question in form.questions.all().select_related('category').order_by('category__order', 'pk'):
        question_data = {
            'question': question.title,
            'placeholder': f"{{{{ answer_{question.id} }}}}",
            'subtitle': question.subtitle,
            'question_type': question.question_type,
            'choices': question.choices,
            'media_url': question.media_url,
            'required': question.required,
            'validation_rules': question.validation_rules,
            'sub_questions': [],
            'depends_on': question.depends_on.id if question.depends_on else None,
        }

        for sub_question in question.sub_questions.all():
            question_data['sub_questions'].append({
                'question': sub_question.title,
                'subtitle': sub_question.subtitle,
                'question_type': sub_question.question_type,
                'choices': sub_question.choices,
                'media_url': sub_question.media_url,
                'required': sub_question.required,
                'validation_rules': sub_question.validation_rules,
            })

        if question.category:
            cat_id = question.category.id
            if cat_id not in categories:
                categories[cat_id] = {
                    'name': question.category.name,
                    'description': question.category.description,
                    'show_in_table': question.category.show_in_table,
                    'columns': question.category.columns,
                    'questions': []
                }
            categories[cat_id]['questions'].append(question_data)
        else:
            uncategorized.append(question_data)

    if uncategorized:
        categories['uncategorized'] = {
            'name': '',
            'description': None,
            'show_in_table': False,
            'columns': [],
            'questions': uncategorized
        }

    context['category_groups'] = sorted(
        categories.values(),
        key=lambda x: (x['name'] == 'General Information', x.get('order', 999)))

    context['logo_url'] = os.path.join(context['asset_path'], 'logo.png')

    template_content = render_to_string('protocol_template_base.html', context)
    template_path = os.path.join(settings.BASE_DIR, f'form/templates/pdf/protocol_template_{form_id}.html')
    os.makedirs(os.path.dirname(template_path), exist_ok=True)
    with open(template_path, "w", encoding="utf-8") as file:
        file.write(template_content)

    return template_path
