from collections import defaultdict

from django_ccbv.views import TemplateView

from schemaviz import Edge, Node, NodeFont, VisNetwork

from ..models import Beer


class BeerNetworkView(TemplateView):
    template_name = 'core/network.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        qs = (
            Beer.objects.select_related('brewery__city')
        )
        nodes = {}
        edges = []
        for beer in qs:
            beer_key = f'beer-{beer.pk}'
            brewery = beer.brewery
            brewery_key = f'brewery-{brewery.pk}'
            if beer_key not in nodes:
                nodes[beer_key] = Node(
                    id=beer_key,
                    label=beer.name,
                    group='beer',
                )
                if beer.style:
                    beer_style_key = f'style-{beer.style.pk}'
                    if beer_style_key not in nodes:
                        nodes[beer_style_key] = Node(
                            id=beer_style_key,
                            label=f'{beer.style.name}',
                            group='beer-style'
                        )
                    edges.append(Edge(
                        from_=beer_style_key,
                        to=beer_key,
                        dashes=True,
                    ))
            if brewery_key not in nodes:
                nodes[brewery_key] = Node(
                    id=brewery_key,
                    label=f'{brewery.name}',
                    group='brewery',
                )
                if brewery.city:
                    state_key = f'state-{brewery.city.us_state}'
                    if state_key not in nodes:
                        nodes[state_key] = Node(
                            id=state_key,
                            label=f'{brewery.city.us_state}',
                            group='state'
                        )
                    edges.append(Edge(
                        from_=state_key,
                        to=brewery_key,
                        dashes=True,
                        length=500,
                    ))
            edges.append(Edge(
                from_=brewery_key,
                to=beer_key,
            ))
        vis_data = VisNetwork(list(nodes.values()), edges)
        context['vis_data'] = vis_data.to_dict()
        return context
