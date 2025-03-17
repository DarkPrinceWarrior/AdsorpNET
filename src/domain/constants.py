"""
Константы предметной области для проекта AdsorpNET.
"""

# Молярные массы металлов
METAL_MOLAR_MASSES = {
    'Cu': 242, 
    'Zn': 297,
    'Al': 375,
    'Fe': 404,
    'Zr': 233,
    'Mg': 256,
    'La': 433,
    'Ce': 434,
    'Y': 383
}

# Молярные массы лигандов
LIGAND_MOLAR_MASSES = {
    'BTC': 207,
    'BDC': 164,
    'NH2-BDC': 179,
    'BTB': 435
}

# Ионные радиусы металлов (Å)
METAL_IONIC_RADIUS = {
    'Cu': 0.73,
    'Zn': 0.74,
    'Al': 0.53,
    'Fe': 0.65,
    'Zr': 0.72,
    'Mg': 0.72,
    'La': 1.06,
    'Ce': 1.01,
    'Y': 0.90
}

# Электроотрицательность металлов
METAL_ELECTRONEGATIVITY = {
    'Cu': 1.90,
    'Zn': 1.65,
    'Al': 1.61,
    'Fe': 1.83,
    'Zr': 1.33,
    'Mg': 1.31,
    'La': 1.10,
    'Ce': 1.12,
    'Y': 1.22
}

# SMILES структуры лигандов
LIGAND_SMILES = {
    'BTC': 'C1(=CC(=CC(=C1)C(=O)[O-])C(=O)[O-])C(=O)[O-]',
    'BDC': 'O=C([O-])C1=CC=C(C=C1)C(=O)[O-]',
    'NH2-BDC': 'NC1=C(C=CC(=C1)C(=O)[O-])C(=O)[O-]',
    'BTB': 'c1cc(ccc1c2cc(cc(c2)c3ccc(cc3)C(=O)[O-])c4ccc(cc4)C(=O)[O-])C(=O)[O-]'
}

# SMILES структуры растворителей
SOLVENT_SMILES = {
    'ДМФА': 'O=CN(C)C',
    'Этанол': 'CCO',
    'Вода': 'O',
    'ДМСО': 'CS(=O)C',
    'Ацетонитрил': 'CC#N'
}