import pandas as pd

# process a CSV into a smiles file and a feature file for training
# with TransVAE

FEATURE = 'xtb_lumo'
TRAIN_CSV = 'zinc_train_red.csv'
TEST_CSV = 'zinc_test.csv'
METHOD = 'z_std'

def process_for_training(feature, train_csv, test_csv, method=''):
    df_train = pd.read_csv(train_csv)
    df_test = pd.read_csv(test_csv)

    # Scale to standard normal
    if method == 'z_std':
        feat_mean = df_train[feature].mean()
        feat_std = df_train[feature].std()
        print(f'mean {feature} of training : {feat_mean}')
        print(f'std {feature} of training : {feat_std}')
        df_train[feature] = (df_train[feature]-feat_mean)/(feat_std)
        df_test[feature] = (df_test[feature]-feat_mean)/(feat_std)
        
    # scale to between 0 and 1
    elif method == 'min_max':
        feat_max = df_train[feature].max()
        feat_min = df_train[feature].min()
        print(f'max {feature} of training : {feat_max}')
        print(f'min {feature} of training : {feat_min}')
        df_train[feature] = (df_train[feature]-feat_min)/(feat_max - feat_min)
        df_test[feature] = (df_test[feature]-feat_min)/(feat_max - feat_min)
    
    # raw data if nothing given
    else:
        pass

    df_train.to_csv(f'zinc_train_red.txt', index=False, columns=['smile'])
    df_train.to_csv(f'zinc_train_red_{feature}_{method}.txt', index=False, columns=[feature])

    df_test.to_csv(f'zinc_test.txt', index=False, columns=['smile'])
    df_test.to_csv(f'zinc_test_{feature}_{method}.txt', index=False, columns=[feature])

if __name__ == '__main__':
    process_for_training(FEATURE, TRAIN_CSV, TEST_CSV, METHOD) 
