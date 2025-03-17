import torch
import torch.nn as nn

class MetalClassifier(nn.Module):
    """Классификатор для определения типа металла"""
    def __init__(self, input_dim):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 1)
        )
    
    def forward(self, x):
        return self.layers(x)

class TransformerClassifier(nn.Module):
    """Классификатор на основе трансформера"""
    def __init__(self, input_dim, num_classes):
        super().__init__()
        self.embedding = nn.Linear(input_dim, 128)
        self.transformer = nn.TransformerEncoderLayer(
            d_model=128,
            nhead=4,
            dim_feedforward=256,
            dropout=0.1
        )
        self.classifier = nn.Linear(128, num_classes)
    
    def forward(self, x):
        x = self.embedding(x).unsqueeze(1)  # Add sequence dimension
        x = self.transformer(x)
        x = x.squeeze(1)  # Remove sequence dimension
        return self.classifier(x)

class TransformerTsynClassifier(TransformerClassifier):
    """Классификатор температуры синтеза"""
    pass

class TransformerTdryClassifier(TransformerClassifier):
    """Классификатор температуры сушки"""
    pass

class TransformerTregClassifier(TransformerClassifier):
    """Классификатор температуры регенерации"""
    pass 