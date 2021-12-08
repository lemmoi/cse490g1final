import numpy as np
import morfeus
import warnings
import csv
import sys

# USAGE: Call from command line with `xyz_to_morf.py <PATH/TO/XYZ/FILE.xyz>`
# Creates a corresponding CSV file with calculated features
# Adjust the `process_single` function to change the features generated.


def read_xyz_frame(ifile):
    """Reads a single frame from XYZ file.

    Parameters
    ----------
    ifile
        opened file ready for reading, positioned at the num atoms line
    Returns
    -------
    atoms
        list of atom names
    xyz
        Coordinates of the frame
    eof
        true if end of file has been reached.
    """
    n_atoms = ifile.readline()
    if n_atoms:
        n_atoms = int(n_atoms)
    else:
        xyz = None
        eof = True
        return None, xyz, eof

    atoms = []
    xyz = np.zeros((n_atoms, 3))
    # skip comment line
    next(ifile)
    for i in range(n_atoms):
        line = ifile.readline().split()
        atoms.append(line[0])
        xyz[i] = [float(x) for x in line[1:4]]
    eof = False
    return atoms, xyz, eof

def read_xyz_file(filename: str) -> np.ndarray:
    """Reads xyz files into an atom list and xyz array

    Parameters
    ----------
    filename
        path to xyz file

    Returns
    -------
    list of pairs of
       - a list of atoms
       - a np array of coordinates
    """
    with open(filename, 'r') as file:
        atoms, _xyz, eof = read_xyz_frame(file)
        if eof:
            raise ValueError("File at '{}' is empty.".format(filename))
        else:
            pass
        # initially store each set of xyz coords in a list
        # and then join them all together at the end
        result_list = [(atoms, _xyz)]
        eof = False
        while not eof:
            atoms, _xyz, eof = read_xyz_frame(file)
            if not eof:
                result_list.append((atoms, _xyz))

    return result_list

# Not used, maybe keep around for later
def read_xyz_generator(filename: str) -> np.ndarray:
    """Reads xyz files into an atom list and xyz array as a generator

    Parameters
    ----------
    filename
        path to xyz file

    Returns
    -------
    list of pairs of
       - a list of atoms
       - a np array of coordinates
    """
    with open(filename, 'r') as file:
        atoms, _xyz, eof = read_xyz_frame(file)
        if eof:
            raise ValueError("File at '{}' is empty.".format(filename))
        else:
            pass
        # initially store each set of xyz coords in a list
        # and then join them all together at the end
        yield (atoms, _xyz)
        eof = False
        while not eof:
            atoms, _xyz, eof = read_xyz_frame(file)
            if not eof:
                yield atoms, _xyz
                
def process_single(tup):
    '''
    Process a single (atoms, coordinate) pair with morfeus
    
    tup is a tuple of (elements [iter[str]], coordinates [2darray]) 

    Returns a dictionary of {feature: value}
    '''
    atoms, coords = tup
    result = {}
    
    # XTB whole molecule calculations
    xtb = morfeus.XTB(atoms, coords, version='2')
    result['xtb_homo'] = xtb.get_homo()
    result['xtb_lumo'] = xtb.get_lumo()
    dipole = xtb.get_dipole()
    for i, dim in enumerate(('x', 'y', 'z')):
        result[f'xtb_dipole_{dim}'] = dipole[i]
    
    # corrected and non-corrected
    keys = ['ea', 'ip']
    funcs = [xtb.get_ea, xtb.get_ip]
    for key, func in zip(keys, funcs):
        result[f'xtb_{key}'] = func()
        result[f'xtb_{key}_corrected'] = func(corrected=True)
    
    descriptors = ['electrophilicity', 'nucleophilicity', 'electrofugality', 'nucleofugality']
    for desc in descriptors:
        result[f'xtb_global_{desc}'] = xtb.get_global_descriptor(desc)
        result[f'xtb_global_{desc}_corrected'] = xtb.get_global_descriptor(desc, corrected=True)
    
    # dispersion with D4 model
    # morfeus is not using the latest dftd4 (v3+).
    # dftd4 v2.5.0 can be installed from conda, but the python interface must be installed from
    # git with `pip install 'git+https://github.com/dftd4/dftd4@v2.5.0#egg=dftd4&subdirectory=python'`
    # both the conda and above pip command need to be run

    # warnings about old ASE func
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        disp = morfeus.Dispersion(atoms, coords, compute_coefficients=False)
        disp.compute_coefficients(model="gd4")
        disp.compute_p_int()
        result['d4_disp_area'] = disp.area
        result['d4_disp_vol'] = disp.volume
        result['d4_disp_pint'] = disp.p_int
    
    # solvent accessible surface area
    sasa = morfeus.SASA(atoms, coords)
    result['sasa_area'] = sasa.area
    result['sasa_volume'] = sasa.volume
    
    return result
    
    
def main():
    # First argument on command line is the xyz file to process,
    # a corresponding csv file is created
    xyz_name = sys.argv[1]
    csv_name = f'{xyz_name[:-3]}csv'
    xyzs = read_xyz_file(xyz_name)
    first = process_single(xyzs[0])
    with open(csv_name, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=first.keys())
        writer.writeheader()
        writer.writerow(first)
        
        for i, tup in enumerate(xyzs[1:]):
            writer.writerow(process_single(tup))
            # Force file write every 50, since the calculations
            # are the slow part 
            if i % 50 == 0:
                csvfile.flush()
            
if __name__ == '__main__':
    main()
