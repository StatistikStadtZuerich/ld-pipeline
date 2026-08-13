from .observation_embargoed import ObservationEmbargoed


class ObservationFastView(ObservationEmbargoed):
    """
    Rendert eine (veröffentlichte oder embargoed) Observation-Menge,
    gefiltert auf bestimmte Referenznummern, für einen Fast-View-Lauf.

    Identische Single-File-Gzip-Logik wie ObservationEmbargoed (ein
    gzip-File nach template_output_path/locked, kein Batching).
    Wird für 'view_observation' (veröffentlichte Daten) und 'view_observation_embargoed'
    (Daten mit Sperrfrist) genutzt, siehe main.get_step_definitions().
    """
