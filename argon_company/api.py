from django.conf import settings
from ninja import NinjaAPI

from order.views import router as order_router
from worker.views import router as worker_router

api = NinjaAPI(docs_url='/docs', title="ArgonCompany", version=f"v{settings.VERSION}")

api.add_router('order', order_router, tags=['Order'])
api.add_router('worker', worker_router, tags=['Worker'])