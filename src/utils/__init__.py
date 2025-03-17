# src/utils/__init__.py
"""
Пакет утилит проекта AdsorpNET.
Содержит вспомогательные модули, сгруппированные по назначению.
"""

# Импорты из подмодулей UI
from .ui.messages import (
    show_success_message, 
    show_info_message, 
    show_warning_message, 
    show_error_message
)
from .ui.page_config import load_theme_css, load_user_preferences

# Импорты из подмодулей обработки данных
from .data.feature_generation import (
    safe_generate_features, 
    safe_generate_solvent_features
)
from .data.data_processing import (
    validate_input_parameters,
    calculate_derived_parameters,
    normalize_features,
    prepare_features
)

# Импорты из подмодулей производительности
from .performance.batch_processing import BatchProcessor
from .performance.cuda_optimization import CUDAOptimizer
from .performance.profiling import ModelProfiler
from .performance.pruning import ModelPruner
from .performance.quantization import ModelQuantizer

# Импорты из подмодулей хранения
from .storage.cache import create_cache_key, cached_prediction, clear_prediction_cache

__all__ = [
    # UI
    'show_success_message', 'show_info_message', 'show_warning_message', 'show_error_message',
    'load_theme_css', 'load_user_preferences',
    # Data
    'validate_input_parameters', 'calculate_derived_parameters', 
    'normalize_features', 'prepare_features',
    'safe_generate_features', 'safe_generate_solvent_features',
    # Performance
    'BatchProcessor', 'CUDAOptimizer', 'ModelProfiler', 'ModelPruner', 'ModelQuantizer',
    # Storage
    'create_cache_key', 'cached_prediction', 'clear_prediction_cache'
]