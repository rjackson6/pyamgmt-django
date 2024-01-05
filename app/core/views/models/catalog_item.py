from django_ccbv import DetailView, ListView

from core.models import CatalogItem


class CatalogItemListView(ListView):
    model = CatalogItem
    template_name = 'core/models/catalog-item--list.html'


class CatalogItemDetailView(DetailView):
    model = CatalogItem
    template_name = 'core/models/catalog-item--detail.html'
