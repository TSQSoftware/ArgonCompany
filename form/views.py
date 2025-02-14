from ninja import Router

from form.models import Form, FormAnswer, Question, Answer
from form.schemas import SimpleFormSchema, FormAnswerSchema, QuestionSchema, AnswerSchema
from worker.worker_auth import worker_auth

router = Router()

@router.get("/forms/own", auth=worker_auth, response=list[SimpleFormSchema])
def get_own_forms(request):
    worker = request.worker

    return Form.objects.filter(workers__in=[worker])

@router.get('/forms/{form_id}/answers', auth=worker_auth, response=list[FormAnswerSchema])
def get_form_answers(request, form_id: int):
    worker = request.worker

    return FormAnswer.objects.filter(worker=worker, form_id=form_id)

@router.get('/questions/{form_id}', auth=worker_auth, response=list[QuestionSchema])
def get_questions(request, form_id: int):
    return Question.objects.filter(form=form_id)

@router.get("/answers/{form_answer_id}", auth=worker_auth, response=list[AnswerSchema])
def get_answers(request, form_answer_id: int):
    return Answer.objects.filter(form_answer=form_answer_id)