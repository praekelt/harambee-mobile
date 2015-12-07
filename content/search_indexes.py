from haystack import indexes
from celery_haystack.indexes import CelerySearchIndex
from content.models import Module


class ModuleIndex(CelerySearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    name = indexes.CharField(model_attr='title')

    def get_model(self):
        return Module

    # def index_queryset(self, using=None):
    #     # TODO: Fix
    #     """Used when the entire index for model is updated."""
    #     return self.get_model().objects.all()