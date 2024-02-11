# Base class. Used on Steam source.
class SteamData:
    def __init__(self, req_name, req_std_name, req_appid):
        self.req_name = req_name
        self.req_std_name = req_std_name
        self.req_appid = req_appid

    def get_name(self) -> str:
        return str(self.req_name)
    
    def get_appid(self) -> int:
        return int(self.req_appid)

    def validate_name(self) -> bool:
        if str(self.req_name) != None and str(self.req_name) != '':
            return True
        return False
    

    def to_document(self) -> JSON:
        return {
            'appid': self.req_appid,
            'nome': self.req_name,
            'pdr_nome': self.req_std_name
        }

# Intermediary source. Used on PC Gaming Wiki source.
class GamingWikiData(SteamData):
    def __init__(
        self, req_name, req_std_name, req_appid, req_drm, opt_availability=None, opt_developer=None, 
        opt_genre=None, opt_monetization=None, opt_modes=None, opt_publisher=None, 
        opt_released=None, opt_released_windows=None, opt_removed_drm=None
        ):
        super().__init__(req_name, req_std_name, req_appid)
        self.req_drm = req_drm
        self.opt_availability = opt_availability
        self.opt_developer = opt_developer
        self.opt_genre = opt_genre
        self.opt_monetization = opt_monetization
        self.opt_modes = opt_modes
        self.opt_publisher = opt_publisher
        self.opt_released = opt_released
        self.opt_released_windows = opt_released_windows
        self.opt_removed_drm = opt_removed_drm


    def to_document(self) -> JSON:
        return {
            'appid': self.req_appid,
            'nome': self.req_name,
            'pdr_nome': self.req_std_name,
            'disponivel': self.opt_availability,
            'desenvolvedor': self.opt_developer,
            'genero': self.opt_genre,
            'monetizacao': self.opt_monetization,
            'modos': self.opt_modes,
            'editora': self.opt_publisher,
            'lancamento': self.opt_released,
            'lancamento_windows': self.opt_released_windows,
            'drm_utilizada': self.req_drm,
            'drm_removida': self.opt_removed_drm
        }

# Final source (so far?). Used to gather final data regarding crack status.
class StatusData(GamingWikiData):
    def __init__(self, req_crack_status, req_crack_team, req_drm_crack, req_release_date, req_dates_dif, opt_crack_date=None):
        pass
    

    def to_document(self) -> JSON:
        return {
            'appid': self.req_appid,
            'nome': self.req_name,
            'pdr_nome': self.req_std_name,
            'disponivel': self.opt_availability,
            'desenvolvedor': self.opt_developer,
            'genero': self.opt_genre,
            'monetizacao': self.opt_monetization,
            'modos': self.opt_modes,
            'editora': self.opt_publisher,
            'lancamento': self.opt_released,
            'lancamento_windows': self.opt_released_windows,
            'drm_removida': self.opt_removed_drm,
            'sit_crack': self.req_crack_status,
            'equipe_crack': self.req_crack_team,
            'drm_crack': self.req_drm_crack,
            'lancamento': self.req_release_date,
            'dates_dif': self.req_dates_dif,
            'data_crack': self.opt_crack_date
        }