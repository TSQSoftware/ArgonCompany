from django.http import JsonResponse
from ninja import Router

from form.models import Form, FormAnswer, Question, Answer
from form.schemas import SimpleFormSchema, FormAnswerSchema, QuestionSchema, AnswerSchema
from form.pdf_generator import generate_static_template, generate_protocol_pdf
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

    answer = FormAnswer.objects.create(worker=worker, form_id=form_id, task_id=task_id)

    return answer


@router.get('/questions/{form_id}', auth=worker_auth, response=list[QuestionSchema])
def get_questions(request, form_id: int):
    return Question.objects.filter(form=form_id)


@router.get("/answers/{form_answer_id}", auth=worker_auth, response=list[AnswerSchema])
def get_answers(request, form_answer_id: int):
    return Answer.objects.filter(form_answer=form_answer_id)


@router.get('/form/document/{answer_id}')
def get_form(request, answer_id: int, form_id: int, task_id: int):
    html_path, pdf_path = generate_protocol_pdf(task_id, form_id, answer_id)

    return JsonResponse({
        "html_path": html_path,
        "pdf_path": pdf_path
    }, )


@router.get('/form/static/{form_id}')
def get_static_form(request, form_id: int):
    return JsonResponse({'output': generate_static_template(form_id)})
