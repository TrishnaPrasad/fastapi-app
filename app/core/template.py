from fastapi.templating import Jinja2Templates

from app.core.flash import get_flash

templates = Jinja2Templates(directory="app/templates")


def render(request, template, **context):
    """
    Common template renderer.

    Automatically injects:
    - request
    - flash messages
    """

    context.update(
        {
            "request": request,
            "flash": get_flash(request),
        }
    )

    return templates.TemplateResponse(
        request=request,
        name=template,
        context=context,
    )
