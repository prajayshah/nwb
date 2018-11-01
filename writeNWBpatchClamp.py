import numpy as np
from neo import io as nio   # note this code is validated for neo-0.5.2
from pynwb import NWBFile, NWBHDF5IO
import pandas as pd
import datetime

# # initialize dataframe for saving the tracking .csv file as you create NWB files
# columns = ['cell_id', 'recording_date', 'exp_condition', 'cell_type', 'gain', 'dc',
#        'firing rate', 'nwb_create_date', 'analysis_date']
#
# df = pd.DataFrame(columns=columns)
# df.to_csv('/Volumes/HD1/White_noise/ResponseVariabilityCells.csv', index=False)

def writeNWBpatchClamp(file_path='', output_path='', experiment_condition='',
                       date='', cell_number='', cell_type='', cell_id='', species='', gain=0.0, dc='not_given',
                       offset=None, protocol='white noise'):

    '''
    This function is designed to save the metadata and experimental data (.abf file) from a patch-clamp
    experiment in the Valiante lab

    :param file_path:       path to the .abf file to be saved as NWB
    :param date:            date of the cell recording
    :param cell_number:     cell number from that day for the patient or animal
    :param cell_type:       description of cell (e.g. L2/3 Hu)
    :param cell_id:         numerical ID of cell
    :param species:         species
    :param gain:            gain of the cell recording data
    :param DC:              DC level at which cell was recorded at
    :param offset:          resting membrane potential offset

    :return:
    '''

    # ----------------------------------------------------------------------------------------------------------------------
    # Load up the abf file into python
    # ----------------------------------------------------------------------------------------------------------------------


    fpath = file_path; f = cell_id

    # Load up abf file
    print('Loading data...')
    h = {}
    si = {}  # sampling intervals for each cell in us
    d = {}
    V = {}
    I = {}

    a = nio.AxonIO(filename=fpath)
    bl = bl = a.read_block(lazy=False, signal_group_mode='split-all', units_group_mode='split-all')
    # - .segments represent sweeps (one segment = one sweep)
    # - .analogsignals for each segment: numpy array of voltage recordings and current input,
    #   length of recording block, and sampling rate
    iclamp = 0  # channel 4 as voltage channel
    current_in = 1  # channel 14 as command channel
    V[f] = []  # numpy array of voltage recordings for all sweeps/segments - rows = sweeps, columns = data
    for i in range(0, len(bl.segments)):
        a = bl.segments[i].analogsignals[iclamp].__array__().tolist()
        V[f].append([item for x in a for item in x])
    V[f] = np.array(V[f])
    I[f] = []  # numpy array of stimulus for all sweeps/segments - rows = sweeps, columns = data
    for i in range(0, len(bl.segments)):
        a = bl.segments[i].analogsignals[current_in].__array__().tolist()
        I[f].append([item for x in a for item in x])
    I[f] = np.array(I[f])

    # save data block for each cell
    d[f] = bl


    # ----------------------------------------------------------------------------------------------------------------------
    # Create the NWB file
    # ----------------------------------------------------------------------------------------------------------------------

    nwbfile = NWBFile(session_description = ('Cell #'+ cell_number),
                      session_start_time = date,
                      source = '',
                      identifier = cell_id,
                      file_create_date = date,
                      experiment_description=(species + ' ' + experiment_condition + ' ' + cell_type),
                      experimenter='HM',
                      lab='Valiante Laboratory',
                      institution='Univ. of Toronto',
                      protocol = protocol,
                      notes = ('RMP Offset: ' + offset)
                      )

    # create a new device
    device = nwbfile.create_device(name='Clampfit', source='N/A')

    # create a new electrode
    elec = nwbfile.create_ic_electrode(
        name="elec0", source='', slice='', resistance='', seal='', description='',
        location='', filtering='', initial_access_resistance='', device=device)


    ## Current clamp stimulus data
    from pynwb.icephys import CurrentClampStimulusSeries

    ccss = CurrentClampStimulusSeries(
        name="ccss", source="command", data=I[f], unit='pA', electrode = elec,
        rate=10e4, gain=gain, starting_time=0.0, description='DC%s' % dc)

    nwbfile.add_stimulus(ccss)

    ## Current Clamp Response data
    from pynwb.icephys import CurrentClampSeries

    ccs = CurrentClampSeries(
        name='ccs', source='command', data=V[f], electrode = elec,
        unit='mV', rate=10e4,
        gain=0.00, starting_time=0.0,
        bias_current=np.nan, bridge_balance=np.nan, capacitance_compensation=np.nan)

    nwbfile.add_acquisition(ccs)

    # after adding all data,
    # write data to NWBFile

    io = NWBHDF5IO(output_path+'%s.nwb' % f, 'w')
    io.write(nwbfile)
    io.close()

    df = pd.read_csv('/Volumes/HD1/White_noise/ResponseVariabilityCells.csv')

    df_append = df.append({'cell_id': cell_id,
                           'recording_date': date,
                           'exp_condition': experiment_condition,
                           'cell_type': cell_type,
                           'gain': gain,
                           'dc': dc,
                           'nwb_create_date': datetime.datetime.now().strftime("%I:%M%p %B %d, %Y")
                           }, ignore_index=True)

    df_append.to_csv('/Volumes/HD1/White_noise/ResponseVariabilityCells.csv', index=False)



## WRITE NWB files

# # error
# # writeNWBpatchClamp(file_path="/Users/prajayshah/OneDrive - University of Toronto/UTPhD/White noise/Human tissue/March 29, 2018/Cell 2/Gain 20/18329010.abf",
# #                    output_path="/Users/prajayshah/OneDrive - University of Toronto/UTPhD/White noise/Human tissue/March 29, 2018/",
# #                    date='Mar 29, 2018', cell_number='2', cell_type='Hu L2/3', cell_id='18329010', species='Human',
# #                    experiment_condition='Epilepsy',
# #                    gain=20., dc='25', offset='-15')
#
# # error
# writeNWBpatchClamp(file_path="/Users/prajayshah/OneDrive - University of Toronto/UTPhD/White noise/Human tissue/March 29, 2018/Cell 2/Gain 40/18329011.abf",
#                    output_path="/Users/prajayshah/OneDrive - University of Toronto/UTPhD/White noise/Human tissue/March 29, 2018/",
#                    date='Mar 29, 2018', cell_number='2', cell_type='Hu L2/3', cell_id='18329011', species='Human',
#                    experiment_condition='Epilepsy',
#                    gain=40., dc='25', offset='-15')

# # error
# writeNWBpatchClamp(file_path="/Users/prajayshah/OneDrive - University of Toronto/UTPhD/White noise/Human tissue/March 29, 2018/Cell 3/Gain 20/18329015.abf",
#                    output_path="/Users/prajayshah/OneDrive - University of Toronto/UTPhD/White noise/Human tissue/March 29, 2018/",
#                    date='Mar 29, 2018', cell_number='3', cell_type='Hu L2/3', cell_id='18329015', species='Human',
#                    experiment_condition='Epilepsy',
#                    gain=20., dc='25', offset='-15')


# # error
# writeNWBpatchClamp(file_path="/Users/prajayshah/OneDrive - University of Toronto/UTPhD/White noise/Human tissue/March 29, 2018/Cell 9.2/Gain 20/18329048.abf",
#                    output_path="/Users/prajayshah/OneDrive - University of Toronto/UTPhD/White noise/Human tissue/March 29, 2018/",
#                    date='Mar 29, 2018', cell_number='9.2', cell_type='Hu L2/3', cell_id='18329048', species='Human',
#                    experiment_condition='Epilepsy',
#                    gain=20., dc='100', offset='-19')

# writeNWBpatchClamp(file_path="/Volumes/HD1/White_noise/Human_tissue/Epilepsy cases/Feb 20, 2018/Cell 4/Gain 20/18220020.abf",
#                    output_path="/Volumes/HD1/White_noise/Human_tissue/Epilepsy cases/nwb files/",
#                    date='Feb 20, 2018', cell_number='4', cell_type='Hu L2/3', cell_id='18220020', species='Human',
#                    experiment_condition='Epilepsy',
#                    gain=20., dc='100', offset='-17.5')

writeNWBpatchClamp(file_path="/Volumes/HD1/White_noise/Human_tissue/Tumor cases/October 22, 2018/Cell 3/Gain 40/18o22025.abf",
                   output_path="/Volumes/HD1/White_noise/Human_tissue/Tumor cases/nwb files/",
                   date='Oct 22, 2018', cell_number='3', cell_type='Hu L2/3', cell_id='18o22025', species='Human',
                   experiment_condition='Tumor',
                   gain=40., dc='125', offset='-20')

