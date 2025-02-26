import os

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from ninja import Router

from argon_company import settings
from form.models import Form, FormAnswer, Question, Answer
from form.pdf_generator import generate_static_template, generate_protocol_pdf
from form.schemas import SimpleFormSchema, FormAnswerSchema, QuestionSchema, AnswerSchema, AnswerUpdateSchema
from tasks.models import Task
from tasks.schemas import TaskSchema
from worker.models import Worker
from worker.worker_auth import worker_auth

router = Router()


@router.get("/forms/own", auth=worker_auth, response=list[SimpleFormSchema])
def get_own_forms(request):
    worker = request.worker

    return Form.objects.filter(workers__in=[worker])


@router.get('/forms/{form_id}/{task_id}/answer', auth=worker_auth, response=FormAnswerSchema)
def get_form_answer(request, form_id: int, task_id: int):
    worker = request.worker

    try:
        return FormAnswer.objects.filter(worker=worker, form_id=form_id, task_id=task_id).get()
    except FormAnswer.DoesNotExist:
        return JsonResponse({'error': 'No such form'}, status=404)


@router.post('/forms/{form_id}/{task_id}/answer', auth=worker_auth, response=FormAnswerSchema)
def create_form_answer(request, form_id: int, task_id: int):
    worker = request.worker

    try:
        form = Form.objects.filter(id=form_id).get()
    except Form.DoesNotExist:
        return JsonResponse({'error': 'No such form'}, status=404)

    if not form.workers.filter(id=worker.id).exists():
        return JsonResponse({'error': 'No such worker'}, status=404)

    try:
        task = Task.objects.filter(id=task_id).get()
    except Task.DoesNotExist:
        return JsonResponse({'error': 'No such task'}, status=404)

    answer = FormAnswer.objects.create(worker=worker, form=form, task=task)

    return answer


@router.get('/questions/{form_id}', auth=worker_auth, response=list[QuestionSchema])
def get_questions(request, form_id: int):
    return Question.objects.filter(form=form_id)


@router.get("/answers/{form_answer_id}", auth=worker_auth, response=list[AnswerSchema])
def get_answers(request, form_answer_id: int):
    return Answer.objects.filter(form_answer=form_answer_id)


@router.get('/answer/{form_id}/{task_id}/{question_id}', auth=worker_auth, response=AnswerSchema)
def get_answer(request, form_id: int, task_id: int, question_id: int):
    worker = request.worker

    form = get_object_or_404(Form, id=form_id)
    if not form.workers.filter(id=worker.id).exists():
        return JsonResponse({'error': 'No such worker'}, status=404)

    get_object_or_404(Task, id=task_id)
    question = get_object_or_404(Question, id=question_id, form=form)
    form_answer = get_object_or_404(FormAnswer, worker=worker, form_id=form_id, task_id=task_id)

    answer, _ = Answer.objects.get_or_create(question=question, form_answer=form_answer)

    return answer


@router.post('/answer/{form_id}/{task_id}/{question_id}', auth=worker_auth, response=AnswerSchema)
def update_answer(request, form_id: int, task_id: int, question_id: int, data: AnswerUpdateSchema):
    worker = request.worker

    form = get_object_or_404(Form, id=form_id)
    if not form.workers.filter(id=worker.id).exists():
        return JsonResponse({'error': 'Worker is not assigned to this form'}, status=403)

    get_object_or_404(Task, id=task_id)

    question = get_object_or_404(Question, id=question_id, form=form)

    form_answer, _ = FormAnswer.objects.get_or_create(
        worker=worker, form_id=form_id, task_id=task_id
    )

    answer_obj, created = Answer.objects.get_or_create(
        question=question,
        form_answer=form_answer
    )

    if question.question_type == 'text':
        answer_obj.text_answer = data.text_answer
    elif question.question_type == 'single_choice':
        answer_obj.single_choice_answer = data.single_choice_answer
    elif question.question_type == 'multiple_choice':
        answer_obj.multiple_choice_answer = data.multiple_choice_answer

    answer_obj.save()

    return answer_obj


@router.post('/form/template/{form_id}')  # FIXME ADMIN AUTH
def generate_template(request, form_id: int):
    template = generate_static_template(form_id)
    return JsonResponse({'success': template is not None}, status=200)


@router.get('/form/template/{form_id}', auth=worker_auth)
def template_exists(request, form_id: int):
    template_path = os.path.join(settings.BASE_DIR, f'form/templates/pdf/protocol_template_{form_id}.html')

    exists = os.path.exists(template_path)
    if not exists:
        generate_static_template(form_id)

    return JsonResponse({'exists': True}, status=200)


@router.post('/form/document/{form_id}/{task_id}/', response=TaskSchema)
def generate_document(request, form_id: int, task_id: int):
    worker = Worker.objects.first()

    form = get_object_or_404(Form, id=form_id)
    task = get_object_or_404(Task, id=task_id)

    if not form.workers.filter(id=worker.id).exists():
        return JsonResponse({'error': 'No such worker'}, status=404)

    answer = get_object_or_404(FormAnswer, worker=worker, form=form, task=task)

    generate_protocol_pdf(task, form, answer, worker)

    return task

