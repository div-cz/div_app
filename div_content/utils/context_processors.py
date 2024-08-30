from div_content.models import Userprofile

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
