from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski
import numpy as np

def analyze_ligand(ligand_name):
    """
    Analyzes a ligand and computes various molecular descriptors.

    Parameters:
    - ligand_name (str): The name of the ligand.

    Returns:
    - dict: A dictionary containing molecular descriptors.
    """
    ligand_smiles = {
        'BTC': 'C1(=CC(=CC(=C1)C(=O)[O-])C(=O)[O-])C(=O)[O-]',
        'BDC': 'O=C([O-])C1=CC=C(C=C1)C(=O)[O-]',
        'NH2-BDC': 'NC1=C(C=CC(=C1)C(=O)[O-])C(=O)[O-]',
        'BTB': 'c1cc(ccc1c2cc(cc(c2)c3ccc(cc3)C(=O)[O-])c4ccc(cc4)C(=O)[O-])C(=O)[O-]'
    }

    smiles = ligand_smiles.get(ligand_name)
    if not smiles:
        return f"Ligand {ligand_name} not found in the dictionary."

    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        return "Invalid SMILES string."

    def count_substructures(pattern):
        return len(mol.GetSubstructMatches(pattern))

    # Define SMARTS patterns
    carboxylate_pattern = Chem.MolFromSmarts('C(=O)[O-]')
    carboxylic_acid_pattern = Chem.MolFromSmarts('C(=O)O')
    amino_group_pattern = Chem.MolFromSmarts('N([H])[H]')  # Specifically -NH₂

    # Counting carboxyl groups
    carboxyl_groups = count_substructures(carboxylate_pattern) + count_substructures(carboxylic_acid_pattern)
    
    # Counting aromatic rings using RDKit's ring info
    aromatic_rings = sum(1 for ring in mol.GetRingInfo().AtomRings() 
                         if all(mol.GetAtomWithIdx(idx).GetIsAromatic() for idx in ring))
    
    # Counting amino groups
    amino_groups = count_substructures(amino_group_pattern)

    # Counting atoms
    carbon_atoms = sum(1 for atom in mol.GetAtoms() if atom.GetSymbol() == 'C')
    oxygen_atoms = sum(1 for atom in mol.GetAtoms() if atom.GetSymbol() == 'O')
    nitrogen_atoms = sum(1 for atom in mol.GetAtoms() if atom.GetSymbol() == 'N')

    # Calculating descriptors
    molecular_weight = Descriptors.MolWt(mol)
    logP = Descriptors.MolLogP(mol)
    TPSA = Descriptors.TPSA(mol)
    h_bond_acceptors = Lipinski.NumHAcceptors(mol)
    h_bond_donors = Lipinski.NumHDonors(mol)

    return {
        'carboxyl_groups (ligand)': carboxyl_groups,
        'aromatic_rings (ligand)': aromatic_rings,
        'carbon_atoms (ligand)': carbon_atoms,
        'oxygen_atoms (ligand)': oxygen_atoms,
        'nitrogen_atoms (ligand)': nitrogen_atoms,
        'molecular_weight (ligand)': molecular_weight,
        'amino_groups (ligand)': amino_groups,
        'logP (ligand)': logP,
        'TPSA (ligand)': TPSA,
        'h_bond_acceptors (ligand)': h_bond_acceptors,
        'h_bond_donors (ligand)': h_bond_donors
    }

def safe_generate_features(ligand_type):
    """
    Safely generates molecular descriptors for a given ligand.

    Parameters:
    - ligand_type (str): The name of the ligand.

    Returns:
    - tuple: (dict of molecular descriptors, list of column names)
    """
    # Define the new_columns first
    new_columns = [
        'carboxyl_groups (ligand)', 
        'aromatic_rings (ligand)', 
        'carbon_atoms (ligand)', 
        'oxygen_atoms (ligand)', 
        'nitrogen_atoms (ligand)', 
        'molecular_weight (ligand)', 
        'amino_groups (ligand)', 
        'logP (ligand)', 
        'TPSA (ligand)', 
        'h_bond_acceptors (ligand)', 
        'h_bond_donors (ligand)'
    ]
    
    try:
        result = analyze_ligand(ligand_type)
        if isinstance(result, str):
            return {column: None for column in new_columns}, new_columns
        return result, new_columns
    except Exception as e:
        print(f"Error processing ligand {ligand_type}: {e}")
        return {column: None for column in new_columns}, new_columns

def parse_solvent_mixture(solvent_str):
    """
    Parses a solvent mixture string separated by '/' and retrieves their SMILES strings.

    Parameters:
    - solvent_str (str): The solvent mixture string (e.g., 'Этанол/Вода').

    Returns:
    - list: A list of SMILES strings corresponding to the solvents.
    """
    solvent_smiles_russian = {
        'ДМФА': 'O=CN(C)C',
        'Этанол': 'CCO',
        'Вода': 'O',
        'ДМСО': 'CS(=O)C',
        'Ацетонитрил': 'CC#N'
    }
    
    components = solvent_str.split('/')
    return [solvent_smiles_russian.get(comp.strip()) for comp in components]

def compute_solvent_descriptors(smiles_list):
    """
    Computes molecular descriptors for a list of SMILES strings and aggregates them.

    Parameters:
    - smiles_list (list): A list of SMILES strings.

    Returns:
    - dict or None: A dictionary of aggregated descriptors or None if no valid SMILES.
    """
    descriptors_list = []
    for smiles in smiles_list:
        if not smiles:
            continue  # Skip if SMILES is None
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            descriptors = {
                'MolWt': Descriptors.MolWt(mol),
                'LogP': Descriptors.MolLogP(mol),
                'NumHDonors': Descriptors.NumHDonors(mol),
                'NumHAcceptors': Descriptors.NumHAcceptors(mol)
            }
            descriptors_list.append(descriptors)
        else:
            print(f"Invalid SMILES string encountered: {smiles}")
    
    # Aggregate descriptors (mean)
    if descriptors_list:
        aggregated = {
            key: np.mean([d[key] for d in descriptors_list])
            for key in descriptors_list[0]
        }
        return aggregated
    else:
        return None

def analyze_solvent(solvent_str):
    """
    Analyzes a solvent mixture and computes aggregated molecular descriptors.

    Parameters:
    - solvent_str (str): The solvent mixture string (e.g., 'Этанол/Вода').

    Returns:
    - dict: A dictionary of aggregated molecular descriptors.
    """
    smiles_list = parse_solvent_mixture(solvent_str)
    descriptors = compute_solvent_descriptors(smiles_list)
    if descriptors:
        return descriptors
    else:
        return f"Solvent mixture '{solvent_str}' could not be processed."

def safe_generate_solvent_features(solvent_str):
    """
    Safely generates molecular descriptors for a given solvent mixture.

    Parameters:
    - solvent_str (str): The solvent mixture string.

    Returns:
    - tuple: (dict of molecular descriptors, list of column names)
    """
    # Define the new_columns for solvent descriptors
    solvent_new_columns = [
        'MolWt',
        'LogP',
        'NumHDonors',
        'NumHAcceptors'
    ]

    try:
        result = analyze_solvent(solvent_str)
        if isinstance(result, str):
            # If an error message is returned from analyze_solvent
            return {column: None for column in solvent_new_columns}, solvent_new_columns
        return result, solvent_new_columns
    except Exception as e:
        print(f"Error processing solvent '{solvent_str}': {e}")
        return {column: None for column in solvent_new_columns}, solvent_new_columns