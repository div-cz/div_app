# -------------------------------------------------------------------
#                    UTILS.METAINDEX.PY
# -------------------------------------------------------------------

from div_content.models import Metaindex
from datetime import date

def add_to_metaindex(instance, section):
    from div_content.models import Metaindex
    
    if section == "Book":
        if Metaindex.objects.filter(section="Book", item_id=instance.bookid).exists():
            return "exists"
        Metaindex.objects.create(
            section="Book",
            item_id=instance.bookid,
            title=instance.titlecz or instance.title,
            author=instance.author,
            year=str(instance.year or ""),
            description=(instance.description or "")[:255],
            divrating=str(instance.divrating or "0"),
            img=instance.img,
            url=instance.url
        )
        return "added"
        
    elif section == "Movie":
        if Metaindex.objects.filter(section="Movie", item_id=instance.movieid).exists():
            return "exists"
        Metaindex.objects.create(
            section="Movie",
            item_id=instance.movieid,
            title=instance.titlecz or instance.title,
            author="",
            year=str(instance.releaseyear or ""),
            description=(instance.description or "")[:255],
            divrating=str(instance.divrating or "0"),
            img=instance.img,
            url=instance.url
        )
        return "added"
        
    elif section == "Game":
        if Metaindex.objects.filter(section="Game", item_id=instance.gameid).exists():
            return "exists"
        Metaindex.objects.create(
            section="Game",
            item_id=instance.gameid,
            title=instance.titlecz or instance.title,
            author="",
            year = str(instance.premieredate.year) if instance.premieredate else "",
            description=(instance.descriptioncz or instance.description or "")[:255],
            divrating=str(instance.divrating or "0"),
            img=instance.img,
            url=instance.url
        )
        return "added"
        
        
    return "error"
