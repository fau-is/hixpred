import pandas as pd
import src.util as util
import numpy as np


def get_sepsis_data(target_activity, max_len, min_len):
    """
    Creates sequences from the sepsis dataset
    :param target_activity:
    :param max_len: Numerical value. Determines the maximal length of the retruned lists
    :param min_len: Numerical value. Determines the minimal length of the retruned lists
    :return: Six lists.
        x_seqs_ : One-Hot coded Sequence List
        x_statics_ : List of arrays (?)
        y_ : Numerical List. Each entry is either 0 or 1. 0 if target_activity is not in sequence, 1 if target_activity is in sequence
        x_time_vals_ : List of Lists containing Timestemps (?)
        seq_features : List of strings storing sequence features
        static_features : List of strings storing static features
    """
    ds_path = '../data/Sepsis Cases - Event Log.csv'

    static_features = ['InfectionSuspected', 'DiagnosticBlood', 'DisfuncOrg',
                       'SIRSCritTachypnea', 'Hypotensie',
                       'SIRSCritHeartRate', 'Infusion', 'DiagnosticArtAstrup', 'Age',
                       'DiagnosticIC', 'DiagnosticSputum', 'DiagnosticLiquor',
                       'DiagnosticOther', 'SIRSCriteria2OrMore', 'DiagnosticXthorax',
                       'SIRSCritTemperature', 'DiagnosticUrinaryCulture', 'SIRSCritLeucos',
                       'Oligurie', 'DiagnosticLacticAcid', 'Hypoxie',
                       'DiagnosticUrinarySediment', 'DiagnosticECG']

    seq_features = ['Leucocytes', 'CRP', 'LacticAcid', 'ER Registration', 'ER Triage', 'ER Sepsis Triage',
                    'IV Liquid', 'IV Antibiotics', 'Admission NC', 'Admission IC',
                    'Return ER', 'Release A', 'Release B', 'Release C', 'Release D',
                    'Release E']

    int2act = dict(zip(range(len(seq_features)), seq_features))

    df = pd.read_csv(ds_path)
    df['Complete Timestamp'] = pd.to_datetime(df['Complete Timestamp'])

    # Sort case id by timestamp of first event
    df_ = df.groupby('Case ID').first()
    df_ = df_.sort_values(by='Complete Timestamp')
    x = pd.CategoricalDtype(df_.index.values, ordered=True)
    df['Case ID'] = df['Case ID'].astype(x)
    df = df.sort_values(['Case ID', 'Complete Timestamp'])
    df = df.reset_index()

    df['Age'] = df['Age'].fillna(-1)
    df['Age'] = df['Age'].apply(lambda x: x / max(df['Age']))

    max_leucocytes = np.percentile(df['Leucocytes'].dropna(), 95)  # remove outliers
    max_lacticacid = np.percentile(df['LacticAcid'].dropna(), 95)  # remove outliers

    x_seqs = []
    x_statics = []
    x_time_vals = []
    y = []

    for case in df['Case ID'].unique():

        after_registration_flag = False
        found_target_flag = False

        df_tmp = df[df['Case ID'] == case]
        df_tmp = df_tmp.sort_values(by='Complete Timestamp')

        idx = -1
        for _, x in df_tmp.iterrows():
            idx = idx + 1
            if x['Activity'] == 'ER Registration' and idx == 0:
                x_statics.append(x[static_features].values.astype(float))
                x_time_vals.append([])
                x_seqs.append([])
                after_registration_flag = True

            if x['Activity'] == target_activity and after_registration_flag:
                found_target_flag = True

            if after_registration_flag:
                if not found_target_flag:  # important for data leakage
                    x_seqs[-1].append(util.get_one_hot_of_activity_sepsis(x, max_leucocytes, max_lacticacid))
                    x_time_vals[-1].append(x['Complete Timestamp'])

        if after_registration_flag:
            if found_target_flag:
                y.append(1)
            else:
                y.append(0)

    assert len(x_seqs) == len(x_statics) == len(y) == len(x_time_vals)

    x_seqs_, x_statics_, y_, x_time_vals_ = [], [], [], []
    for i, x in enumerate(x_seqs):
        if min_len <= len(x) <= max_len:
            x_seqs_.append(x)
            x_statics_.append(x_statics[i])
            y_.append(y[i])
            x_time_vals_.append(x_time_vals[i])

    """
    # Create event log
    f = open(f'../output/sepsis.txt', "w+")
    f.write(f'Case ID, Activity, Timestamp,{",".join([x for x in static_features])} \n')
    for idx in range(0, len(x_seqs_)):
        for idx_ts in range(0, len(x_seqs_[idx])):
            f.write(f'{idx},{int2act[np.argmax(x_seqs_[idx][idx_ts])]},'
                    f'{x_time_vals_[idx][idx_ts]},{",".join([str(x) for x in x_statics_[idx]])}\n')
    f.close()
    """

    return x_seqs_, x_statics_, y_, x_time_vals_, seq_features, static_features