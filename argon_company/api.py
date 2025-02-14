from argon_company import settings
from ninja import NinjaAPI

from tasks.views import router as order_router
from worker.views import router as worker_router
from form.views import router as form_router

api = NinjaAPI(docs_url='/docs', title="ArgonCompany", version=f"v{settings.VERSION}")

api.add_router('tasks', order_router, tags=['Order'])
api.add_router('worker', worker_router, tags=['Worker'])
api.add_router('form', form_router, tags=['Form'])