""" Contractions of yast tensors """
import numpy as np
from ._auxliary import _clear_axes, _unpack_axes, _common_rows, _common_keys, _tarray, _Darray
from ._tests import YastError, _check, _test_configs_match, _test_fusions_match
from ._merging import _merge_to_matrix, _unmerge_matrix, _flip_sign_hf
from ._merging import _masks_for_tensordot, _masks_for_vdot, _masks_for_trace

__all__ = ['tensordot', 'vdot', 'trace', 'swap_gate', 'ncon']


def tensordot(a, b, axes, conj=(0, 0)):
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
        Defult is (0, 0), i.e. no tensor is conjugated

    Returns
    -------
    tansor: Tensor
    """
    _test_configs_match(a, b)
    la_con, lb_con = _clear_axes(*axes)  # contracted meta legs
    la_out = tuple(ii for ii in range(a.mlegs) if ii not in la_con)  # outgoing meta legs
    lb_out = tuple(ii for ii in range(b.mlegs) if ii not in lb_con)  # outgoing meta legs

    axes_a = _unpack_axes(a, la_out, la_con)  # native legs of a; tuple of two tuples
    axes_b = _unpack_axes(b, lb_con, lb_out)  # native legs of b; tuple of two tuples

    conja, conjb = (1 - 2 * conj[0]), (1 - 2 * conj[1])
    mconj = (-conja * conjb)

    if _check["signatures_match"] and not all(a.struct.s[i] == mconj * b.struct.s[j] for i, j in zip(axes_a[1], axes_b[0])):
        raise YastError('Signs do not match in tensordot')

    needs_mask = False
    for i1, i2 in zip(axes_a[1], axes_b[0]):
        if a.hard_fusion[i1].tree != b.hard_fusion[i2].tree:
            raise YastError('Order of hard fusions on leg %1d of a and leg %1d of b do not match' % (i1, i2))
        if _check["signatures_match"] and ((mconj == 1 and a.hard_fusion[i1].s != b.hard_fusion[i2].s) or
                                            (mconj == -1 and a.hard_fusion[i1].s != b.hard_fusion[i2].ms)):
            raise YastError('Hard fusions do not match. Signature problem.')
        if a.hard_fusion[i1].t != b.hard_fusion[i2].t or a.hard_fusion[i1].D != b.hard_fusion[i2].D:
            needs_mask = True

    c_n = np.array(a.struct.n + b.struct.n, dtype=int).reshape((1, 2, a.config.sym.NSYM))
    c_s = np.array([conja, conjb], dtype=int)
    c_n = a.config.sym.fuse(c_n, c_s, 1)[0]

    ind_a, ind_b = _common_rows(_tarray(a)[:, axes_a[1], :], _tarray(b)[:, axes_b[0], :])
    s_eff_a, s_eff_b = (conja, -conja), (conjb, -conjb)

    aa = a.diag() if a.isdiag else a
    bb = b.diag() if b.isdiag else b

    Am, ls_l, ls_ac, ua_l, ua_r = _merge_to_matrix(aa, axes_a, s_eff_a, ind_a, sort_r=True)
    Bm, ls_bc, ls_r, ub_l, ub_r = _merge_to_matrix(bb, axes_b, s_eff_b, ind_b)

    meta_dot = tuple((al + br, al + ar, bl + br) for al, ar, bl, br in zip(ua_l, ua_r, ub_l, ub_r))

    if needs_mask:
        msk_a, msk_b = _masks_for_tensordot(a.config, a.struct, a.hard_fusion, axes_a[1], ls_ac,
                                                    b.struct, b.hard_fusion, axes_b[0], ls_bc)
        Am = {ul + ur: Am[ul + ur][:, msk_a[ur]] for ul, ur in zip(ua_l, ua_r)}
        Bm = {ul + ur: Bm[ul + ur][msk_b[ul], :] for ul, ur in zip(ub_l, ub_r)}
    elif _check["consistency"] and (ua_r != ub_l or ls_ac != ls_bc):
        raise YastError('Mismatch in bond dimensions of contracted legs.')

    c_s = tuple(conja * a.struct.s[i1] for i1 in axes_a[0]) + tuple(conjb * b.struct.s[i2] for i2 in axes_b[1])
    c_meta_fusion = [a.meta_fusion[ii] for ii in la_out] + [b.meta_fusion[ii] for ii in lb_out]
    c_hard_fusion = [a.hard_fusion[ii] for ii in axes_a[0]] if conj[0] == 0 else \
                    [_flip_sign_hf(a.hard_fusion[ii]) for ii in axes_a[0]]
    c_hard_fusion += [b.hard_fusion[ii] for ii in axes_b[1]] if conj[1] == 0 else \
                    [_flip_sign_hf(b.hard_fusion[ii]) for ii in axes_b[1]]
    c = a.__class__(config=a.config, s=c_s, n=c_n, meta_fusion=c_meta_fusion, hard_fusion=c_hard_fusion)

    c.A = c.config.backend.dot(Am, Bm, conj, meta_dot)
    _unmerge_matrix(c, ls_l, ls_r)
    return c



# def diagdot(a, b, axes, conj=(0, 0)):
#     r"""
#     Compute tensor dot product of a tensor with a diagonal tensor.

#     Other tensors should be diagonal.
#     Legs of a new tensor are ordered in the same way as those of the first one.
#     Produce diagonal tensor if both are diagonal.

#     Parameters
#     ----------
#     other: Tensor
#         diagonal tensor

#     axis: int or tuple
#         leg of non-diagonal tensor to be multiplied by the diagonal one.

#     conj: tuple
#         shows which tensor to conjugate: (0, 0), (0, 1), (1, 0), (1, 1)
#     """

#     if not b.isdiag:
#         raise YastError('Second tensor should be diagonal')

#     conja = (1 - 2 * conj[0])
#     na_con = 0 if self.isdiag else axis if isinstance(axis, int) else axis[0]

#     t_a_con = self.tset[:, na_con, :]
#     block_a = sorted([(tuple(x.flat), tuple(y.flat)) for x, y in zip(t_a_con, self.tset)], key=lambda x: x[0])
#     block_b = sorted([tuple(x.flat) for x in other.tset])
#     block_a = itertools.groupby(block_a, key=lambda x: x[0])
#     block_b = iter(block_b)

#     to_execute = []
#     try:
#         tta, ga = next(block_a)
#         ttb = next(block_b)
#         while True:
#             if tta == ttb:
#                 for ta in ga:
#                     to_execute.append((ta[1], ttb, ta[1]))
#                 tta, ga = next(block_a)
#                 ttb = next(block_b)
#             elif tta < ttb:
#                 tta, ga = next(block_a)
#             elif tta > ttb:
#                 ttb = next(block_b)
#     except StopIteration:
#         pass

#     c = Tensor(settings=self.conf, s=conja * self.s, n=conja * self.n, isdiag=self.isdiag)
#     c.A = self.conf.back.dot_diag(self.A, other.A, conj, to_execute, na_con, self._ndim)
#     c.tset = np.array([ind for ind in c.A], dtype=np.int).reshape(len(c.A), c._ndim, c.nsym)
#     return c



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
    lout = tuple(ii for ii in range(a.mlegs) if ii not in lin1 + lin2)
    in1, in2, out = _unpack_axes(a, lin1, lin2, lout)

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
    c_meta_fusion=tuple(a.meta_fusion[ii] for ii in lout)
    c_hard_fusion=tuple(a.hard_fusion[ii] for ii in out)

    c = a.__class__(config=a.config, s=c_s, n=a.struct.n, meta_fusion=c_meta_fusion, hard_fusion=c_hard_fusion)

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
    AA = {ind: a.config.backend.diag_create(x) for ind, x in a.A.items()} if a.isdiag else a.A
    if needs_mask:
        t12 = tuple(tuple(t.flat) for t in t1[ind])
        D1 = tuple(tuple(x.flat) for x in D1[ind])
        D2 = tuple(tuple(x.flat) for x in D2[ind])
        msk12 = _masks_for_trace(a.config, t12, D1, D2, a.hard_fusion, in1, in2)
        meta = [(tuple(to[n]), tuple(tset[n].flat), tuple(Drsh[n]), tt) for n, tt in zip(ind, t12)]
        c.A = c.config.backend.trace_with_mask(AA, order, meta, msk12)
    else:
        if not np.all(D1[ind] == D2[ind]):
            raise YastError('Not all bond dimensions of the traced legs match')
        meta = [(tuple(to[n]), tuple(tset[n].flat), tuple(Drsh[n])) for n in ind]
        c.A = c.config.backend.trace(AA, order, meta)
    c.update_struct()
    return c



# def trace(self, axes=(0, 1)):
#     """
#     Compute trace of legs specified by axes.

#     For diagonal tensor, return 0-rank tensor
#     """
#     try:
#         in1 = tuple(axes[0])
#     except TypeError:
#         in1 = (axes[0],)  # indices going u
#     try:
#         in2 = tuple(axes[1])
#     except TypeError:
#         in2 = (axes[1],)  # indices going v

#     if len(in1) != len(in2):
#         logger.exception('Number of axis to trace should be the same')
#         raise FatalError

#     if self.isdiag:
#         if in1 == in2 == ():
#             return self.copy()
#         elif in1 + in2 == (0, 1) or in1 + in2 == (1, 0):
#             a = Tensor(settings=self.conf)
#             to_execute = []
#             for tt in self.tset:
#                 to_execute.append((tuple(tt.flat), ()))  # old, new
#             a.A = a.conf.back.trace_axis(A=self.A, to_execute=to_execute, axis=0)
#         else:
#             logger.exception('Wrong axes for diagonal tensor')
#             raise FatalError
#     else:
#         out = tuple(ii for ii in range(self._ndim) if ii not in in1 + in2)
#         nout = np.array(out, dtype=np.int)
#         nin1 = np.array(in1, dtype=np.int)
#         nin2 = np.array(in2, dtype=np.int)
#         if not all(self.s[nin1] == -self.s[nin2]):
#             logger.exception('Signs do not match')
#             raise FatalError

#         to_execute = []
#         for tt in self.tset:
#             if np.all(tt[nin1, :] == tt[nin2, :]):
#                 to_execute.append((tuple(tt.flat), tuple(tt[nout].flat)))  # old, new
#         a = Tensor(settings=self.conf, s=self.s[nout], n=self.n)
#         a.A = a.conf.back.trace(A=self.A, to_execute=to_execute, in1=in1, in2=in2, out=out)

#     a.tset = np.array([ind for ind in a.A], dtype=np.int).reshape(len(a.A), a._ndim, a.nsym)
#     return a

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
    try:
        fss = a.config.sym.FERMIONIC  # fermionic symmetry sectors
    except AttributeError:
        return a
    if any(fss):
        c = a if inplace else a.clone()
        tset = _tarray(c)
        l1, l2 = _clear_axes(*axes)  # swaped groups of legs
        if len(set(l1) & set(l2)) > 0:
            raise YastError('Cannot sweep the same index')
        if l2 == (-1,):
            l1, l2 = l2, l1
        if l1 == (-1,):
            l2, = _unpack_axes(a, l2)
            t1 = c.n
        else:
            l1, l2 = _unpack_axes(a, l1, l2)
            al1 = np.array(l1, dtype=np.intp)
            t1 = np.sum(tset[:, al1, :], axis=1)
        al2 = np.array(l2, dtype=np.intp)
        t2 = np.sum(tset[:, al2, :], axis=1)
        tp = np.sum(t1 * t2, axis=1) % 2 == 1
        for ind, odd in zip(a.struct.t, tp):
            if odd:
                c.A[ind] = -c.A[ind]
        return c
    return a


def ncon(ts, inds, conjs=None):
    """Execute series of tensor contractions"""
    if len(ts) != len(inds):
        raise YastError('Wrong number of tensors')
    for ii, ind in enumerate(inds):
        if ts[ii].get_ndim() != len(ind):
            raise YastError('Wrong number of legs in %02d-th tensors.' % ii)

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







# def trace_dot_diag(self, other, axis1=0, axis2=1, conj=(0, 0)):
#     r""" Contract two legs of a tensor with a diagonal tensor -- equivalent to dot_diag and trace of the result.

#     Other tensor should be diagonal.
#     Legs of a new tensor are ordered in the same way as those of the first one.

#     Parameters
#     ----------
#     other: Tensor
#         diagonal tensor

#     axis1, axis2: int
#         2 legs of the first tensor to be multiplied by the diagonal one.
#         they are ignored if the first tensor is diagonal.

#     conj: tuple
#         shows which tensor to conjugate: (0, 0), (0, 1), (1, 0), (1, 1)
#     """
#     if self.isdiag:
#         return self.dot_diag(other, axis=0, conj=conj).trace()

#     if self.s[axis1] != -self.s[axis2]:
#         logger.exception('Signs do not match')
#         raise FatalError

#     conja = (1 - 2 * conj[0])
#     na_con = np.array([axis1, axis2], dtype=np.int)
#     out = tuple(ii for ii in range(self._ndim) if ii != axis1 and ii != axis2)
#     nout = np.array(out, dtype=np.int)

#     ind = np.all(self.tset[:, axis1, :] == self.tset[:, axis2, :], axis=1)
#     tset = self.tset[ind]
#     t_a_con = tset[:, axis1, :]
#     t_a_out = tset[:, nout, :]

#     block_a = sorted([(tuple(x.flat), tuple(y.flat), tuple(z.flat)) for x, y, z in zip(t_a_con, tset, t_a_out)], key=lambda x: x[0])
#     block_b = sorted([tuple(x.flat) for x in other.tset])
#     block_a = itertools.groupby(block_a, key=lambda x: x[0])
#     block_b = iter(block_b)

#     to_execute = []
#     try:
#         tta, ga = next(block_a)
#         ttb = next(block_b)
#         while True:
#             if tta == ttb:
#                 for ta in ga:
#                     to_execute.append((ta[1], ttb, ta[2]))
#                 tta, ga = next(block_a)
#                 ttb = next(block_b)
#             elif tta < ttb:
#                 tta, ga = next(block_a)
#             elif tta > ttb:
#                 ttb = next(block_b)
#     except StopIteration:
#         pass

#     c = Tensor(settings=self.conf, s=conja * self.s[nout], n=conja * self.n, isdiag=False)
#     c.A = self.conf.back.trace_dot_diag(self.A, other.A, conj, to_execute, axis1, axis2, self._ndim)
#     c.tset = np.array([ind for ind in c.A], dtype=np.int).reshape(len(c.A), c._ndim, c.nsym)
#     return c