from django.db import models
from django.core.exceptions import ValidationError

from worker.models import Worker

class Form(models.Model):
    name = models.CharField(max_length=255)
    workers = models.ManyToManyField(Worker, related_name='forms', blank=True)

    def __str__(self):
        return f"Form: {self.name} (Workers: {self.workers.count()})"

class Question(models.Model):
    TEXT = 'text'
    SINGLE_CHOICE = 'single_choice'
    MULTIPLE_CHOICE = 'multiple_choice'

    QUESTION_TYPES = [
        (TEXT, 'Text'),
        (SINGLE_CHOICE, 'Single Choice'),
        (MULTIPLE_CHOICE, 'Multiple Choice'),
    ]

    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    choices = models.JSONField(default=list, blank=True, null=True)

    def __str__(self):
        return f"Question: {self.title} ({self.get_question_type_display()}) in Form: {self.form.name}"

class FormAnswer(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='answers')
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='form_answers')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"FormAnswer: {self.form.name} by {self.worker.first_name} {self.worker.last_name} on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

class Answer(models.Model):
    form_answer = models.ForeignKey(FormAnswer, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text_answer = models.TextField(blank=True, null=True)
    single_choice_answer = models.CharField(max_length=255, blank=True, null=True)
    multiple_choice_answer = models.JSONField(default=list, blank=True, null=True)

    def clean(self):
        if self.question.question_type == Question.TEXT:
            if not self.text_answer:
                raise ValidationError("Text answer is required for text questions.")
            if self.single_choice_answer or self.multiple_choice_answer:
                raise ValidationError("Only text_answer should be filled for text questions.")
        elif self.question.question_type == Question.SINGLE_CHOICE:
            if not self.single_choice_answer:
                raise ValidationError("Single choice answer is required for single choice questions.")
            if self.single_choice_answer not in self.question.choices:
                raise ValidationError("Invalid choice selected.")
            if self.text_answer or self.multiple_choice_answer:
                raise ValidationError("Only single_choice_answer should be filled for single choice questions.")
        elif self.question.question_type == Question.MULTIPLE_CHOICE:
            if not self.multiple_choice_answer:
                raise ValidationError("Multiple choice answer is required for multiple choice questions.")
            if not all(choice in self.question.choices for choice in self.multiple_choice_answer):
                raise ValidationError("Invalid choices selected.")
            if self.text_answer or self.single_choice_answer:
                raise ValidationError("Only multiple_choice_answer should be filled for multiple choice questions.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Answer to '{self.question.title}' by {self.form_answer.worker.first_name} {self.form_answer.worker.last_name} in Form '{self.form_answer.form.name}'"