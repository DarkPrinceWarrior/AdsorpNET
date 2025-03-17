from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
MODELS_DIR = BASE_DIR / "saved_models"
SCALERS_DIR = BASE_DIR / "saved_scalers"

# Конфигурация моделей
MODEL_CONFIG = {
    'metal_binary_classifier': {
        'path': MODELS_DIR / 'dnn_metal_binary_classifier.pth',
        'type': 'pytorch'
    },
    'major_metal_classifier': {
        'path': MODELS_DIR / 'best_major_classifier_metal.pth',
        'type': 'pytorch'
    },
    'minor_metal_classifier': {
        'path': MODELS_DIR / 'best_minor_classifier_metal.pth',
        'type': 'pytorch'
    },
    'ligand_classifier': {
        'path': MODELS_DIR / 'xgb_ligand_classifier.json',
        'type': 'xgboost'
    },
    'solvent_classifier': {
        'path': MODELS_DIR / 'xgb_solvent_classifier.json',
        'type': 'xgboost'
    }
}

# Конфигурация масштабировщиков
SCALER_CONFIG = {
    'binary_metals': SCALERS_DIR / 'scaler_binary_metals.pkl',
    'major_metal': SCALERS_DIR / 'scaler_major_metal.pkl',
    'minor_metal': SCALERS_DIR / 'scaler_minor_metal.pkl',
    'ligand': SCALERS_DIR / 'scaler_ligand.pkl',
    'solvent': SCALERS_DIR / 'scaler_solvent.pkl'
}

# Константы для вычислений
CALCULATION_CONSTANTS = {
    'micropore_volume_factor': 0.034692,
    'benzene_energy_factor': 0.33,
    'pore_width_constant': 12
}