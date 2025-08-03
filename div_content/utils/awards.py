
# -------------------------------------------------------------------
#                    UTILS.AWARDS.PY
# -------------------------------------------------------------------
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime
from div_content.models import (
    Metaaward, Movieaward, Bookaward, Gameaward,
    Movie, Book, Game
)

class AwardUtils:
    """Pomocné funkce pro práci s oceněními"""
    
    @staticmethod
    def get_award_statistics():
        """Vrátí základní statistiky o oceněních"""
        return {
            'total_awards': Metaaward.objects.count(),
            'movie_awards': Movieaward.objects.count(),
            'book_awards': Bookaward.objects.count(),
            'game_awards': Gameaward.objects.count(),
            'total_winners': (
                Movieaward.objects.filter(winner=True).count() +
                Bookaward.objects.filter(winner=True).count() +
                Gameaward.objects.filter(winner=True).count()
            ),
            'recent_years': Metaaward.objects.values_list('year', flat=True).distinct().order_by('-year')[:5],
        }
    
    @staticmethod
    def get_popular_awards(limit=10):
        """Vrátí nejpopulárnější ocenění (podle počtu nominací)"""
        awards_with_counts = []
        
        # Filmová ocenění
        movie_awards = Metaaward.objects.filter(awardtype='film').annotate(
            nomination_count=Count('movieaward')
        ).filter(nomination_count__gt=0).order_by('-nomination_count')[:limit]
        
        # Knižní ocenění
        book_awards = Metaaward.objects.filter(awardtype='book').annotate(
            nomination_count=Count('bookaward')
        ).filter(nomination_count__gt=0).order_by('-nomination_count')[:limit]
        
        # Herní ocenění
        game_awards = Metaaward.objects.filter(awardtype='game').annotate(
            nomination_count=Count('gameaward')
        ).filter(nomination_count__gt=0).order_by('-nomination_count')[:limit]
        
        return {
            'movie_awards': movie_awards,
            'book_awards': book_awards,
            'game_awards': game_awards,
        }
    
    @staticmethod
    def search_awards(query, award_type=None, year=None):
        """Vyhledá ocenění podle zadaných kritérií"""
        awards = Metaaward.objects.all()
        
        if query:
            awards = awards.filter(
                Q(awardname__icontains=query) |
                Q(description__icontains=query)
            )
        
        if award_type:
            awards = awards.filter(awardtype=award_type)
        
        if year:
            awards = awards.filter(year=year)
        
        return awards.order_by('-year', 'awardname')
    
    @staticmethod
    def get_winners_by_media(media_type, limit=20):
        """Vrátí vítěze podle typu média"""
        if media_type == 'movie':
            return Movieaward.objects.filter(winner=True).select_related(
                'metaAwardid', 'movieid'
            ).order_by('-metaAwardid__year')[:limit]
        elif media_type == 'book':
            return Bookaward.objects.filter(winner=True).select_related(
                'metaAwardid', 'bookid'
            ).order_by('-metaAwardid__year')[:limit]
        elif media_type == 'game':
            return Gameaward.objects.filter(winner=True).select_related(
                'metaawardid', 'gameid'
            ).order_by('-metaawardid__year')[:limit]
        
        return []
    
    @staticmethod
    def bulk_create_nominees(award, nominees_data, media_type):
        """Hromadné vytvoření nominací"""
        created_count = 0
        errors = []
        
        for nominee_data in nominees_data:
            try:
                if media_type == 'movie':
                    movie = Movie.objects.get(id=nominee_data['id'])
                    nominee, created = Movieaward.objects.get_or_create(
                        metaAwardid=award,
                        movieid=movie,
                        defaults={'winner': nominee_data.get('winner', False)}
                    )
                elif media_type == 'book':
                    book = Book.objects.get(id=nominee_data['id'])
                    nominee, created = Bookaward.objects.get_or_create(
                        metaAwardid=award,
                        bookid=book,
                        defaults={'winner': nominee_data.get('winner', False)}
                    )
                elif media_type == 'game':
                    game = Game.objects.get(id=nominee_data['id'])
                    nominee, created = Gameaward.objects.get_or_create(
                        metaawardid=award,
                        gameid=game,
                        defaults={'winner': nominee_data.get('winner', False)}
                    )
                
                if created:
                    created_count += 1
                    
            except Exception as e:
                errors.append(f"Chyba při vytváření nominace: {str(e)}")
        
        return created_count, errors
    
    @staticmethod
    def validate_award_data(award_name, year, award_type):
        """Validuje data pro ocenění"""
        errors = []
        
        # Kontrola roku
        current_year = datetime.now().year
        if year < 1900 or year > current_year + 5:
            errors.append(f"Neplatný rok: {year}")
        
        # Kontrola typu
        valid_types = ['film', 'book', 'game']
        if award_type not in valid_types:
            errors.append(f"Neplatný typ ocenění: {award_type}")
        
        # Kontrola duplicity
        if Metaaward.objects.filter(awardname=award_name, year=year).exists():
            errors.append(f"Ocenění '{award_name}' pro rok {year} již existuje")
        
        return errors
    
    @staticmethod
    def get_award_timeline(award_name, limit=10):
        """Vrátí časovou osu pro konkrétní ocenění"""
        awards = Metaaward.objects.filter(awardname=award_name).order_by('-year')[:limit]
        timeline = []
        
        for award in awards:
            data = {
                'award': award,
                'nominees': [],
                'winners': []
            }
            
            if award.awardtype == 'film':
                nominees = Movieaward.objects.filter(metaAwardid=award).select_related('movieid')
                data['nominees'] = nominees.filter(winner=False)
                data['winners'] = nominees.filter(winner=True)
            elif award.awardtype == 'book':
                nominees = Bookaward.objects.filter(metaAwardid=award).select_related('bookid')
                data['nominees'] = nominees.filter(winner=False)
                data['winners'] = nominees.filter(winner=True)
            elif award.awardtype == 'game':
                nominees = Gameaward.objects.filter(metaawardid=award).select_related('gameid')
                data['nominees'] = nominees.filter(winner=False)
                data['winners'] = nominees.filter(winner=True)
            
            timeline.append(data)
        
        return timeline
    
    @staticmethod
    def get_most_awarded_items(media_type='all', limit=10):
        """Vrátí nejčastěji oceňované položky"""
        result = {}
        
        if media_type in ['all', 'movie']:
            movies = Movie.objects.annotate(
                award_count=Count('movieaward'),
                win_count=Count('movieaward', filter=Q(movieaward__winner=True))
            ).filter(award_count__gt=0).order_by('-win_count', '-award_count')[:limit]
            result['movies'] = movies
        
        if media_type in ['all', 'book']:
            books = Book.objects.annotate(
                award_count=Count('bookaward'),
                win_count=Count('bookaward', filter=Q(bookaward__winner=True))
            ).filter(award_count__gt=0).order_by('-win_count', '-award_count')[:limit]
            result['books'] = books
        
        if media_type in ['all', 'game']:
            games = Game.objects.annotate(
                award_count=Count('gameaward'),
                win_count=Count('gameaward', filter=Q(gameaward__winner=True))
            ).filter(award_count__gt=0).order_by('-win_count', '-award_count')[:limit]
            result['games'] = games
        
        return result
    
    @staticmethod
    def export_award_data(award, format='json'):
        """Exportuje data ocenění do různých formátů"""
        data = {
            'award': {
                'name': award.awardname,
                'year': award.year,
                'type': award.awardtype,
                'description': award.description,
            },
            'nominees': [],
            'winners': []
        }
        
        if award.awardtype == 'film':
            nominees = Movieaward.objects.filter(metaAwardid=award).select_related('movieid')
            for nominee in nominees:
                item_data = {
                    'title': nominee.movieid.titlecz or nominee.movieid.title,
                    'original_title': nominee.movieid.title,
                    'year': nominee.movieid.releaseyear,
                    'is_winner': nominee.winner
                }
                if nominee.winner:
                    data['winners'].append(item_data)
                else:
                    data['nominees'].append(item_data)
        
        # Podobně pro knihy a hry...
        
        if format == 'json':
            import json
            return json.dumps(data, ensure_ascii=False, indent=2)
        elif format == 'csv':
            # CSV export implementace
            pass
        
        return data

# Pomocné funkce pro admin
def get_admin_award_context(award):
    """Vrátí kontext pro admin stránky"""
    context = {
        'award': award,
        'total_nominees': 0,
        'total_winners': 0,
        'nominees_by_type': {}
    }
    
    if award.awardtype == 'film':
        nominees = Movieaward.objects.filter(metaAwardid=award)
        context['total_nominees'] = nominees.count()
        context['total_winners'] = nominees.filter(winner=True).count()
        context['nominees_by_type']['movies'] = nominees.select_related('movieid')
    elif award.awardtype == 'book':
        nominees = Bookaward.objects.filter(metaAwardid=award)
        context['total_nominees'] = nominees.count()
        context['total_winners'] = nominees.filter(winner=True).count()
        context['nominees_by_type']['books'] = nominees.select_related('bookid')
    elif award.awardtype == 'game':
        nominees = Gameaward.objects.filter(metaawardid=award)
        context['total_nominees'] = nominees.count()
        context['total_winners'] = nominees.filter(winner=True).count()
        context['nominees_by_type']['games'] = nominees.select_related('gameid')
    
    return context