from pynwb import NWBHDF5IO

def readNWBpatchClamp(fpath):

    # read nwb file for the chosen file
    io = NWBHDF5IO(fpath, 'r')
    nwbfile = io.read()

    # current input
    ccss = nwbfile.get_stimulus('ccss')
    current_stimulus = ccss.data[()]

    # current output
    ccs = nwbfile.get_acquisition('ccs')
    current_clamp = ccs.data[()]

    io.close()

    return nwbfile, ccss, ccs

[nwbfile, ccss, ccs] = readNWBpatchClamp(fpath='/Volumes/HD1/White_noise/Human_tissue/Epilepsy cases/nwb files/18220020.nwb')