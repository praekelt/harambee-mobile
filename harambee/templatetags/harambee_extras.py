from bs4 import BeautifulSoup
from django import template
import re
import bleach
from django.utils.html import remove_tags

register = template.Library()


@register.filter
def tabindex(value, index):
    value.field.widget.attrs['tabindex'] = index
    return value


@register.filter(name='streak')
def streak(number, value):
    if value == 0:
        return range(value, number)
    else:
        return range(number+value, 6)


allowed_tags = ['b', 'i', 'strong', 'em', 'img', 'a', 'br']
allowed_attributes = ['href', 'title', 'style', 'src']
allowed_styles = [
    'font-family',
    'font-weight',
    'text-decoration',
    'font-variant',
    'width',
    'height']