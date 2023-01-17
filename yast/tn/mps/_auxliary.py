""" Mps structure and its basic """
from ... import initialize
from ._mps import MpsMpo, YampsError


def load_from_dict(config, in_dict):
    r"""
    Create MPS/MPO from dictionary.

    Parameters
    ----------
    config : module, types.SimpleNamespace, or typing.NamedTuple
        :ref:`YAST configuration <tensor/configuration:yast configuration>`

    nr_phys: int
        number of physical legs: 1 for MPS (default); 2 for MPO;

    in_dict: dict
        dictionary containing serialized MPS/MPO, i.e.,
        a result of :meth:`yamps.MpsMpo.save_to_dict`.

    Returns
    -------
    yamps.MpsMpo
    """
    nr_phys = in_dict['nr_phys']
    N = len(in_dict['A'])
    out_Mps = MpsMpo(N, nr_phys=nr_phys)
    for n in range(out_Mps.N):
        out_Mps.A[n] = initialize.load_from_dict(config=config, d=in_dict['A'][n])
    return out_Mps


def load_from_hdf5(config, file, in_file_path):
    r"""
    Create MPS/MPO from HDF5 file.

    Parameters
    -----------
    config : module, types.SimpleNamespace, or typing.NamedTuple
        :ref:`YAST configuration <tensor/configuration:yast configuration>`

    file: File
        A 'pointer' to a file opened by a user

    Returns
    -------
    yast.MpsMpo
    """
    
    sym_id = file[in_file_path].get('sym/SYM_ID')[()]
    nsym = file[in_file_path].get('sym/NSYM')[()]
    if not sym_id.decode('ascii') == config.sym.SYM_ID or not nsym == config.sym.NSYM:
        raise YampsError("config doesn't match the one for saved data")
    nr_phys = int(file[in_file_path].get('nr_phys')[()])
    N = len(file[in_file_path+'/A'].keys())
    out_Mps = MpsMpo(N, nr_phys=nr_phys)
    for n in range(out_Mps.N):
        out_Mps.A[n] = initialize.load_from_hdf5(config, file, in_file_path+'/A/'+str(n))
    return out_Mps
