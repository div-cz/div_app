from django import template
from django.utils.safestring import mark_safe
from div_content.models import Userprofile
import re

register = template.Library()

@register.filter
def get_parent_comment(queryset, pk):
    return queryset.get(forumcommentid=pk)


# def highlight_search(text, search):
#     text = text.lower()
#     search = search.lower()
#     highlighted = text.replace(search, '<span style="background-color:#CABAC8;">{}</span>'.format(search))
#     return mark_safe(highlighted)
@register.filter
def highlight_search(text, search):
    search_pattern = re.compile(re.escape(search), re.IGNORECASE)

    def replace_match(match):
        return f'<span style="background-color:#CABAC8;">{match.group(0)}</span>'

    # Rozdělí text podle HTML tagů
    parts = re.split(r'(<[^>]+>)', text)

    # Bere sudé prvky listu = text
    for i in range(0, len(parts), 2):
        parts[i] = search_pattern.sub(replace_match, parts[i])

    highlighted_text = ''.join(parts)
    return mark_safe(highlighted_text)


@register.simple_tag
def get_user_avatar(user):
    try:
        user_profile = Userprofile.objects.filter(user=user.id).first()
        if user_profile.avatar:
            return "/static/img/avatar/" + user_profile.avatar.imagepath
        else:
            return "/img/Account-black.png"
    except Exception as e:
        return "/img/Account-black.png"