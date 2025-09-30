from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import HTTPException
import logging

log = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Build errors dict keyed by PascalCase field names for client compatibility
        errors = {}
        for err in exc.errors():
            loc = err.get('loc', [])
            if not loc:
                continue
            field = loc[-1]
            parts = str(field).split('_')
            pascal = ''.join(p.title() for p in parts)
            msg = err.get('msg')
            if field == 'role':
                msg = 'Role phải là một trong các giá trị: Admin, Assistant'
            errors.setdefault(pascal, []).append(msg)

        payload = {
            "type": "https://tools.ietf.org/html/rfc9110#section-15.5.1",
            "title": "One or more validation errors occurred.",
            "status": 400,
            "errors": errors,
        }
        log.debug("Validation error on %s: %s", request.url.path, errors)
        return JSONResponse(status_code=400, content=payload)


    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        log.warning("HTTPException on %s: %s", request.url.path, exc.detail)
        payload = {"status": exc.status_code, "detail": exc.detail}
        return JSONResponse(status_code=exc.status_code, content=payload)


    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        # catch-all: log and return a generic 500 payload
        log.exception("Unhandled exception on %s", request.url.path)
        payload = {"status": 500, "detail": "An internal server error occurred."}
        return JSONResponse(status_code=500, content=payload)
