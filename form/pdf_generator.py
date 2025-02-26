import asyncio
import os
from datetime import datetime

from django.conf import settings
from django.core.files.base import ContentFile
from django.template import Template, Context
from django.template.loader import render_to_string
from django.templatetags.static import static
from pyppeteer import launch

from form.models import Form, FormAnswer
from tasks.models import Task, TaskAttachment
from worker.models import Worker


async def generate_pdf_with_pyppeteer(html_content):
    """Generates a PDF from HTML using Pyppeteer and returns it as a byte stream."""
    browser = await launch(headless=True, handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False)
    page = await browser.newPage()
    await page.setContent(html_content)
    pdf_bytes = await page.pdf({
        'format': 'A4',
        'printBackground': True,
        'scale': 1.0,
        'margin': {
            'left': '10mm',
            'right': '10mm',
            'top': '10mm',
            'bottom': '10mm',
        }
    })
    await browser.close()
    return pdf_bytes


def generate_protocol_pdf(task: Task, form: Form, form_answer: FormAnswer, worker: Worker) -> TaskAttachment | None:
    """Generates a PDF and creates a TaskAttachment."""

    template_path = os.path.join(settings.BASE_DIR, f'form/templates/pdf/protocol_template_{form.id}.html')
    if not os.path.exists(template_path):
        return None

    with open(template_path, "r", encoding="utf-8") as template_file:
        template_content = template_file.read()

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
    }

    for index, answer in enumerate(form_answer.answers.all(), start=1):
        context_data[f'answer_{index}'] = answer.formatted_answer()

    context = Context(context_data)
    html_string = template.render(context)
    pdf_bytes = asyncio.run(generate_pdf_with_pyppeteer(html_string))
    pdf_filename = f"protocol_{form_answer.id}.pdf"
    pdf_file = ContentFile(pdf_bytes, name=pdf_filename)
    task_attachment = TaskAttachment(
        task=task,
        worker=worker,
        file=pdf_file,
        description=f"Protokół {worker.first_name} {worker.last_name}",
        attachment_type="file",
    )

    task_attachment.save()
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
