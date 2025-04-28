from enum import StrEnum


class PpdaStatus(StrEnum):
    DRAFT             = "borrador"            # Equipo MMA/SEREMI redactando
    PUBLIC_REVIEW     = "consulta pública"    # Periodo de observaciones
    AWAITING_APPROVAL = "en toma de razón"    # En Contraloría / DO
    ACTIVE            = "vigente"             # Plan en plena ejecución
    UNDER_REVISION    = "en revisión"         # Modificación parcial
    SUPERSEDED        = "reemplazado"         # Sustituido por un nuevo PPDA
    COMPLETED         = "finalizado"          # Metas cumplidas
    REPEALED          = "derogado"            # Anulado sin reemplazo