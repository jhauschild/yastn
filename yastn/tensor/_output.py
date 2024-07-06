# Copyright 2024 The YASTN Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
""" Methods outputing data from yastn.Tensor. """
from __future__ import annotations
import numpy as np
from functools import reduce
from operator import mul
from ._auxliary import _clear_axes, _unpack_axes, _struct, _slc, _flatten
from ._tests import YastnError, _test_configs_match
from ..sym import sym_none
from ._legs import Leg, leg_union, _leg_fusions_need_mask
from ._merging import _embed_tensor


__all__ = ['compress_to_1d', 'save_to_dict', 'save_to_hdf5', 'requires_grad']


def save_to_dict(a) -> dict:
    r"""
    Export YASTN tensor to dictionary containing all the information needed to recreate the tensor.

    Allows saving the tensor, e.g., with numpy.save()

    Complementary function is :meth:`yastn.load_from_dict`

    Parameters
    ----------
    a: yastn.Tensor
        tensor to export
    """
    _d = a.config.backend.to_numpy(a._data)
    hfs = [hf._asdict() for hf in a.hfs]
    return {'_d': _d, 's': a.struct.s, 'n': a.struct.n,
            't': a.struct.t, 'D': a.struct.D, 'isdiag': a.isdiag,
            'mfs': a.mfs, 'hfs': hfs,
            'SYM_ID': a.config.sym.SYM_ID, 'fermionic': a.config.fermionic}


def save_to_hdf5(a, file, path) -> Never:
    """
    Export tensor into hdf5 type file.

    Complementary function is :meth:`yastn.load_from_hdf5`

    Parameters
    ----------
    a : yastn.Tensor
        tensor to export
    """
    _d = a.config.backend.to_numpy(a._data)
    hfs = tuple(tuple(hf) for hf in a.hfs)
    file.create_dataset(path+'/isdiag', data=[int(a.isdiag)])
    file.create_group(path+'/mfs/'+str(a.mfs))
    file.create_group(path+'/hfs/'+str(hfs))
    file.create_dataset(path+'/n', data=a.struct.n)
    file.create_dataset(path+'/s', data=a.struct.s)
    file.create_dataset(path+'/ts', data=a.struct.t)
    file.create_dataset(path+'/Ds', data=a.struct.D)
    file.create_dataset(path+'/matrix', data=_d)


def compress_to_1d(a, meta=None) -> tuple[numpy.array | torch.tensor, dict]:
    """
    Return 1D array containing tensor data (without cloning the data if not necessary) and
    create metadata allowing re-creation of the original tensor.

    Parameters
    ----------
        a: yastn.Tensor
            tensor to export
        meta: dict
            There is an option to provide meta obtained from earlier application of :meth:`yastn.Tensor.compress_to_1d`.
            Extra zero blocks (missing in tensor) are then included in the returned 1D array
            to make it consistent with structure given in meta.
            Raises error if tensor has some blocks which are not included in meta or otherwise
            meta does not match the tensor.

    .. note::
        :meth:`yastn.Tensor.compress_to_1d` and :meth:`yastn.decompress_from_1d`
        provide mechanism that allows using external matrix-free methods, such as eigs implemented in scipy.

    Returns
    -------
    tensor (type derived from backend)
        1D array with tensor data
    dict
        metadata with structure of the symmetric tensor
    """
    if meta is None:
        meta = {'config': a.config, 'struct': a.struct, 'slices': a.slices,
                'mfs': a.mfs, 'legs': a.get_legs(native=True)}
        return a._data, meta
    # else:
    _test_configs_match(a.config, meta['config'])
    if a.struct.s != meta['struct'].s:
        raise YastnError("Tensor signature do not match meta.")
    if a.struct.n != meta['struct'].n:
        raise YastnError("Tensor charge than do not match meta.")
    if a.isdiag != meta['struct'].diag:
        raise YastnError("Tensor diagonality do not match meta.")
    if a.mfs != meta['mfs']:
        raise YastnError("Tensor meta-fusion structure do not match meta.")

    meta_hfs =  tuple(leg.legs[0] for leg in meta['legs'])
    if a.hfs != meta_hfs:
        legs_a = a.get_legs()
        legs_u = {n: leg_union(leg_a, leg) for n, (leg_a, leg) in enumerate(zip(legs_a, meta['legs']))}
        a = _embed_tensor(a, legs_a, legs_u)  # mask needed
        if a.hfs != meta_hfs:
            raise YastnError("Tensor fused legs do not match metadata.")

    if a.struct == meta['struct'] and a.slices == meta['slices']:
        return a._data, meta
    # else: embed filling in missing zero blocks # TODO ?
    ia, im, meta_merge = 0, 0, []
    while ia < len(a.struct.t):
        if a.struct.t[ia] < meta['struct'].t[im] or im >= len(meta['struct'].t):
            raise YastnError("Tensor has blocks that do not appear in meta.")
        if a.struct.t[ia] == meta['struct'].t[im]:
            meta_merge.append((meta['slices'][im].slcs[0], a.slices[ia].slcs[0]))
            ia += 1
            im += 1
        else: #a.struct.t[ia] > meta['struct'].t[im]:
            im += 1
    data = a.config.backend.embed_slc(a._data, meta_merge, meta['struct'].size)
    return data, meta


############################
#    output information    #
############################


def show_properties(a) -> Never:
    """
    Print basic properties of the tensor:
        * it's symmetry
        * signature
        * total charge
        * whether it is a diagonal tensor
        * meta/logical rank - treating meta-fused legs as a single logical leg
        * native rank
        * total dimension of all existing charge sectors for each leg, treating meta-fused legs as a single leg
        * total dimension of all existing charge sectors for native leg
        * number of non-empty blocks
        * total number of elements across all non-empty blocks
        * fusion tree for each leg
        * fusion history with 'o' indicating original legs, 'm' meta-fusion,
          'p' hard-fusion (product), 's' blocking (sum).
    """
    print("Symmetry     :", a.config.sym.SYM_ID)
    print("signature    :", a.struct.s)  # signature
    print("charge       :", a.struct.n)  # total charge of tensor
    print("isdiag       :", a.isdiag)
    print("dim meta     :", a.ndim)  # number of meta legs
    print("dim native   :", a.ndim_n)  # number of native legs
    print("shape meta   :", a.get_shape(native=False))
    print("shape native :", a.get_shape(native=True))
    print("no. blocks   :", len(a.struct.t))  # number of blocks
    print("size         :", a.struct.size)  # total number of elements in all blocks
    st = {i: leg.history() for i, leg in enumerate(a.get_legs())}
    print("legs fusions :", st, "\n")


def __str__(a) -> str:
    legs = a.get_legs()
    ts = tuple(leg.t for leg in legs)
    Ds = tuple(leg.D for leg in legs)
    s = f"{a.config.sym.SYM_ID} s= {a.struct.s} n= {a.struct.n}\n"
    s += f"leg charges  : {ts}\n"
    s += f"dimensions   : {Ds}"
    return s


def requires_grad(a) -> bool:
    """
    Return ``True`` if tensor data have autograd enabled
    """
    return a.config.backend.requires_grad(a._data)


def print_blocks_shape(a) -> str:
    """
    Print shapes of blocks as a sequence of block's charge followed by its shape
    """
    for t, D in zip(a.struct.t, a.struct.D):
        print(f"{t} {D}")


def is_complex(a) -> bool:
    """
    Return ``True`` if tensor data are complex
    """
    return a.config.backend.is_complex(a._data)


def get_tensor_charge(a) -> Sequence[int]:
    """
    Return :attr:`yastn.Tensor.n`
    """
    return a.struct.n


def get_signature(a, native=False) -> Sequence[int]:
    """
    Return tensor signature, equivalent to :attr:`yastn.Tensor.s`.

    If native, returns the signature of tensors's native legs, see :attr:`yastn.Tensor.s_n`.
    """
    return a.s_n if native else a.s


def get_rank(a, native=False) -> int:
    """
    Return tensor rank equivalent to :attr:`yastn.Tensor.ndim`.

    If native, the native rank of the tensor is returned, see :attr:`yastn.Tensor.ndim_n`.
    """
    return a.ndim_n if native else a.ndim


def get_blocks_charge(a) -> Sequence[Sequence[int]]:
    """
    Return charges of all native blocks.

    In case of product of abelian symmetries, for each block the individual symmetry charges are flattened into a single tuple.
    """
    return a.struct.t


def get_blocks_shape(a) -> Sequence[Sequence[int]]:
    """
    Shapes of all native blocks.
    """
    return a.struct.D


def get_shape(a, axes=None, native=False) ->  int | Sequence[int]:
    r"""
    Return effective bond dimensions as sum of dimensions along sectors for each leg.

    Parameters
    ----------
    axes : int | Sequence[int]
        indices of legs; If axes is ``None`` returns for all legs (default).s
    """
    if axes is None:
        axes = tuple(n for n in range(a.ndim_n if native else a.ndim))
    if isinstance(axes, int):
        return sum(a.get_legs(axes, native=native).D)
    return tuple(sum(leg.D) for leg in a.get_legs(axes, native=native))


def get_dtype(a) -> numpy.dtype | torch.dtype:
    """
    dtype of tensor data used by the backend.
    """
    return a.config.backend.get_dtype(a._data)


def __getitem__(a, key) -> numpy.ndarray | torch.tensor:
    """
    Block corresponding to a given charge combination.

    The type of the returned tensor depends on the backend,
    for example :class:`numpy.ndarray` or :class:`torch.Tensor`.
    In case of diagonal tensor, returns 1D array.

    Parameters
    ----------
    key : Sequence[int] | Sequence[Sequence[int]]
        charges of the block.
    """
    key = tuple(_flatten(key))
    try:
        ind = a.struct.t.index(key)
    except ValueError as exc:
        raise YastnError('tensor does not have block specify by key') from exc
    x = a._data[slice(*a.slices[ind].slcs[0])]

    # TODO this should be reshape called from backend ?
    return x if a.isdiag else x.reshape(a.struct.D[ind])

def __contains__(a, key) -> bool:
    key = tuple(_flatten(key)) if (hasattr(key,'__iter__') or hasattr(key,'__next__')) else (key,)
    if a.isdiag:
        return key in a.struct.t or (key+key) in a.struct.t
    return key in a.struct.t

##################################################
#    output tensors info - advanced structure    #
##################################################

def get_leg_fusion(a, axes=None):  # pragma: no cover
    """
    .. deprecated::
        to inspect Legs of the tensor, use :meth:`yastn.Tensor.get_legs`.

    Fusion trees for meta legs.

    Parameters
    ----------
    axes : Int or tuple of ints
        indices of legs; If axes is None returns all (default).
    """
    if axes is None:
        return {'meta': a.mfs, 'hard': a.hfs}
    if isinstance(axes, int):
        return a.mfs(axes)
    return {'meta': tuple(a.mfs(n) for n in axes), 'hard': tuple(a.hfs(n) for n in axes)}


def get_legs(a, axes=None, native=False) -> yastn.Leg | Sequence[yastn.Leg]:
    r"""
    Return a leg or a set of legs of a Tensor.

    Parameters
    ----------
    axes : int | Sequence[int] | None
        indices of legs to retrieve. If ``None`` return list with all legs.

    native : bool
        consider native legs if ``True``; otherwise returns fused legs (default).
    """
    legs = []
    tset = np.array(a.struct.t, dtype=np.int64).reshape((len(a.struct.t), len(a.struct.s), len(a.struct.n)))
    Dset = np.array(a.struct.D, dtype=np.int64).reshape((len(a.struct.D), len(a.struct.s)))
    if axes is None:
        axes = tuple(range(a.ndim)) if not native else tuple(range(a.ndim_n))
    multiple_legs = hasattr(axes, '__iter__')
    axes, = _clear_axes(axes)
    for ax in axes:
        legs_ax = []
        if not native:
            mf = a.mfs[ax]
            nax, = _unpack_axes(a.mfs, (ax,))
        else:
            nax = (ax,)
        for i in nax:
            tseta = tset[:, i, :].reshape(len(tset), a.config.sym.NSYM).tolist()
            Dseta = Dset[:, i].ravel().tolist()
            tDn = {tuple(tn): Dn for tn, Dn in zip(tseta, Dseta)}
            tDn = dict(sorted(tDn.items()))
            t, D = tuple(tDn.keys()), tuple(tDn.values())
            legs_ax.append(Leg(a.config, s=a.struct.s[i], t=t, D=D, legs=(a.hfs[i],)))
        if not native and mf[0] > 1:
            tseta = tset[:, nax, :].reshape(len(tset), len(nax) * a.config.sym.NSYM).tolist()
            Dseta = np.prod(Dset[:, nax], axis=1, dtype=np.int64).ravel().tolist()
            tDn = {tuple(tn): Dn for tn, Dn in zip(tseta, Dseta)}
            tDn = dict(sorted(tDn.items()))
            t, D = tuple(tDn.keys()), tuple(tDn.values())
            legs.append(Leg(a.config.sym, s=legs_ax[0].s, t=t, D=D, fusion=mf, legs=tuple(legs_ax), _verified=True))
        else:
            legs.append(legs_ax.pop())
    return tuple(legs) if multiple_legs else legs.pop()


def get_leg_structure(a, axis, native=False):  # pragma: no cover
    r"""
    .. deprecated::
        to inspect Legs of the tensor, use :meth:`yastn.Tensor.get_legs`.

    Find all charges and the corresponding bond dimension for n-th leg.

    Parameters
    ----------
    axis : int
        Index of a leg.

    native : bool
        consider native legs if True; otherwise meta/fused legs (default).

    Returns
    -------
        tDn : dict of {charge of the sector: size of the sector}
    """
    axis, = _clear_axes(axis)
    if not native:
        axis, = _unpack_axes(a.mfs, axis)
    tset = np.array(a.struct.t, dtype=np.int64).reshape((len(a.struct.t), len(a.struct.s), len(a.struct.n)))
    Dset = np.array(a.struct.D, dtype=np.int64).reshape((len(a.struct.D), len(a.struct.s)))
    tset = tset[:, axis, :]
    Dset = Dset[:, axis]
    tset = tset.reshape(len(tset), len(axis) * a.config.sym.NSYM).tolist()
    Dset = np.prod(Dset, axis=1, dtype=np.int64) if len(axis) > 1 else Dset.reshape(-1)
    Dset = Dset.tolist()

    tDn = {tuple(tn): Dn for tn, Dn in zip(tset, Dset)}
    return tDn


def get_leg_charges_and_dims(a, native=False):  # pragma: no cover
    """
    .. deprecated::
        to inspect Legs of the tensor, use :meth:`yastn.Tensor.get_legs`.

    Collect information about charges and dimensions on all legs into two lists.
    """
    _tmp = [a.get_leg_structure(n, native=native) for n in range(a.ndim_n if native else a.ndim)]
    _tmp = [{k: lst[k] for k in sorted(lst)} for lst in _tmp]
    ts_and_Ds= tuple(zip(*[tuple(zip(*lst.items())) for lst in _tmp]))
    if len(ts_and_Ds) < 1:
        return (), ()
    ts, Ds = ts_and_Ds
    return ts, Ds


############################
#   Down-casting tensors   #
############################

def to_dense(a, legs=None, native=False, reverse=False) -> numpy.ndarray | torch.tensor:
    r"""
    Create dense tensor corresponding to the symmetric tensor.

    The type of the returned tensor depends on the backend, i.e. ``numpy.ndarray`` or ``torch.tensor``.
    Blocks are ordered according to increasing charges on each leg.
    It is possible to supply a list of additional charge sectors to be included by explictly specifying `legs`.
    These legs should be consistent with current structure of the tensor.
    This allows to fill in extra zero blocks.

    Parameters
    ----------
    legs : dict[int, yastn.Leg]
        specify extra charge sectors on the legs by adding desired :class:`yastn.Leg`
        under legs's index into dictionary.

    native: bool
        output native tensor (ignoring meta-fusion of legs).

    reverse: bool
        reverse the order in which blocks are sorted. Default order is ascending in
        values of block's charges.
    """
    c = a.to_nonsymmetric(legs, native, reverse)
    x = c.config.backend.clone(c._data)
    x = c.config.backend.diag_create(x) if c.isdiag else x.reshape(c.struct.D[0])
    return x


def to_numpy(a, legs=None, native=False, reverse=False) -> numpy.ndarray:
    r"""
    Create dense :class:`numpy.ndarray`` corresponding to the symmetric tensor.
    See :func:`yastn.to_dense`.
    """
    return a.config.backend.to_numpy(a.to_dense(legs, native, reverse))


def to_raw_tensor(a) -> numpy.ndarray | torch.tensor:
    """
    If the symmetric tensor has just a single non-empty block, return raw tensor representing
    that block.

    The type of the returned tensor depends on the backend, i.e. ``numpy.ndarray`` or ``torch.tensor``.
    """
    if len(a.struct.D) == 1:
        return a._data.reshape(a.struct.D[0])
    raise YastnError('Only tensor with a single block can be converted to raw tensor.')


def to_nonsymmetric(a, legs=None, native=False, reverse=False) -> yastn.Tensor:
    r"""
    Create equivalent ``yastn.Tensor`` with no explict symmetry. All blocks of the original
    tensor are accummulated into a single block.

    Blocks are ordered according to increasing charges on each leg.
    It is possible to supply a list of additional charge sectors to be included by explictly
    specifying `legs`. These legs should be consistent with current structure of the tensor.
    This allows to fill in extra zero blocks.

    .. note::
        YASTN structure is redundant since resulting tensor is effectively just
        a single dense block. To obtain this single dense block directly, use :meth:`yastn.Tensor.to_dense`.

    Parameters
    ----------
    legs : dict[int, yastn.Leg]
        specify extra charge sectors on the legs by adding desired :class:`yastn.Leg`
        under legs's index into dictionary.

    native: bool
        output native tensor (ignoring meta-fusion of legs).

    reverse: bool
        reverse the order in which blocks are sorted. Default order is ascending in
        values of block's charges.
    """
    config_dense = a.config._replace(sym=sym_none)

    legs_a = list(a.get_legs(native=native))
    ndim_a = len(legs_a)  # ndim_n if native else ndim


    if legs is not None:
        if any((n < 0) or (n >= ndim_a) for n in legs.keys()):
            raise YastnError('Specified leg out of ndim')
        legs_new = {n: leg_union(legs_a[n], leg) for n, leg in legs.items()}
        if any(_leg_fusions_need_mask(leg, legs_a[n]) for n, leg in legs_new.items()):
            a = _embed_tensor(a, legs_a, legs_new)  # mask needed
        for n, leg in legs_new.items():
            legs_a[n] = leg

    Dtot = tuple(sum(leg.D) for leg in legs_a)

    if ndim_a == 0:  # scalar
        meta = [(slice(*sl.slcs[0]), ()) for sl in a.slices]
    else:
        step = -1 if reverse else 1
        tD = []
        for leg in legs_a:
            Dlow, tDn = 0, {}
            for tn, Dn in zip(leg.t[::step], leg.D[::step]):
                Dhigh = Dlow + Dn
                tDn[tn] = (Dlow, Dhigh)
                Dlow = Dhigh
            tD.append(tDn)

        axes = tuple((n,) for n in range(ndim_a))
        if not native:
            axes = tuple(_unpack_axes(a.mfs, *axes))

        lt, nsym = len(a.struct.t), len(a.struct.n)
        tset = np.array(a.struct.t, dtype=np.int64).reshape(lt, a.ndim_n, nsym)
        tset_ax = list(zip(*[tset[:, ax, :].reshape(lt, len(ax) * nsym).tolist() for ax in axes]))
        meta = [(slice(*t_sl.slcs[0]), tuple(tDn[tuple(tt)] for tDn, tt in zip(tD, t_ax))) for t_sl, t_ax in zip(a.slices, tset_ax)]

    c_s = a.get_signature(native)
    c_t = ((),)
    c_D = (Dtot,)

    if a.isdiag:
        Dtot = Dtot[:1]
        meta = [(sl, D[:1]) for sl, D in meta]

    Dp = reduce(mul, Dtot, 1)
    c_struct = _struct(s=c_s, n=(), diag=a.isdiag, t=c_t, D=c_D, size=Dp)
    c_slices = (_slc(((0, Dp),), c_D[0], Dp),)
    data = a.config.backend.merge_to_dense(a._data, Dtot, meta)
    return a._replace(config=config_dense, struct=c_struct, slices=c_slices, data=data, mfs=None, hfs=None)


def zero_of_dtype(a):
    """ Return zero scalar of the instance specified by backend and dtype. """
    return a.config.backend.zeros((), dtype=a.yast_dtype, device=a.device)


def to_number(a, part=None) -> number:
    r"""
    Assuming the symmetric tensor has just a single non-empty block of total dimension one,
    return this element as a scalar.

    The type of the scalar is given by the backend.
    For empty tensor return 0.

    .. note::
        This operation preserves autograd.

    Parameters
    ----------
    part : str
        if 'real', returns real part only.
    """
    size = a.size
    if size == 1:
        x = a.config.backend.first_element(a._data)
    elif size == 0:
        x = a.zero_of_dtype()
    else:
        raise YastnError('Only single-element (symmetric) Tensor can be converted to scalar')
    return a.config.backend.real(x) if part == 'real' else x


def item(a) -> float:
    """
    Assuming the symmetric tensor has just a single non-empty block of total dimension one,
    return this element as standard Python scalar.

    For empty tensor, returns 0.
    """
    size = a.size
    if size == 1:
        return a.config.backend.item(a._data)
    if size == 0:
        return 0
    raise YastnError("Only single-element (symmetric) Tensor can be converted to scalar")
