import shutil

import pandas as pd
import glob

# Recombine the split xyz and csv files into one

XYZ_FILES = sorted(glob.glob("zinc_train*.xyz"))
CSV_FILES = [f'{file[:-3]}csv' for file in XYZ_FILES]
TXT_FILES = [f'{file[:-3]}txt' for file in XYZ_FILES]


def combine_csvs(csv_files, txt_files, output_csv):
    with open(output_csv, 'a') as final_csv:
        is_first = True
        for csv, txt in zip(csv_files, txt_files):
            with open(txt, 'r') as smiles_file:
                smiles = [line.strip() for line in smiles_file]
            df = pd.read_csv(csv)
            df.insert(0, 'smile', smiles)

            df.to_csv(final_csv, header=is_first, index=False)
            is_first = False
            print(f'completed {csv}')


def combine_xyzs(xyz_files, output_xyz):
    with open(output_xyz, 'ab') as final_xyz:
        for xyz_file in xyz_files:
            with open(xyz_file, 'rb') as xyz:
                shutil.copyfileobj(xyz, final_xyz)
                # add new line to separate these two
                final_xyz.write(b'\n')
            print(f'completed {xyz_file}')


combine_csvs(CSV_FILES, TXT_FILES, 'zinc_train.csv')
combine_xyzs(XYZ_FILES, 'zinc_train.xyz')
