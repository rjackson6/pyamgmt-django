from ccbv.views import TemplateView

from .utils import apps_as_dataset


class MainView(TemplateView):
    template_name = 'schemaviz/main.html'

    # noinspection PyProtectedMember
    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context.update({
            'vis_data': apps_as_dataset(),
        })
        return context
