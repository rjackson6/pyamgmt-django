from ccbv.views import TemplateView

from core.models import Account

from .utils import apps_dataset


class MainView(TemplateView):
    template_name = 'schemaviz/main.html'

    # noinspection PyProtectedMember
    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context.update({
            # 'vis_data': apps_as_dataset(),
            'vis_data': apps_dataset(),
        })
        return context


class AccountView(TemplateView):
    template_name = 'schemaviz/account.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        # hierarchy = Account.objects.get_hierarchy_list()
        hierarchy = Account.objects.get_hierarchy_flat()
        nodes = []
        edges = []
        for n in hierarchy:
            node = {'id': n['pk'], 'label': n['name']}
            nodes.append(node)
            for e in n['child_account_ids']:
                edge = {'from': n['pk'], 'to': e}
                edges.append(edge)
        context.update({
            'vis_data': hierarchy,
            'nodes': nodes,
            'edges': edges,
        })
        return context
