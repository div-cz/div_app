# -------------------------------------------------------------------
#                    UTILS.CONTEXT_PRECESSOR.PY
# -------------------------------------------------------------------


# Tyto funkce se přidávájí do SETTINGS.PY -> TEMPLATES

from div_content.models import Userprofile, Favorite
from django.core.cache import cache

from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from div_content.models import Metastats, Usermessage, Userchatsession
#from div_content.models.meta import Metastats


def get_metastats(request):
    """
    Vrací metastats jako globální kontext dostupný ve všech šablonách.
    Cache na 24 hodin – aktualizace probíhá jednou denně v noci.
    """
    data = cache.get("metastats_global")

    if data is None:
        stats = {item.statname: item.value for item in Metastats.objects.all()}
        cache.set("metastats_global", stats, 14400)  # 14400 = 4 hodin
        return {"metastats": stats}

    return {"metastats": data}


def get_userprofile_avatar(request):
    """Returns Userprofile avatar if it is set up; otherwise, it returns the default account image."""
    
    # Default avatar path
    default_avatar = "/img/Account.png"
    
    # Check if the user is authenticated
    if request.user.is_authenticated:
        userprofile = Userprofile.objects.filter(user=request.user.id).first()
        
        # Return the user's avatar if it exists, otherwise return the default avatar
        if userprofile and userprofile.avatar:
            return {
                "avatar_imgpath": "/static/img/avatar/" + userprofile.avatar.imagepath,
                "userprofileinfo": userprofile
            }
        else:
            return {
                "avatar_imgpath": default_avatar,
                "userprofileinfo": userprofile
            }
    else:
        # If the user is not authenticated, return the default avatar
        return {
            "avatar_imgpath": default_avatar,
            "userprofileinfo": None
        }


def get_user_unread_messages(request):
    """Checks if logged user has unread messages and if so it activates notification bell in navbar. """
    # Check if the user is authenticated
    if request.user.is_authenticated:
        instance_user = request.user
        all_chat_sessions = Userchatsession.objects.filter(Q(user1=instance_user) | Q(user2=instance_user))
        has_unread_messages = False

        for session in all_chat_sessions:
            if session.user1 == instance_user:
                message = Usermessage.objects.filter(chatsession=session, sender=session.user2).order_by('-sentat').first()
            else:
                message = Usermessage.objects.filter(chatsession=session, sender=session.user1).order_by('-sentat').first()
            if message and not message.isread:
                has_unread_messages = True
                return {
                    "has_unread_messages": has_unread_messages
                }
            
        return {
            "has_unread_messages": has_unread_messages
        }
    else:
        # If user is not authenticated return False
        return {
            "has_unread_messages": False
        }
