"""
Модуль с определениями признаков для моделей.
"""

# Признаки для металлов
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

# Признаки для лигандов
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

# Признаки для растворителей
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

# Признаки для массы соли
features_salt_mass = [
    'W0, см3/г', 'E0, кДж/моль', 'х0, нм', 'а0, ммоль/г', 'E,  кДж/моль',
    'SБЭТ, м2/г', 'Ws, см3/г', 'Sme, м2/г', 'Wme, см3/г', 
    'Adsorption_Potential', 'Capacity_Density', 'K_equilibrium', 'Delta_G', 
    'SurfaceArea_MicroVol_Ratio', 'Adsorption_Energy_Ratio', 'S_BET_E', 'x0_W0', 'B_micropore',
    
    'Металл_Al', 'Металл_Cu', 'Металл_Fe', 'Металл_La', 'Металл_Zn',
    'Металл_Zr', 'Total molecular weight (metal)', 
    'Average ionic radius (metal)', 'Average electronegativity (metal)',
    
    'Молярка_соли', 'Молярка_кислоты',
    
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

# Признаки для массы кислоты
features_acid_mass = [
    'W0, см3/г', 'E0, кДж/моль', 'х0, нм', 'а0, ммоль/г', 'E,  кДж/моль',
    'SБЭТ, м2/г', 'Ws, см3/г', 'Sme, м2/г', 'Wme, см3/г', 
    'Adsorption_Potential', 'Capacity_Density', 'K_equilibrium', 'Delta_G', 
    'SurfaceArea_MicroVol_Ratio', 'Adsorption_Energy_Ratio', 'S_BET_E', 'x0_W0', 'B_micropore',
    
    'Металл_Al', 'Металл_Cu', 'Металл_Fe', 'Металл_La', 'Металл_Zn',
    'Металл_Zr', 'Total molecular weight (metal)', 
    'Average ionic radius (metal)', 'Average electronegativity (metal)',
    
    'Молярка_соли', 'Молярка_кислоты',
    
    'Лиганд_BDC', 'Лиганд_BTB', 'Лиганд_BTC',
    
    'carboxyl_groups (ligand)', 'aromatic_rings (ligand)',
    'carbon_atoms (ligand)', 'oxygen_atoms (ligand)',
    'nitrogen_atoms (ligand)', 'molecular_weight (ligand)',
    'amino_groups (ligand)', 'logP (ligand)', 'TPSA (ligand)',
    'h_bond_acceptors (ligand)', 'h_bond_donors (ligand)',
    
    'Растворитель_ДМФА', 'Растворитель_ДМФА/Этанол/Вода',
    'MolWt', 'LogP', 'NumHDonors',
    'NumHAcceptors',
    
    "m (соли), г", 'n_соли'
]

# Признаки для объема синтеза
features_Vsyn = [
    'W0, см3/г', 'E0, кДж/моль', 'х0, нм', 'а0, ммоль/г', 'E,  кДж/моль',
    'SБЭТ, м2/г', 'Ws, см3/г', 'Sme, м2/г', 'Wme, см3/г', 
    'Adsorption_Potential', 'Capacity_Density', 'K_equilibrium', 'Delta_G', 
    'SurfaceArea_MicroVol_Ratio', 'Adsorption_Energy_Ratio', 'S_BET_E', 'x0_W0', 'B_micropore',
    
    'Металл_Al', 'Металл_Cu', 'Металл_Fe', 'Металл_La',
    'Металл_Zn', 'Металл_Zr', 'Total molecular weight (metal)', 'Average ionic radius (metal)', 'Average electronegativity (metal)',
    
    'Молярка_соли', 'Молярка_кислоты', 'Лиганд_BDC', 'Лиганд_BTB', 'Лиганд_BTC', 'carboxyl_groups (ligand)', 'aromatic_rings (ligand)',
    'carbon_atoms (ligand)', 'oxygen_atoms (ligand)', 'nitrogen_atoms (ligand)', 'molecular_weight (ligand)', 'amino_groups (ligand)',
    'logP (ligand)', 'TPSA (ligand)', 'h_bond_acceptors (ligand)', 'h_bond_donors (ligand)', 'Растворитель_ДМФА', 'Растворитель_ДМФА/Этанол/Вода',
    'MolWt', 'LogP', 'NumHDonors', 'NumHAcceptors', 'm (соли), г', 'n_соли', 'm(кис-ты), г', 'n_кислоты'
]

# Признаки для температуры синтеза
features_Tsyn = [
    'W0, см3/г', 'E0, кДж/моль', 'х0, нм', 'а0, ммоль/г', 'E,  кДж/моль',
    'SБЭТ, м2/г', 'Ws, см3/г', 'Sme, м2/г', 'Wme, см3/г', 
    'Adsorption_Potential', 'Capacity_Density', 'K_equilibrium', 'Delta_G', 
    'SurfaceArea_MicroVol_Ratio', 'Adsorption_Energy_Ratio', 'S_BET_E', 'x0_W0', 'B_micropore',
    
    'Металл_Al', 'Металл_Cu', 'Металл_Fe', 'Металл_La',
    'Металл_Zn', 'Металл_Zr', 'Total molecular weight (metal)', 'Average ionic radius (metal)', 'Average electronegativity (metal)',
    
    'Молярка_соли', 'Молярка_кислоты', 'Лиганд_BDC', 'Лиганд_BTB', 'Лиганд_BTC', 'carboxyl_groups (ligand)', 'aromatic_rings (ligand)',
    'carbon_atoms (ligand)', 'oxygen_atoms (ligand)', 'nitrogen_atoms (ligand)', 'molecular_weight (ligand)', 'amino_groups (ligand)',
    'logP (ligand)', 'TPSA (ligand)', 'h_bond_acceptors (ligand)', 'h_bond_donors (ligand)', 'Растворитель_ДМФА', 'Растворитель_ДМФА/Этанол/Вода',
    'MolWt', 'LogP', 'NumHDonors', 'NumHAcceptors', 'm (соли), г', 'n_соли', 'm(кис-ты), г', 'n_кислоты', 'Vсин. (р-ля), мл'
]

# Признаки для температуры сушки
features_Tdry = [
    'W0, см3/г', 'E0, кДж/моль', 'х0, нм', 'а0, ммоль/г', 'E,  кДж/моль',
    'SБЭТ, м2/г', 'Ws, см3/г', 'Sme, м2/г', 'Wme, см3/г', 
    'Adsorption_Potential', 'Capacity_Density', 'K_equilibrium', 'Delta_G', 
    'SurfaceArea_MicroVol_Ratio', 'Adsorption_Energy_Ratio', 'S_BET_E', 'x0_W0', 'B_micropore',
    
    'Металл_Al', 'Металл_Cu', 'Металл_Fe', 'Металл_La',
    'Металл_Zn', 'Металл_Zr', 'Total molecular weight (metal)', 'Average ionic radius (metal)', 'Average electronegativity (metal)',
    
    'Молярка_соли', 'Молярка_кислоты', 'Лиганд_BDC', 'Лиганд_BTB', 'Лиганд_BTC', 'carboxyl_groups (ligand)', 'aromatic_rings (ligand)',
    'carbon_atoms (ligand)', 'oxygen_atoms (ligand)', 'nitrogen_atoms (ligand)', 'molecular_weight (ligand)', 'amino_groups (ligand)',
    'logP (ligand)', 'TPSA (ligand)', 'h_bond_acceptors (ligand)', 'h_bond_donors (ligand)', 'Растворитель_ДМФА', 'Растворитель_ДМФА/Этанол/Вода',
    'MolWt', 'LogP', 'NumHDonors', 'NumHAcceptors', 'm (соли), г', 'n_соли', 'm(кис-ты), г', 'n_кислоты', 'Vсин. (р-ля), мл', 'Т.син., °С'
]

# Признаки для температуры регенерации
features_Treg = [
    'W0, см3/г', 'E0, кДж/моль', 'х0, нм', 'а0, ммоль/г', 'E,  кДж/моль',
    'SБЭТ, м2/г', 'Ws, см3/г', 'Sme, м2/г', 'Wme, см3/г', 
    'Adsorption_Potential', 'Capacity_Density', 'K_equilibrium', 'Delta_G', 
    'SurfaceArea_MicroVol_Ratio', 'Adsorption_Energy_Ratio', 'S_BET_E', 'x0_W0', 'B_micropore',
    
    'Металл_Al', 'Металл_Cu', 'Металл_Fe', 'Металл_La',
    'Металл_Zn', 'Металл_Zr', 'Total molecular weight (metal)',
    'Average ionic radius (metal)', 'Average electronegativity (metal)',
    
    'Молярка_соли', 'Молярка_кислоты', 'Лиганд_BDC', 'Лиганд_BTB', 'Лиганд_BTC', 
    'carboxyl_groups (ligand)', 'aromatic_rings (ligand)',
    'carbon_atoms (ligand)', 'oxygen_atoms (ligand)', 'nitrogen_atoms (ligand)', 
    'molecular_weight (ligand)', 'amino_groups (ligand)',
    'logP (ligand)', 'TPSA (ligand)', 'h_bond_acceptors (ligand)', 'h_bond_donors (ligand)', 
    'Растворитель_ДМФА', 'Растворитель_ДМФА/Этанол/Вода',
    'MolWt', 'LogP', 'NumHDonors', 'NumHAcceptors', 'm (соли), г',
    'n_соли', 'm(кис-ты), г', 'n_кислоты', 'Vсин. (р-ля), мл', 'Т.син., °С', 'Т суш., °С'
]

# Колонки для one-hot кодирования
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