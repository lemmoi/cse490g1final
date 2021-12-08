# obabel can't process multiple smiles in parallel, so split the data
# and launch a process for each split

# STEP 1: split the training file into smaller files, each with 80000 smiles
split -l 80000 -d zinc_train.txt zinc_train --additional-suffix=.smi

# STEP 2: For each smiles file, convert to xyz using GAFF
for i in *.smi; do
    root=${i%.*}
    obabel -ismi "$i" -oxyz -O "${root}.xyz" --ff GAFF --gen3d &
done