from django import template
from ..models import Flower, GalleryFlower

register = template.Library()


@register.simple_tag
def update_variable(value):
    return value