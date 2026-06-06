from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import ConfiguracionEmpresa

def render_to_pdf(template_src, context_dict=None):
    if context_dict is None:
        context_dict = {}
    if 'empresa_config' not in context_dict:
        context_dict['empresa_config'] = ConfiguracionEmpresa.objects.first()
        
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
