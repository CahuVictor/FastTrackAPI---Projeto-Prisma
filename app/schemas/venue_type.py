from enum import Enum

class VenueTypes(str, Enum):
    AUDITORIO = "Auditorio"
    SALAO = "Salao"
    
    
# if ("Auditorio" == VenueTypes.AUDITORIO.value):
#     print("igual")
# else:
#     print("diferente")

# print(VenueTypes.AUDITORIO)
# print(VenueTypes.AUDITORIO.value)