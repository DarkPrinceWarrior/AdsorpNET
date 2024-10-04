import streamlit as st
import torch
import torch.nn as nn
import torch.nn.functional as F
import joblib
import pandas as pd
import numpy as np

# ======================================
# 1. Define the Model Architecture
# ======================================

# Define feature names as used during training
features_metal = [
    "W0, см3/г",
    "E0, кДж/моль",
    "х0, нм",
    "а0, ммоль/г",
    "E,  кДж/моль",
    "SБЭТ, м2/г",
    "Ws, см3/г",
    "Sme, м2/г",
    "Wme, см3/г",
    "Adsorption_Potential",
    "Capacity_Density",
    "K_equilibrium",
    "Delta_G",
    "SurfaceArea_MicroVol_Ratio",
    "Adsorption_Energy_Ratio",
    "S_BET_E",
    "x0_W0",
    "B_micropore",
]


features_ligand = [
    "W0, см3/г",
    "E0, кДж/моль",
    "х0, нм",
    "а0, ммоль/г",
    "E,  кДж/моль",
    "SБЭТ, м2/г",
    "Ws, см3/г",
    "Sme, м2/г",
    "Wme, см3/г",
    "Adsorption_Potential",
    "Capacity_Density",
    "K_equilibrium",
    "Delta_G",
    "SurfaceArea_MicroVol_Ratio",
    "Adsorption_Energy_Ratio",
    "S_BET_E",
    "x0_W0",
    "B_micropore",
    
    "Металл_Al",
    "Металл_Cu",
    "Металл_Fe",
    "Металл_La",
    "Металл_Zn",
    "Металл_Zr",
    
    "Total molecular weight (metal)",
    "Average ionic radius (metal)",
    "Average electronegativity (metal)",
]

features_solvent = [
    "W0, см3/г",
    "E0, кДж/моль",
    "х0, нм",
    "а0, ммоль/г",
    "E,  кДж/моль",
    "SБЭТ, м2/г",
    "Ws, см3/г",
    "Sme, м2/г",
    "Wme, см3/г",
    "Adsorption_Potential",
    "Capacity_Density",
    "K_equilibrium",
    "Delta_G",
    "SurfaceArea_MicroVol_Ratio",
    "Adsorption_Energy_Ratio",
    "S_BET_E",
    "x0_W0",
    "B_micropore",
    
    "Металл_Al",
    "Металл_Cu",
    "Металл_Fe",
    "Металл_La",
    "Металл_Zn",
    "Металл_Zr",
    
    "Total molecular weight (metal)",
    "Average ionic radius (metal)",
    "Average electronegativity (metal)",
    
    "Молярка_соли",
    "Молярка_кислоты",
    
    "Лиганд_BDC",
    "Лиганд_BTB",
    "Лиганд_BTC",
    
    "carboxyl_groups (ligand)",
    "aromatic_rings (ligand)",
    "carbon_atoms (ligand)",
    "oxygen_atoms (ligand)",
    "nitrogen_atoms (ligand)",
    "molecular_weight (ligand)",
    "amino_groups (ligand)",
    "logP (ligand)",
    "TPSA (ligand)",
    "h_bond_acceptors (ligand)",
    "h_bond_donors (ligand)",
    
]

features_salt_mass = [
    'W0, см3/г', 'E0, кДж/моль', 'х0, нм', 'а0, ммоль/г', 'E,  кДж/моль',
    'SБЭТ, м2/г', 'Ws, см3/г', 'Sme, м2/г', 'Wme, см3/г', 
    'Adsorption_Potential', 'Capacity_Density', 'K_equilibrium', 'Delta_G', 
    'SurfaceArea_MicroVol_Ratio', 'Adsorption_Energy_Ratio', 'S_BET_E', 'x0_W0',"B_micropore",
    
     'Металл_Al', 'Металл_Cu', 'Металл_Fe', 'Металл_La', 'Металл_Zn',
       'Металл_Zr', 'Total molecular weight (metal)', 
    'Average ionic radius (metal)', 'Average electronegativity (metal)',
    
    'Молярка_соли','Молярка_кислоты',
    
    'Лиганд_BDC', 'Лиганд_BTB', 'Лиганд_BTC',
    
    'carboxyl_groups (ligand)', 'aromatic_rings (ligand)',
       'carbon_atoms (ligand)', 'oxygen_atoms (ligand)',
       'nitrogen_atoms (ligand)', 'molecular_weight (ligand)',
       'amino_groups (ligand)', 'logP (ligand)', 'TPSA (ligand)',
       'h_bond_acceptors (ligand)', 'h_bond_donors (ligand)',
       
       'Растворитель_ДМФА', 'Растворитель_ДМФА/Этанол/Вода',
       'MolWt', 'LogP', 'NumHDonors',
       'NumHAcceptors'
]


features_acid_mass = [
    'W0, см3/г', 'E0, кДж/моль', 'х0, нм', 'а0, ммоль/г', 'E,  кДж/моль',
    'SБЭТ, м2/г', 'Ws, см3/г', 'Sme, м2/г', 'Wme, см3/г', 
    'Adsorption_Potential', 'Capacity_Density', 'K_equilibrium', 'Delta_G', 
    'SurfaceArea_MicroVol_Ratio', 'Adsorption_Energy_Ratio', 'S_BET_E', 'x0_W0',"B_micropore",
    
     'Металл_Al', 'Металл_Cu', 'Металл_Fe', 'Металл_La', 'Металл_Zn',
       'Металл_Zr', 'Total molecular weight (metal)', 
    'Average ionic radius (metal)', 'Average electronegativity (metal)',
    
    'Молярка_соли','Молярка_кислоты',
    
    'Лиганд_BDC', 'Лиганд_BTB', 'Лиганд_BTC',
    
    'carboxyl_groups (ligand)', 'aromatic_rings (ligand)',
       'carbon_atoms (ligand)', 'oxygen_atoms (ligand)',
       'nitrogen_atoms (ligand)', 'molecular_weight (ligand)',
       'amino_groups (ligand)', 'logP (ligand)', 'TPSA (ligand)',
       'h_bond_acceptors (ligand)', 'h_bond_donors (ligand)',
       
       'Растворитель_ДМФА', 'Растворитель_ДМФА/Этанол/Вода',
       'MolWt', 'LogP', 'NumHDonors',
       'NumHAcceptors',
       
       "m (соли), г",'n_соли'
]


features_Vsyn = [
    'W0, см3/г',  'E0, кДж/моль',  'х0, нм',  'а0, ммоль/г',  'E,  кДж/моль',  'SБЭТ, м2/г', 'Ws, см3/г',  'Sme, м2/г',
    'Wme, см3/г',  'Adsorption_Potential',  'Capacity_Density',  'K_equilibrium',  'Delta_G',  'SurfaceArea_MicroVol_Ratio', 
    'Adsorption_Energy_Ratio',  'S_BET_E',  'x0_W0',  'B_micropore', 
    
    'Металл_Al',  'Металл_Cu',  'Металл_Fe',  'Металл_La',
    'Металл_Zn',  'Металл_Zr',  'Total molecular weight (metal)',  'Average ionic radius (metal)',  'Average electronegativity (metal)',
    
    'Молярка_соли',  'Молярка_кислоты',  'Лиганд_BDC',  'Лиганд_BTB',  'Лиганд_BTC',  'carboxyl_groups (ligand)',  'aromatic_rings (ligand)',
    'carbon_atoms (ligand)',  'oxygen_atoms (ligand)',  'nitrogen_atoms (ligand)',  'molecular_weight (ligand)',  'amino_groups (ligand)',
    'logP (ligand)',  'TPSA (ligand)',  'h_bond_acceptors (ligand)',  'h_bond_donors (ligand)',  'Растворитель_ДМФА',  'Растворитель_ДМФА/Этанол/Вода',
    'MolWt',  'LogP',  'NumHDonors',  'NumHAcceptors',  'm (соли), г',  'n_соли','m(кис-ты), г','n_кислоты'
]

features_Tsyn = [
    'W0, см3/г',  'E0, кДж/моль',  'х0, нм',  'а0, ммоль/г',  'E,  кДж/моль',  'SБЭТ, м2/г', 'Ws, см3/г',  'Sme, м2/г',
    'Wme, см3/г',  'Adsorption_Potential',  'Capacity_Density',  'K_equilibrium',  'Delta_G',  'SurfaceArea_MicroVol_Ratio', 
    'Adsorption_Energy_Ratio',  'S_BET_E',  'x0_W0',  'B_micropore', 
    
    'Металл_Al',  'Металл_Cu',  'Металл_Fe',  'Металл_La',
    'Металл_Zn',  'Металл_Zr',  'Total molecular weight (metal)',  'Average ionic radius (metal)',  'Average electronegativity (metal)',
    
    'Молярка_соли',  'Молярка_кислоты',  'Лиганд_BDC',  'Лиганд_BTB',  'Лиганд_BTC',  'carboxyl_groups (ligand)',  'aromatic_rings (ligand)',
    'carbon_atoms (ligand)',  'oxygen_atoms (ligand)',  'nitrogen_atoms (ligand)',  'molecular_weight (ligand)',  'amino_groups (ligand)',
    'logP (ligand)',  'TPSA (ligand)',  'h_bond_acceptors (ligand)',  'h_bond_donors (ligand)',  'Растворитель_ДМФА',  'Растворитель_ДМФА/Этанол/Вода',
    'MolWt',  'LogP',  'NumHDonors',  'NumHAcceptors',  'm (соли), г',  'n_соли','m(кис-ты), г','n_кислоты','Vсин. (р-ля), мл'
]

features_Tdry = [
    'W0, см3/г',  'E0, кДж/моль',  'х0, нм',  'а0, ммоль/г',  'E,  кДж/моль',  'SБЭТ, м2/г', 'Ws, см3/г',  'Sme, м2/г',
    'Wme, см3/г',  'Adsorption_Potential',  'Capacity_Density',  'K_equilibrium',  'Delta_G',  'SurfaceArea_MicroVol_Ratio', 
    'Adsorption_Energy_Ratio',  'S_BET_E',  'x0_W0',  'B_micropore', 
    
    'Металл_Al',  'Металл_Cu',  'Металл_Fe',  'Металл_La',
    'Металл_Zn',  'Металл_Zr',  'Total molecular weight (metal)',  'Average ionic radius (metal)',  'Average electronegativity (metal)',
    
    'Молярка_соли',  'Молярка_кислоты',  'Лиганд_BDC',  'Лиганд_BTB',  'Лиганд_BTC',  'carboxyl_groups (ligand)',  'aromatic_rings (ligand)',
    'carbon_atoms (ligand)',  'oxygen_atoms (ligand)',  'nitrogen_atoms (ligand)',  'molecular_weight (ligand)',  'amino_groups (ligand)',
    'logP (ligand)',  'TPSA (ligand)',  'h_bond_acceptors (ligand)',  'h_bond_donors (ligand)',  'Растворитель_ДМФА',  'Растворитель_ДМФА/Этанол/Вода',
    'MolWt',  'LogP',  'NumHDonors',  'NumHAcceptors',  'm (соли), г',  'n_соли','m(кис-ты), г','n_кислоты','Vсин. (р-ля), мл','Т.син., °С'
]

features_Treg = [
    'W0, см3/г',  'E0, кДж/моль',  'х0, нм',  'а0, ммоль/г',  'E,  кДж/моль',  'SБЭТ, м2/г', 'Ws, см3/г',  'Sme, м2/г',
    'Wme, см3/г',  'Adsorption_Potential',  'Capacity_Density',  'K_equilibrium',  'Delta_G',  'SurfaceArea_MicroVol_Ratio', 
    'Adsorption_Energy_Ratio',  'S_BET_E',  'x0_W0',  'B_micropore', 
    
    'Металл_Al',  'Металл_Cu',  'Металл_Fe',  'Металл_La',
    'Металл_Zn',  'Металл_Zr',  'Total molecular weight (metal)',  'Average ionic radius (metal)',
    'Average electronegativity (metal)',
    
    'Молярка_соли',  'Молярка_кислоты',  'Лиганд_BDC',  'Лиганд_BTB',  'Лиганд_BTC', 
    'carboxyl_groups (ligand)',  'aromatic_rings (ligand)',
    'carbon_atoms (ligand)',  'oxygen_atoms (ligand)',  'nitrogen_atoms (ligand)', 
    'molecular_weight (ligand)',  'amino_groups (ligand)',
    'logP (ligand)',  'TPSA (ligand)',  'h_bond_acceptors (ligand)',  'h_bond_donors (ligand)', 
    'Растворитель_ДМФА',  'Растворитель_ДМФА/Этанол/Вода',
    'MolWt',  'LogP',  'NumHDonors',  'NumHAcceptors',  'm (соли), г',
    'n_соли','m(кис-ты), г','n_кислоты','Vсин. (р-ля), мл','Т.син., °С','Т суш., °С'
]

metal_columns = [
    "Металл_Al",
    "Металл_Cu",
    "Металл_Fe",
    "Металл_La",
    "Металл_Zn",
    "Металл_Zr",
]

ligand_columns = ["Лиганд_BDC", "Лиганд_BTB", "Лиганд_BTC"]

solvent_columns = ['Растворитель_ДМФА', 'Растворитель_ДМФА/Этанол/Вода']


class MetalClassifier(nn.Module):
    def __init__(
        self, input_dim, embed_dim=32, num_heads=2, num_layers=2, dropout=0.01
    ):
        super(MetalClassifier, self).__init__()
        self.input_dim = input_dim

        # Linear layer to project input features to embedding dimension
        self.embedding = nn.Linear(input_dim, embed_dim)

        # Transformer Encoder Layer with batch_first=True
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=embed_dim,
            dropout=dropout,
            activation="relu",
            batch_first=True,
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer, num_layers=num_layers
        )

        # Fully connected layers
        self.fc1 = nn.Linear(embed_dim, 64)
        self.bn1 = nn.BatchNorm1d(64)
        self.dropout1 = nn.Dropout(dropout)

        self.fc2 = nn.Linear(64, 32)
        self.bn2 = nn.BatchNorm1d(32)
        self.dropout2 = nn.Dropout(dropout)

        self.fc3 = nn.Linear(32, 16)
        self.bn3 = nn.BatchNorm1d(16)
        self.dropout3 = nn.Dropout(dropout)

        self.output = nn.Linear(16, 1)  # Binary classification

    def forward(self, x):
        # x: [batch_size, input_dim]
        x = self.embedding(x)  # [batch_size, embed_dim]

        # Transformer expects input as [batch_size, seq_len, embed_dim] because batch_first=True
        x = x.unsqueeze(1)  # [batch_size, 1, embed_dim]  # Assuming seq_len=1
        x = self.transformer_encoder(x)  # [batch_size, 1, embed_dim]
        x = x.squeeze(1)  # [batch_size, embed_dim]

        # Fully connected layers
        x = F.relu(self.bn1(self.fc1(x)))
        x = self.dropout1(x)

        x = F.relu(self.bn2(self.fc2(x)))
        x = self.dropout2(x)

        x = F.relu(self.bn3(self.fc3(x)))
        x = self.dropout3(x)

        logits = self.output(x)  # [batch_size, 1]
        return logits.squeeze()  # [batch_size]


# --- Major and Minor Classes Classifier ---
class TransformerClassifier(nn.Module):
    def __init__(
        self,
        input_dim,
        num_classes,
        embed_dim=32,
        num_heads=2,
        num_layers=2,
        dropout=0.01,
    ):
        super(TransformerClassifier, self).__init__()
        self.input_dim = input_dim
        self.num_classes = num_classes

        # Linear layer to project input features to embedding dimension
        self.embedding = nn.Linear(input_dim, embed_dim)

        # Transformer Encoder Layer with batch_first=True
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=embed_dim * 2,
            dropout=dropout,
            activation="relu",
            batch_first=True,  # Aligns with input format [batch_size, seq_len, embed_dim]
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer, num_layers=num_layers
        )

        # Fully connected layers
        self.fc1 = nn.Linear(embed_dim, 64)
        self.bn1 = nn.BatchNorm1d(64)
        self.dropout1 = nn.Dropout(dropout)

        self.fc2 = nn.Linear(64, 32)
        self.bn2 = nn.BatchNorm1d(32)
        self.dropout2 = nn.Dropout(dropout)

        self.fc3 = nn.Linear(32, 16)
        self.bn3 = nn.BatchNorm1d(16)
        self.dropout3 = nn.Dropout(dropout)

        self.output = nn.Linear(16, num_classes)  # Multi-class classification

    def forward(self, x):
        # x: [batch_size, input_dim]
        x = self.embedding(x)  # [batch_size, embed_dim]

        # Transformer expects input as [batch_size, seq_len, embed_dim] because batch_first=True
        x = x.unsqueeze(1)  # [batch_size, 1, embed_dim]  # Assuming seq_len=1
        x = self.transformer_encoder(x)  # [batch_size, 1, embed_dim]
        x = x.squeeze(1)  # [batch_size, embed_dim]

        # Fully connected layers
        x = F.relu(self.bn1(self.fc1(x)))
        x = self.dropout1(x)

        x = F.relu(self.bn2(self.fc2(x)))
        x = self.dropout2(x)

        x = F.relu(self.bn3(self.fc3(x)))
        x = self.dropout3(x)

        logits = self.output(x)  # [batch_size, num_classes]
        return logits


class TransformerTsynClassifier(nn.Module):
    def __init__(
        self,
        input_dim,
        num_classes,
        embed_dim=32,
        num_heads=2,
        num_layers=2,
        dropout=0.01,
    ):
        super(TransformerTsynClassifier, self).__init__()
        self.input_dim = input_dim
        self.num_classes = num_classes

        # Linear layer to project input features to embedding dimension
        self.embedding = nn.Linear(input_dim, embed_dim)

        # Transformer Encoder Layer with batch_first=True
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=embed_dim,
            dropout=dropout,
            activation="relu",
            batch_first=True,  # Aligns with input format [batch_size, seq_len, embed_dim]
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer, num_layers=num_layers
        )

         # Fully connected layers
        self.fc1 = nn.Linear(embed_dim, 64)
        self.bn1 = nn.BatchNorm1d(64)
        self.dropout1 = nn.Dropout(dropout)
        
        self.fc2 = nn.Linear(64, 32)
        self.bn2 = nn.BatchNorm1d(32)
        self.dropout2 = nn.Dropout(dropout)
        
        self.fc3 = nn.Linear(32, 16)
        self.bn3 = nn.BatchNorm1d(16)
        self.dropout3 = nn.Dropout(dropout)
        
        self.output = nn.Linear(16, num_classes)  # Output layer for multi-class classification

    def forward(self, x):
        # x: [batch_size, input_dim]
        x = self.embedding(x)  # [batch_size, embed_dim]

        # Transformer expects input as [batch_size, seq_len, embed_dim] because batch_first=True
        x = x.unsqueeze(1)  # [batch_size, 1, embed_dim]  # Assuming seq_len=1
        x = self.transformer_encoder(x)  # [batch_size, 1, embed_dim]
        x = x.squeeze(1)  # [batch_size, embed_dim]

        # Fully connected layers
        x = F.relu(self.bn1(self.fc1(x)))
        x = self.dropout1(x)

        x = F.relu(self.bn2(self.fc2(x)))
        x = self.dropout2(x)

        x = F.relu(self.bn3(self.fc3(x)))
        x = self.dropout3(x)

        logits = self.output(x)  # [batch_size, num_classes]
        return logits
    
    
class TransformerTdryClassifier(nn.Module):
    def __init__(
        self,
        input_dim,
        num_classes,
        embed_dim=32,
        num_heads=2,
        num_layers=2,
        dropout=0.01,
    ):
        super(TransformerTdryClassifier, self).__init__()
        self.input_dim = input_dim
        self.num_classes = num_classes

        # Linear layer to project input features to embedding dimension
        self.embedding = nn.Linear(input_dim, embed_dim)

        # Transformer Encoder Layer with batch_first=True
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=embed_dim,
            dropout=dropout,
            activation="relu",
            batch_first=True,  # Aligns with input format [batch_size, seq_len, embed_dim]
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer, num_layers=num_layers
        )

        # Fully connected layers
        self.fc1 = nn.Linear(embed_dim, 64)
        self.bn1 = nn.BatchNorm1d(64)
        self.dropout1 = nn.Dropout(dropout)
        
        self.fc2 = nn.Linear(64, 32)
        self.bn2 = nn.BatchNorm1d(32)
        self.dropout2 = nn.Dropout(dropout)
        
        self.fc3 = nn.Linear(32, 16)
        self.bn3 = nn.BatchNorm1d(16)
        self.dropout3 = nn.Dropout(dropout)
        
        self.output = nn.Linear(16, num_classes)  # Output layer for multi-class classification

    def forward(self, x):
        # x: [batch_size, input_dim]
        x = self.embedding(x)  # [batch_size, embed_dim]
        
        # Transformer expects input as [sequence_length, batch_size, embed_dim]
        x = x.unsqueeze(0)  # [1, batch_size, embed_dim]
        x = self.transformer_encoder(x)  # [1, batch_size, embed_dim]
        x = x.squeeze(0)  # [batch_size, embed_dim]
        
        # Fully connected layers
        x = F.relu(self.bn1(self.fc1(x)))
        x = self.dropout1(x)
        
        x = F.relu(self.bn2(self.fc2(x)))
        x = self.dropout2(x)
        
        x = F.relu(self.bn3(self.fc3(x)))
        x = self.dropout3(x)
        
        logits = self.output(x)  # [batch_size, num_classes]
        return logits
    

class TransformerTregClassifier(nn.Module):
    def __init__(
        self,
        input_dim,
        num_classes,
        embed_dim=32,
        num_heads=2,
        num_layers=2,
        dropout=0.01,
    ):
        super(TransformerTregClassifier, self).__init__()
        self.input_dim = input_dim
        self.num_classes = num_classes

        # Linear layer to project input features to embedding dimension
        self.embedding = nn.Linear(input_dim, embed_dim)

        # Transformer Encoder Layer with batch_first=True
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=embed_dim,
            dropout=dropout,
            activation="relu",
            batch_first=True,  # Aligns with input format [batch_size, seq_len, embed_dim]
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer, num_layers=num_layers
        )

        # Fully connected layers
        self.fc1 = nn.Linear(embed_dim, 64)
        self.bn1 = nn.BatchNorm1d(64)
        self.dropout1 = nn.Dropout(dropout)
        
        self.fc2 = nn.Linear(64, 32)
        self.bn2 = nn.BatchNorm1d(32)
        self.dropout2 = nn.Dropout(dropout)
        
        self.fc3 = nn.Linear(32, 16)
        self.bn3 = nn.BatchNorm1d(16)
        self.dropout3 = nn.Dropout(dropout)
        
        self.output = nn.Linear(16, num_classes)  # Output layer for multi-class classification

    def forward(self, x):
        # x: [batch_size, input_dim]
        x = self.embedding(x)  # [batch_size, embed_dim]

        # Transformer expects input as [batch_size, seq_len, embed_dim] because batch_first=True
        x = x.unsqueeze(1)  # [batch_size, 1, embed_dim]  # Assuming seq_len=1
        x = self.transformer_encoder(x)  # [batch_size, 1, embed_dim]
        x = x.squeeze(1)  # [batch_size, embed_dim]

        # Fully connected layers
        x = F.relu(self.bn1(self.fc1(x)))
        x = self.dropout1(x)

        x = F.relu(self.bn2(self.fc2(x)))
        x = self.dropout2(x)

        x = F.relu(self.bn3(self.fc3(x)))
        x = self.dropout3(x)

        logits = self.output(x)  # [batch_size, num_classes]
        return logits