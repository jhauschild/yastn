""" Contractions of yast tensors """
from functools import lru_cache
from itertools import groupby, product
import numpy as np
from ._auxliary import _clear_axes, _unpack_axes, _common_rows, _common_keys, _tarray, _Darray, _struct
from ._tests import YastError, _check, _test_configs_match, _test_fusions_match
from ._merging import _merge_to_matrix, _unmerge_matrix, _flip_sign_hf
from ._merging import _masks_for_tensordot, _masks_for_vdot, _masks_for_trace, _masks_for_axes


__all__ = ['tensordot', 'vdot', 'trace', 'swap_gate', 'ncon', 'broadcast', 'mask']


def tensordot(a, b, axes, conj=(0, 0), policy=None):
    r"""
    Compute tensor dot product of two tensor along specified axes.

    Outgoing legs are ordered such that first ones are the remaining legs of the first tensor in the original order,
    and than those of the second tensor.

    Parameters
    ----------
    a, b: Tensors to contract

    axes: tuple
        legs of both tensors (for each it is specified by int or tuple of ints)
        e.g. axes=(0, 3) to contract 0th leg of a with 3rd leg of b
                axes=((0, 3), (1, 2)) to contract legs 0 and 3 of a with 1 and 2 of b, respectivly.

    conj: tuple
        shows which tensor to conjugate: (0, 0), (0, 1), (1, 0), (1, 1).
        Defult is (0, 0), i.e. neither tensor is conjugated

    policy: str
        method of executing contraction.
        `merge` is merging blocks into effective 2d matrices before executing matrix multiplication
        (typically peferable for many small blocks).
        `direct` is performing multiplication block by block
        (might be preferable for tensors with fewer legs, or contracting over single axis).
        `hybrid` (default) switches between those methods using simple heuristic.

    Returns
    -------
    tansor: Tensor
    """

    la_con, lb_con = _clear_axes(*axes)  # contracted meta legs
    if len(la_con) != len(lb_con):
        raise YastError('Number of contracted axes of two tensors should be the same.')

    if b.isdiag:
        if len(lb_con) == 1:
            c = a.broadcast(b, axis=la_con[0], conj=conj)
            c.moveaxis(source=la_con, destination=(-1,), inplace=True)
        elif len(lb_con) == 2:
            c = a.broadcast(b, axis=la_con[0], conj=conj)
            c = c.trace(axes=la_con)
        elif len(lb_con) == 0:
            raise YastError('Cannot do outer product with diagonal tensor -- call b.diag() first.')
        else:
            raise YastError('Too many axis to contract.')
        return c

    if a.isdiag:
        if len(la_con) == 1:
            c = b.broadcast(a, axis=lb_con[0], conj=conj[::-1])
            c.moveaxis(source=lb_con, destination=(0,), inplace=True)
        elif len(la_con) == 2:
            c = b.broadcast(a, axis=lb_con[0], conj=conj[::-1])
            c = c.trace(axes=lb_con)
        elif len(la_con) == 0:
            raise YastError('Cannot do outer product with diagonal tensor -- call b.diag() first.')
        else:
            raise YastError('Too many axis to contract.')
        return c

    _test_configs_match(a, b)
    la_out = tuple(ii for ii in range(a.ndim) if ii not in la_con)  # outgoing meta legs
    lb_out = tuple(ii for ii in range(b.ndim) if ii not in lb_con)  # outgoing meta legs
    axes_a = _unpack_axes(a.meta_fusion, la_out, la_con)  # native legs of a; tuple of two tuples
    axes_b = _unpack_axes(b.meta_fusion, lb_con, lb_out)  # native legs of b; tuple of two tuples
    if len(axes_a[1]) != len(axes_b[0]):
        raise YastError('Number of contracted native axes of two tensors should be the same.')

    conja, conjb = (1 - 2 * conj[0]), (1 - 2 * conj[1])
    mconj = - conja * conjb

    if _check["signatures_match"] and not all(a.struct.s[i] == mconj * b.struct.s[j] for i, j in zip(axes_a[1], axes_b[0])):
        raise YastError('Signatures of contracted legs do not match.')

    needs_mask = False  # for hard-fused legs
    for i1, i2 in zip(axes_a[1], axes_b[0]):
        if a.hard_fusion[i1].tree != b.hard_fusion[i2].tree:
            raise YastError(f'Hard fusions of leg {i1} of a and leg {i2} of b are not compatible: mismatch in the number of fused legs or fusion order.')
        if _check["signatures_match"] and ((mconj == 1 and a.hard_fusion[i1].s != b.hard_fusion[i2].s) or
                                            (mconj == -1 and a.hard_fusion[i1].s != b.hard_fusion[i2].ms)):
            raise YastError('Hard fusions of leg {i1} of a and leg {i2} of b are not compatible: signatures do not match.')
        if a.hard_fusion[i1].t != b.hard_fusion[i2].t or a.hard_fusion[i1].D != b.hard_fusion[i2].D:
            needs_mask = True

    c_s = tuple(conja * a.struct.s[i1] for i1 in axes_a[0]) + tuple(conjb * b.struct.s[i2] for i2 in axes_b[1])
    c_n = np.array(a.struct.n + b.struct.n, dtype=int).reshape((1, 2, a.config.sym.NSYM))
    c_n = tuple(a.config.sym.fuse(c_n, (conja, conjb), 1)[0])
    c_meta_fusion = [a.meta_fusion[ii] for ii in la_out] + [b.meta_fusion[ii] for ii in lb_out]
    c_hard_fusion = [a.hard_fusion[ii] for ii in axes_a[0]] if conj[0] == 0 else \
                    [_flip_sign_hf(a.hard_fusion[ii]) for ii in axes_a[0]]
    c_hard_fusion += [b.hard_fusion[ii] for ii in axes_b[1]] if conj[1] == 0 else \
                    [_flip_sign_hf(b.hard_fusion[ii]) for ii in axes_b[1]]

    if policy is None:
        policy = a.config.default_tensordot

    if policy == 'merge' or (policy == 'hybrid' and len(axes_a[1]) != 1) or a.config.sym.NSYM == 0:
        ind_a, ind_b = _common_rows(_tarray(a)[:, axes_a[1], :], _tarray(b)[:, axes_b[0], :])
        s_eff_a, s_eff_b = (conja, -conja), (conjb, -conjb)

        Am, ls_l, ls_ac, ua_l, ua_r = _merge_to_matrix(a, axes_a, s_eff_a, ind_a, sort_r=True)
        Bm, ls_bc, ls_r, ub_l, ub_r = _merge_to_matrix(b, axes_b, s_eff_b, ind_b)

        meta_dot = tuple((al + br, al + ar, bl + br) for al, ar, bl, br in zip(ua_l, ua_r, ub_l, ub_r))

        if needs_mask:
            msk_a, msk_b = _masks_for_tensordot(a.config, a.struct, a.hard_fusion, axes_a[1], ls_ac,
                                                        b.struct, b.hard_fusion, axes_b[0], ls_bc)
            Am = {ul + ur: Am[ul + ur][:, msk_a[ur]] for ul, ur in zip(ua_l, ua_r)}
            Bm = {ul + ur: Bm[ul + ur][msk_b[ul], :] for ul, ur in zip(ub_l, ub_r)}
        elif _check["consistency"] and (ua_r != ub_l or ls_ac != ls_bc):
            raise YastError('Mismatch in bond dimensions of contracted legs.')

        c = a.__class__(config=a.config, s=c_s, n=c_n, meta_fusion=c_meta_fusion, hard_fusion=c_hard_fusion)
        c.A = c.config.backend.dot(Am, Bm, conj, meta_dot)
        _unmerge_matrix(c, ls_l, ls_r)
    else:
        meta, c_t, c_D = _meta_tensordot_nomerge(a.struct, b.struct, axes_a, axes_b)
        c_struct = _struct(t=c_t, D=c_D, s=c_s, n=c_n)
        c = a.__class__(config=a.config, isdiag=a.isdiag, meta_fusion=c_meta_fusion, hard_fusion=c_hard_fusion, struct=c_struct)
        oA = tuple(axes_a[0] + axes_a[1])
        oB = tuple(axes_b[0] + axes_b[1])
        if needs_mask:
            ma, mb = _masks_for_axes(a.config, a.struct, a.hard_fusion, axes_a[1], b.struct, b.hard_fusion, axes_b[0], meta)
            c.A = a.config.backend.dot_nomerge_masks(a.A, b.A, conj, oA, oB, meta, ma, mb)
        else:
            c.A = a.config.backend.dot_nomerge(a.A, b.A, conj, oA, oB, meta)
    return c


@lru_cache(maxsize=1024)
def _meta_tensordot_nomerge(a_struct, b_struct, axes_a, axes_b):
    """ meta information for backend, and new tensor structure for tensordot_nomerge """
    nsym = len(a_struct.n)
    a_ndim, b_ndim = len(a_struct.s), len(b_struct.s)

    ta = np.array(a_struct.t, dtype=int).reshape(len(a_struct.t), a_ndim, nsym)
    tb = np.array(b_struct.t, dtype=int).reshape(len(b_struct.t), b_ndim, nsym)
    Da = np.array(a_struct.D, dtype=int).reshape(len(a_struct.D), a_ndim)
    Db = np.array(b_struct.D, dtype=int).reshape(len(b_struct.D), b_ndim)

    ta_con = ta[:, axes_a[1], :]
    tb_con = tb[:, axes_b[0], :]
    ta_out = ta[:, axes_a[0], :]
    tb_out = tb[:, axes_b[1], :]

    Da_con = np.prod(Da[:, axes_a[1]], axis=1)
    Db_con = np.prod(Db[:, axes_b[0]], axis=1)
    Da_out = Da[:, axes_a[0]]
    Db_out = Db[:, axes_b[1]]
    Da_pro = np.prod(Da_out, axis=1)
    Db_pro = np.prod(Db_out, axis=1)

    block_a = [(tuple(t1.flat), tuple(t2.flat), tuple(t3.flat), D1, tuple(D2), D3) for t1, t2, t3, D1, D2, D3 in zip(ta_con, ta_out, ta, Da_con, Da_out, Da_pro)]
    block_a = groupby(sorted(block_a, key=lambda x: x[0]), key=lambda x: x[0])

    block_b = [(tuple(t1.flat), tuple(t2.flat), tuple(t3.flat), D1, tuple(D2), D3) for t1, t2, t3, D1, D2, D3 in zip(tb_con, tb_out, tb, Db_con, Db_out, Db_pro)]
    block_b = groupby(sorted(block_b, key=lambda x: x[0]), key=lambda x: x[0])

    meta = []
    try:
        tta, ga = next(block_a)
        ttb, gb = next(block_b)
        while True:
            if tta == ttb:
                for ta, tb in product(ga, gb):
                    meta.append((ta[2], tb[2], ta[1] + tb[1], (ta[5], ta[3]), (tb[3], tb[5]), ta[4] + tb[4], ta[0]))
                tta, ga = next(block_a)
                ttb, gb = next(block_b)
            elif tta < ttb:
                tta, ga = next(block_a)
            elif tta > ttb:
                ttb, gb = next(block_b)
    except StopIteration:
        pass

    meta = tuple(sorted(meta, key=lambda x: x[2]))
    if len(axes_a[1]) == 1:
        c_t = tuple(mm[2] for mm in meta)
        c_D = tuple(mm[5] for mm in meta)
    else:
        if len(meta) > 0:
            ctD = tuple((kk, next(mm)[5]) for kk, mm in groupby(meta, key=lambda x: x[2]))
            c_t, c_D = zip(*ctD)
        else:
            c_t, c_D = tuple(), tuple()
    return meta, c_t, c_D


def broadcast(a, b, axis, conj=(0, 0)):
    r"""
    Compute tensor dot product of tensor a with diagonal tensor b.

    Legs of resulting tensor are ordered in the same way as those of tensor a.
    Produce diagonal tensor if both are diagonal.

    Parameters
    ----------
    a, b: Tensors
        b is a diagonal tensor

    axis: int
        leg of non-diagonal tensor to be multiplied by the diagonal one.

    conj: tuple
        shows which tensor to conjugate: (0, 0), (0, 1), (1, 0), (1, 1)
    """
    _test_configs_match(a, b)
    if not b.isdiag:
        raise YastError('Tensor b should be diagonal')
    if not isinstance(axis, int):
        raise YastError('axis should be int')

    axis = axis % a.ndim
    if a.meta_fusion[axis] != (1,):
        raise YastError('For applying diagonal mask, leg of tensor a specified by axis cannot be fused')
    axis = sum(a.meta_fusion[ii][0] for ii in range(axis))  # unpack
    if a.hard_fusion[axis].tree != (1,):
        raise YastError('For applying diagonal mask, leg of tensor a specified by axis cannot be fused')

    conja = (1 - 2 * conj[0])
    c_hard_fusion = a.hard_fusion if conja == 1 else tuple(_flip_sign_hf(x) for x in a.hard_fusion)
    meta, c_struct = _meta_broadcast(a.config, a.struct, b.struct, conja, axis)

    c = a.__class__(config=a.config, isdiag=a.isdiag, meta_fusion=a.meta_fusion, hard_fusion=c_hard_fusion, struct=c_struct)
    a_ndim, axis = (1, 0) if a.isdiag else (a.ndimn, axis)
    c.A = a.config.backend.dot_diag(a.A, b.A, conj, meta, axis, a_ndim)
    return c


@lru_cache(maxsize=1024)
def _meta_broadcast(config, a_struct, b_struct, conja, axis):
    """ meta information for backend, and new tensor structure for brodcast """
    nsym = config.sym.NSYM
    ind_tb = tuple(x[:nsym] for x in b_struct.t)
    ind_ta = tuple(x[axis * nsym: (axis + 1) * nsym] for x in a_struct.t)
    meta = tuple((ta, ia + ia, ta) for ta, ia in zip(a_struct.t, ind_ta) if ia in ind_tb)
    c_n = np.array(a_struct.n, dtype=int).reshape((1, 1, -1))
    c_n = tuple(config.sym.fuse(c_n, (1,), conja)[0])
    c_s = a_struct.s if conja == 1 else tuple(-x for x in a_struct.s)
    tD = tuple((ta, da) for ta, da, ia in zip(a_struct.t, a_struct.D, ind_ta) if ia in ind_tb)
    c_t, c_D = zip(*tD)
    c_struct = _struct(t=c_t, D=c_D, s=c_s, n=c_n)
    return meta, c_struct


def mask(a, b, axis=0):
    r"""
    Apply mask given by nonzero elements of diagonal tensor b on specified axis of tensor a.

    Legs of resulting tensor are ordered in the same way as those of tensor a.
    Bond dimensions of specified axis of a are truncated according to the mask.
    Produce diagonal tensor if both are diagonal.

    Parameters
    ----------
    a, b: Tensors
        b is a diagonal tensor

    axis: int
        leg of tensor a where the mask is applied.
    """
    if not b.isdiag:
        raise YastError('Tensor b should be diagonal')
    if not isinstance(axis, int):
        raise YastError('axis should be int')
    _test_configs_match(a, b)

    axis = axis % a.ndim
    if a.meta_fusion[axis] != (1,):
        raise YastError('For applying diagonal mask, leg of tensor a specified by axis cannot be fused')
    axis = sum(a.meta_fusion[ii][0] for ii in range(axis))  # unpack
    if a.hard_fusion[axis].tree != (1,):
        raise YastError('For applying diagonal mask, leg of tensor a specified by axis cannot be fused')
    nsym = b.config.sym.NSYM
    ind_tb = tuple(x[:nsym] for x in b.struct.t if b.config.backend.any_nonzero(b.A[x]))
    ind_ta = tuple(x[axis * nsym: (axis + 1) * nsym] for x in a.struct.t)
    meta = tuple((ta, ia + ia, ta) for ta, ia in zip(a.struct.t, ind_ta) if ia in ind_tb)
    c = a.__class__(config=a.config, isdiag=a.isdiag, meta_fusion=a.meta_fusion, hard_fusion=a.hard_fusion, struct=a.struct)
    a_ndim, axis = (1, 0) if a.isdiag else (a.ndimn, axis)
    c.A = a.config.backend.mask_diag(a.A, b.A, meta, axis, a_ndim)
    c.update_struct()
    return c


def vdot(a, b, conj=(1, 0)):
    r"""
    Compute scalar product x = <a|b> of two tensors. a is conjugated by default.

    Parameters
    ----------
    a, b: Tensor

    conj: tuple
        shows which tensor to conjugate: (0, 0), (0, 1), (1, 0), (1, 1).
        Defult is (1, 0), i.e. tensor a is conjugated.

    Returns
    -------
    x: number
    """
    _test_configs_match(a, b)
    _test_fusions_match(a, b)
    conja, conjb = (1 - 2 * conj[0]), (1 - 2 * conj[1])

    if _check["signatures_match"]:
        if conja * conjb == -1 and any(ha.s != hb.s for ha, hb in zip(a.hard_fusion, b.hard_fusion)):
            raise YastError('Signatures do not match.')
        if conja * conjb == 1 and any(ha.s != hb.ms for ha, hb in zip(a.hard_fusion, b.hard_fusion)):
            raise YastError('Signatures do not match.')

    c_n = np.array(a.struct.n + b.struct.n, dtype=int).reshape((1, 2, a.config.sym.NSYM))
    c_n = a.config.sym.fuse(c_n, (conja, conjb), 1)

    k12, _, _ = _common_keys(a.A, b.A)
    needs_mask = any(ha.t != hb.t or ha.D != hb.D for ha, hb in zip(a.hard_fusion, b.hard_fusion))
    if (len(k12) > 0) and np.all(c_n == 0):
        if needs_mask:
            sla, slb = _masks_for_vdot(a.config, a.struct, a.hard_fusion, b.struct, b.hard_fusion, k12)
            Aa = {t: a.A[t][sla[t]] for t in k12}
            Ab = {t: b.A[t][slb[t]] for t in k12}
        else:
            Aa, Ab = a.A, b.A
        return a.config.backend.vdot(Aa, Ab, conj, k12)
    return a.zero_of_dtype()


def trace(a, axes=(0, 1)):
    """
    Compute trace of legs specified by axes.

    Parameters
    ----------
        axes: tuple
        Legs to be traced out, e.g axes=(0, 1); or axes=((2, 3, 4), (0, 1, 5))

    Returns
    -------
        tensor: Tensor
    """
    lin1, lin2 = _clear_axes(*axes)  # contracted legs
    lout = tuple(ii for ii in range(a.ndim) if ii not in lin1 + lin2)
    in1, in2, out = _unpack_axes(a.meta_fusion, lin1, lin2, lout)

    if len(in1) != len(in2) or len(lin1) != len(lin2):
        raise YastError('Number of axes to trace should be the same')
    if len(in1) == 0:
        return a

    order = in1 + in2 + out

    if not all(a.struct.s[i1] == -a.struct.s[i2] for i1, i2 in zip(in1, in2)):
        raise YastError('Signs do not match')

    needs_mask = any(a.hard_fusion[i1].t != a.hard_fusion[i2].t or a.hard_fusion[i1].D != a.hard_fusion[i2].D
                    for i1, i2 in zip(in1, in2))

    c_s = tuple(a.struct.s[i3] for i3 in out)
    c_meta_fusion = tuple(a.meta_fusion[ii] for ii in lout)
    c_hard_fusion = tuple(a.hard_fusion[ii] for ii in out)

    c = a.__class__(config=a.config, s=c_s, n=a.struct.n, meta_fusion=c_meta_fusion, hard_fusion=c_hard_fusion)

    if a.isdiag:
        if needs_mask:
            raise YastError('Diagonal tensor cannot have nontrivial leg fusion -- this should not have happend ')
        c.A = {(): c.config.backend.sum_elements(a.A)}
        c.update_struct()
        return c

    tset, Dset = _tarray(a), _Darray(a)
    lt = len(tset)
    t1 = tset[:, in1, :].reshape(lt, -1)
    t2 = tset[:, in2, :].reshape(lt, -1)
    to = tset[:, out, :].reshape(lt, -1)
    D1 = Dset[:, in1]
    D2 = Dset[:, in2]
    D3 = Dset[:, out]
    pD1 = np.prod(D1, axis=1).reshape(lt, 1)
    pD2 = np.prod(D2, axis=1).reshape(lt, 1)
    ind = (np.all(t1 == t2, axis=1)).nonzero()[0]
    Drsh = np.hstack([pD1, pD2, D3])
    if needs_mask:
        t12 = tuple(tuple(t.flat) for t in t1[ind])
        D1 = tuple(tuple(x.flat) for x in D1[ind])
        D2 = tuple(tuple(x.flat) for x in D2[ind])
        msk12 = _masks_for_trace(a.config, t12, D1, D2, a.hard_fusion, in1, in2)
        meta = [(tuple(to[n]), tuple(tset[n].flat), tuple(Drsh[n]), tt) for n, tt in zip(ind, t12)]
        c.A = c.config.backend.trace_with_mask(a.A, order, meta, msk12)
    else:
        if not np.all(D1[ind] == D2[ind]):
            raise YastError('Not all bond dimensions of the traced legs match')
        meta = [(tuple(to[n]), tuple(tset[n].flat), tuple(Drsh[n])) for n in ind]
        c.A = c.config.backend.trace(a.A, order, meta)
    c.update_struct()
    return c


def swap_gate(a, axes, inplace=False):
    """
    Return tensor after application of the swap gate.

    Multiply the block with odd charges on swaped legs by -1.
    If one of the provided axes is -1, then swap with the charge n.

    Parameters
    ----------
    axes: tuple
        two groups of legs to be swaped

    Returns
    -------
    tensor : Tensor
    """
    if not a.config.fermionic:
        return a
    fss = (True,) * len(a.struct.n) if a.config.fermionic is True else a.config.fermionic
    axes = tuple(_clear_axes(*axes))  # swapped groups of legs
    tp = _meta_swap_gate(a.struct.t, a.struct.n, a.meta_fusion, a.ndimn, axes, fss)
    if inplace:
        for ts, odd in zip(a.struct.t, tp):
            if odd:
                a.A[ts] = -a.A[ts]
        return a
    c = a.__class__(config=a.config, isdiag=a.isdiag, meta_fusion=a.meta_fusion, hard_fusion=a.hard_fusion, struct=a.struct)
    c.A = {ts: -a.A[ts] if odd else a.config.backend.clone(a.A[ts]) for ts, odd in zip(a.struct.t, tp)}
    return c


@lru_cache(maxsize=1024)
def _meta_swap_gate(t, n, mf, ndim, axes, fss):
    ind_n = [i for i, x in enumerate(axes) if x == (-1,)]
    if len(ind_n) == 0:
        axes = _unpack_axes(mf, *axes)
    else:
        axes = list(axes)
        for ind in ind_n[::-1]:
            axes.pop(ind)
        axes = list(_unpack_axes(mf, *axes))
        for ind in ind_n:
            axes.insert(ind, (-1,))
        axes = tuple(axes)

    tset = np.array(t, dtype=int).reshape((len(t), ndim, len(n)))
    iaxes = iter(axes)
    tp = np.zeros(len(t), dtype=int)

    if len(axes) % 2 == 1:
        raise YastError('Odd number of elements in axes -- needs even.')
    for l1, l2 in zip(*(iaxes, iaxes)):
        if len(set(l1) & set(l2)) > 0:
            raise YastError('Cannot sweep the same index')
        if l2 == (-1,):
            t1 = np.sum(tset[:, l1, :], axis=1)
            t2 = np.array(n, dtype=int).reshape(1, -1)
        elif l1 == (-1,):
            t2 = np.sum(tset[:, l2, :], axis=1)
            t1 = np.array(n, dtype=int).reshape(1, -1)
        else:
            if (-1,) in l1 or (-1,) in l2:
                raise YastError('Swap with tensor charge, i.e. -1, has to be provided as a separate axis.')
            t1 = np.sum(tset[:, l1, :], axis=1) % 2
            t2 = np.sum(tset[:, l2, :], axis=1) % 2
        tp += np.sum(t1[:, fss] * t2[:, fss], axis=1)
    return tuple(tp % 2)


def ncon(ts, inds, conjs=None):
    """Execute series of tensor contractions"""
    if len(ts) != len(inds):
        raise YastError('Wrong number of tensors')
    for ii, ind in enumerate(inds):
        if ts[ii].ndim != len(ind):
            raise YastError(f'Wrong number of legs in {ii}-th input tensor.')

    ts = dict(enumerate(ts))
    cutoff = 512
    cutoff2 = 2 * cutoff
    edges = [(order, leg, ten) if order > 0 else (-order + cutoff2, leg, ten)
             for ten, el in enumerate(inds) for leg, order in enumerate(el)]

    edges.append((cutoff, cutoff, cutoff))
    conjs = [0] * len(inds) if conjs is None else list(conjs)
    edges = sorted(edges, reverse=True, key=lambda x: x[0])  # order of contraction with info on tensor and axis

    order1, leg1, ten1 = edges.pop()
    ax1, ax2 = [], []
    while order1 != cutoff:  # tensordot two tensors; or trace one tensor
        order2, leg2, ten2 = edges.pop()
        if order1 != order2:
            raise YastError('Contracted legs do not match')
        if ten1 < ten2:
            (t1, t2) = (ten1, ten2)
            ax1.append(leg1)
            ax2.append(leg2)
        else:
            (t1, t2) = (ten2, ten1)
            ax1.append(leg2)
            ax2.append(leg1)
        if edges[-1][0] == cutoff or min(edges[-1][2], edges[-2][2]) != t1 or max(edges[-1][2], edges[-2][2]) != t2:
            # execute contraction
            if t1 == t2:  # trace
                ts[t1] = ts[t1].trace(axes=(ax1, ax2))
                ax12 = ax1 + ax2
                for ii, (order, leg, ten) in enumerate(edges):
                    if ten == t1:
                        edges[ii] = (order, leg - sum(ii < leg for ii in ax12), ten)
            else:  # tensordot
                ts[t1] = ts[t1].tensordot(ts[t2], axes=(ax1, ax2), conj=(conjs[t1], conjs[t2]))
                conjs[t1], conjs[t2] = 0, 0
                del ts[t2]
                lt1 = sum(ii[2] == t1 for ii in edges)  # legs of t1
                for ii, (order, leg, ten) in enumerate(edges):
                    if ten == t1:
                        edges[ii] = (order, leg - sum(ii < leg for ii in ax1), ten)
                    elif ten == t2:
                        edges[ii] = (order, lt1 + leg - sum(ii < leg for ii in ax2), t1)
            ax1, ax2 = [], []
        order1, leg1, ten1 = edges.pop()

    if edges:
        while len(ts) > 1:
            edges = sorted(edges, key=lambda x: x[2])
            t1 = edges[0][2]
            t2 = [key for key in ts.keys() if key != t1][0]
            ts[t1] = ts[t1].tensordot(ts[t2], axes=((), ()), conj=(conjs[t1], conjs[t2]))
            conjs[t1], conjs[t2] = 0, 0
            lt1 = sum(ii[2] == t1 for ii in edges)
            for ii, (order, leg, ten) in enumerate(edges):
                if ten == t2:
                    edges[ii] = (order, leg + lt1, t1)
            del ts[t2]
        order = [ed[1] for ed in sorted(edges)]
        _, result = ts.popitem()
        return result.transpose(axes=order, inplace=True)
    it = iter(ts.values())
    result = next(it)
    for num in it:
        result.A[()] = result.A[()] * num.A[()]
    return result
