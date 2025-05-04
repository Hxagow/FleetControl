from django.views.generic import TemplateView
from django.shortcuts import redirect

class IndexView(TemplateView):
    template_name = "index.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('organizations_panel')
        return super().dispatch(request, *args, **kwargs) 