from haystack import indexes
from content.models import Module


class ModuleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    name = indexes.CharField(model_attr='title')
    search_description = indexes.CharField(model_attr='search')

    def get_model(self):
        return Module
