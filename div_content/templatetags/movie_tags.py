from django import template
from div_content.models import Movie

register = template.Library()

@register.inclusion_tag('tags/film_top10.html')
def nejnovejsi_filmy():
    filmy = Movie.objects.order_by('-releaseyear', 'movieid')[:10]
    return {'nejnovejsi_filmy': filmy}


#{% load my_tags %}
#{% nejnovejsi_filmy %}
