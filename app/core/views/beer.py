from django_ccbv.views import TemplateView

from schemaviz import Edge, Node, VisNetwork
from ..models import Beer


class BeerNetworkView(TemplateView):
    template_name = 'core/network.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        vn = VisNetwork()
        qs = (
            Beer.objects.select_related('brewery__city')
        )
        for beer in qs:
            beer_key = f'beer-{beer.pk}'
            brewery = beer.brewery
            brewery_key = f'brewery-{brewery.pk}'
            if beer_key not in vn.nodes:
                vn.nodes[beer_key] = Node(
                    id=beer_key,
                    label=beer.name,
                    group='beer',
                )
                if beer.style:
                    beer_style_key = f'style-{beer.style.pk}'
                    if beer_style_key not in vn.nodes:
                        vn.nodes[beer_style_key] = Node(
                            id=beer_style_key,
                            label=f'{beer.style.name}',
                            group='beer-style'
                        )
                    vn.edges[(beer_style_key, beer_key)].append(Edge(
                        from_=beer_style_key,
                        to=beer_key,
                        dashes=True,
                    ))
            if brewery_key not in vn.nodes:
                vn.nodes[brewery_key] = Node(
                    id=brewery_key,
                    label=f'{brewery.name}',
                    group='brewery',
                )
                if brewery.city:
                    state_key = f'state-{brewery.city.us_state}'
                    if state_key not in vn.nodes:
                        vn.nodes[state_key] = Node(
                            id=state_key,
                            label=f'{brewery.city.us_state}',
                            group='state'
                        )
                    vn.edges[(state_key, brewery_key)].append(Edge(
                        from_=state_key,
                        to=brewery_key,
                        dashes=True,
                        smooth=False,
                    ))
            vn.edges[(brewery_key, beer_key)].append(Edge(
                from_=brewery_key,
                to=beer_key,
            ))
        context['vis_data'] = vn.to_json()
        return context
