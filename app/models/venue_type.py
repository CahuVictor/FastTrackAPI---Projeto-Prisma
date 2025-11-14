from enum import Enum

class VenueType(str, Enum):
    AUDITORIO = "Auditorio"
    SALAO = "Salao"
    THEATER = "theater"
    STADIUM = "stadium"
    HALL = "hall"
    OPEN_AIR = "open_air"
    
    
# if ("Auditorio" == VenueTypes.AUDITORIO.value):
#     print("igual")
# else:
#     print("diferente")

# print(VenueTypes.AUDITORIO)
# print(VenueTypes.AUDITORIO.value)