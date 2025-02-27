from typing import Optional, Any

import jwt
from django.http import HttpRequest
from ninja.security import HttpBearer

from argon_company import settings
from worker.models import Worker


class WorkerAuth(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> Optional[Any]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            worker_id = payload.get('worker_id')

            worker = Worker.objects.get(id=worker_id)
            request.worker = worker
            return worker
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Worker.DoesNotExist):
            return None

worker_auth = WorkerAuth()