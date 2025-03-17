from .temperature_classifier import BaseTemperatureClassifier

class TsynClassifier(BaseTemperatureClassifier):
    """Классификатор для температуры синтеза."""
    
    def __init__(self, device: str = None):
        super().__init__(temp_type='Tsyn', device=device)

class TdryClassifier(BaseTemperatureClassifier):
    """Классификатор для температуры сушки."""
    
    def __init__(self, device: str = None):
        super().__init__(temp_type='Tdry', device=device)

class TregClassifier(BaseTemperatureClassifier):
    """Классификатор для температуры регенерации."""
    
    def __init__(self, device: str = None):
        super().__init__(temp_type='Treg', device=device) 