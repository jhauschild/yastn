"""Support of numpy as a data structure used by yast."""
from itertools import groupby
import warnings
import numpy as np
import scipy.linalg
try:
    import fbpca
except ModuleNotFoundError:  # pragma: no cover
    warnings.warn("fbpca not available", Warning)

rng = {'rng': np.random.default_rng()}  # initialize random number generator
BACKEND_ID = "numpy"
DTYPE = {'float64': np.float64,
         'complex128': np.complex128}


def get_dtype(t):
    return t.dtype


def random_seed(seed):
    rng['rng'] = np.random.default_rng(seed)


def set_num_threads(num_threads):
    warnings.warn("backend_np does not support set_num_threads.", Warning)
    pass


###################################
#     single tensor operations    #
###################################


def detach(x):
    return x


def detach_(x):
    return x


def clone(x):
    return x.copy()


def copy(x):
    return x.copy()


def to_numpy(x):
    return x.copy()


def get_shape(x):
    return x.shape


def get_size(x):
    return x.size


def diag_create(x, p=0):
    return np.diag(x, k=p)


def diag_get(x):
    return np.diag(x).copy()


def get_device(x):
    return 'cpu'


def count_greater(x, cutoff):
    return np.sum(x > cutoff).item()


def real(x):
    return np.real(x)


def imag(x):
    return np.imag(x)


def max_abs(x):
    return np.abs(x).max()


def norm_matrix(x):
    return np.linalg.norm(x)


def count_nonzero(x):
    return np.count_nonzero(x)


def delete(x, sl):
    return np.delete(x, slice(*sl))


def insert(x, start, values):
    return np.insert(x, start, values)


def expm(x):
    return scipy.linalg.expm(x)


#########################
#    output numbers     #
#########################


def first_element(x):
    return x.flat[0]


def item(x):
    return x.item()


def sum_elements(data):
    """ sum of all elements of all tensors in A """
    return data.sum().reshape(1)


def norm(data, p):
    """ 'fro' for Frobenious; 'inf' for max(abs(A)) """
    if p == 'fro':
        return np.linalg.norm(data)
    return max(np.abs(data)) if len(data) > 0  else np.float64(0.)


def entropy(A, alpha=1, tol=1e-12):
    """ von Neuman or Renyi entropy from svd's"""
    Snorm = np.sqrt(np.sum([np.sum(x ** 2) for x in A.values()]))
    if Snorm > 0:
        Smin = min([min(x) for x in A.values()])
        ent = []
        for x in A.values():
            x = x / Snorm
            x = x[x > tol]
            if alpha == 1:
                ent.append(-2 * np.sum(x * x * np.log2(x)))
            else:
                ent.append(np.sum(x**(2 * alpha)))
        ent = np.sum(ent)
        if alpha != 1:
            ent = np.log2(ent) / (1 - alpha)
        return ent, Smin, Snorm
    return Snorm, Snorm, Snorm  # this should be 0., 0., 0.


##########################
#     setting values     #
##########################


def dtype_scalar(x, dtype='float64', **kwargs):
    return DTYPE[dtype](x)


def zeros(D, dtype='float64', **kwargs):
    return np.zeros(D, dtype=DTYPE[dtype])


def ones(D, dtype='float64', **kwargs):
    return np.ones(D, dtype=DTYPE[dtype])


def randR(D, **kwargs):
    return 2 * rng['rng'].random(D) - 1


def randC(D, **kwargs):
    return 2 * (rng['rng'].random(D) + 1j *  rng['rng'].random(D)) - (1 + 1j)


def to_tensor(val, Ds=None, dtype='float64', **kwargs):
    # try:
    T = np.array(val, dtype=DTYPE[dtype])
    # except TypeError:
    #     T = np.array(val, dtype=DTYPE['complex128'])
    return T if Ds is None else T.reshape(Ds)


def to_mask(val):
    return val.nonzero()[0].ravel()


def square_matrix_from_dict(H, D=None, **kwargs):
    dtype = np.common_type(*tuple(H.values()))
    T = np.zeros((D, D), dtype=dtype)
    for (i, j), v in H.items():
        if i < D and j < D:
            T[i, j] = v
    return T


def requires_grad_(data, requires_grad=True):
    warnings.warn("backend_np does not support autograd.", Warning)
    pass


def requires_grad(data):
    return False


def move_to(data, *args, **kwargs):
    return data


def conj(data):
    return data.conj()


def trace(data, order, meta, Dsize):
    """ Trace dict of tensors according to meta = [(tnew, told, Dreshape), ...].
        Repeating tnew are added."""
    newdata = np.zeros((Dsize,), dtype=data.dtype)
    for (sln, slo, Do, Drsh) in meta:
        newdata[slice(*sln)] += np.trace(data[slice(*slo)].reshape(Do).transpose(order).reshape(Drsh)).ravel()
    return newdata


def trace_with_mask(data, order, meta, Dsize, tcon, msk12):
    """ Trace dict of tensors according to meta = [(tnew, told, Dreshape), ...].
        Repeating tnew are added."""
    newdata = np.zeros((Dsize,), dtype=data.dtype)
    for (sln, slo, Do, Drsh), tt in zip(meta, tcon):
        temp = data[slice(*slo)].reshape(Do).transpose(order).reshape(Drsh)
        newdata[slice(*sln)] += np.sum(temp[msk12[tt][0], msk12[tt][1]], axis=0).ravel()
    return newdata


def transpose(data, axes, meta_transpose):
    newdata = np.zeros_like(data)
    for sln, slo, Do in meta_transpose:
        newdata[slice(*sln)] = data[slice(*slo)].reshape(Do).transpose(axes).ravel()
    return newdata


def rsqrt(data, cutoff=0):
    res = np.zeros_like(data)
    ind = np.abs(data) > cutoff
    res[ind] = 1. / np.sqrt(data[ind])
    return res


def reciprocal(data, cutoff=0):
    res = np.zeros_like(data)
    ind = np.abs(data) > cutoff
    res[ind] = 1. / data[ind]
    return res


def exp(data, step):
    return np.exp(step * data)


def sqrt(data):
    return np.sqrt(data)


def absolute(data):
    return np.abs(data)


def svd_lowrank(A, meta, D_block, n_iter=60, k_fac=6):
    U, S, V = {}, {}, {}
    for (iold, iU, iS, iV) in meta:
        k = min(min(A[iold].shape), D_block)
        U[iU], S[iS], V[iV] = fbpca.pca(A[iold], k=k, raw=True, n_iter=n_iter, l=k_fac * k)
    return U, S, V


def svd(A, meta):
    U, S, V = {}, {}, {}
    for (iold, iU, iS, iV) in meta:
        try:
            U[iU], S[iS], V[iV] = scipy.linalg.svd(A[iold], full_matrices=False)
        except scipy.linalg.LinAlgError:  # pragma: no cover
            U[iU], S[iS], V[iV] = scipy.linalg.svd(A[iold], full_matrices=False, lapack_driver='gesvd')
    return U, S, V


def eigh(A, meta=None):
    S, U = {}, {}
    if meta is not None:
        for (ind, indS, indU) in meta:
            S[indS], U[indU] = np.linalg.eigh(A[ind])
    else:
        S, U = np.linalg.eigh(A)
    return S, U


def svd_S(A):
    S = {}
    for ind in A:
        try:
            S[ind] = scipy.linalg.svd(A[ind], full_matrices=False, compute_uv=False)
        except scipy.linalg.LinAlgError:  # pragma: no cover
            S[ind] = scipy.linalg.svd(A[ind], full_matrices=False, lapack_driver='gesvd', compute_uv=False)
    return S


def qr(A, meta):
    Q, R = {}, {}
    for (ind, indQ, indR) in meta:
        Q[indQ], R[indR] = scipy.linalg.qr(A[ind], mode='economic')
        sR = np.sign(np.real(np.diag(R[indR])))
        sR[sR == 0] = 1
        # positive diag of R
        Q[indQ] = Q[indQ] * sR
        R[indR] = sR.reshape([-1, 1]) * R[indR]
    return Q, R


# def rq(A):
#     R, Q = {}, {}
#     for ind in A:
#         R[ind], Q[ind] = scipy.linalg.rq(A[ind], mode='economic')
#         sR = np.sign(np.real(np.diag(R[ind])))
#         sR[sR == 0] = 1
#         # positive diag of R
#         R[ind], Q[ind] = R[ind] * sR, sR.reshape([-1, 1]) * Q[ind]
#     return R, Q


def select_global_largest(S, D_keep, D_total, keep_multiplets, eps_multiplet, ordering):
    if ordering == 'svd':
        s_all = np.hstack([S[ind][:D_keep[ind]] for ind in S])
    elif ordering == 'eigh':
        s_all = np.hstack([S[ind][-D_keep[ind]:] for ind in S])
    Darg = D_total + int(keep_multiplets)
    order = s_all.argsort()[-1:-Darg-1:-1]
    if keep_multiplets:  # if needed, preserve multiplets within each sector
        s_all = s_all[order]
        gaps = np.abs(s_all)
        # compute gaps and normalize by larger singular value. Introduce cutoff
        gaps = np.abs(gaps[:len(s_all) - 1] - gaps[1:len(s_all)]) / gaps[0]  # / (gaps[:len(values) - 1] + 1.0e-16)
        gaps[gaps > 1.0] = 0.  # for handling vanishing values set to exact zero
        if gaps[D_total - 1] < eps_multiplet:
            # the chi is within the multiplet - find the largest chi_new < chi
            # such that the complete multiplets are preserved
            for i in range(D_total - 1, -1, -1):
                if gaps[i] > eps_multiplet:
                    order = order[:i + 1]
                    break
    return order


def eigs_which(val, which):
    if which == 'LM':
        return (-abs(val)).argsort()
    if which == 'SM':
        return abs(val).argsort()
    if which == 'LR':
        return (-val.real).argsort()
    # elif which == 'SR':
    return (val.real).argsort()


def range_largest(D_keep, D_total, ordering):
    if ordering == 'svd':
        return (0, D_keep)
    if ordering == 'eigh':
        return (D_total - D_keep, D_total)


def maximum(A):
    """ maximal element of A """
    return max(np.max(x) for x in A.values())


def embed_msk(data, msk, Dsize):
    newdata = np.zeros((Dsize,), dtype=data.dtype)
    newdata[msk] = data
    return newdata

def embed_slc(data, meta, Dsize):
    newdata = np.zeros((Dsize,), dtype=data.dtype)
    for sln, slo in meta:
        newdata[slice(*sln)] = data[slice(*slo)]
    return newdata


################################
#     two dicts operations     #
################################


def add(Adata, Bdata, meta, Dsize):
    newdata = np.zeros((Dsize,), dtype=np.common_type(Adata, Bdata))
    for sl_c, sl_a, sl_b, ab in meta:
        if ab == 'AB':
            newdata[slice(*sl_c)] = Adata[slice(*sl_a)] + Bdata[slice(*sl_b)]
        elif ab == 'A':
            newdata[slice(*sl_c)] = Adata[slice(*sl_a)]
        else:  # ab == 'B'
            newdata[slice(*sl_c)] = Bdata[slice(*sl_b)]
    return newdata


def sub(Adata, Bdata, meta, Dsize):
    newdata = np.zeros((Dsize,), dtype=np.common_type(Adata, Bdata))
    for sl_c, sl_a, sl_b, ab in meta:
        if ab == 'AB':
            newdata[slice(*sl_c)] = Adata[slice(*sl_a)] - Bdata[slice(*sl_b)]
        elif ab == 'A':
            newdata[slice(*sl_c)] = Adata[slice(*sl_a)]
        else:  # ab == 'B'
            newdata[slice(*sl_c)] = -Bdata[slice(*sl_b)]
    return newdata


def apxb(Adata, Bdata, x, meta, Dsize):
    newdata = np.zeros((Dsize,), dtype=np.common_type(Adata, Bdata))
    for sl_c, sl_a, sl_b, ab in meta:
        if ab == 'AB':
            newdata[slice(*sl_c)] = Adata[slice(*sl_a)] + x * Bdata[slice(*sl_b)]
        elif ab == 'A':
            newdata[slice(*sl_c)] = Adata[slice(*sl_a)]
        else:  # ab == 'B'
            newdata[slice(*sl_c)] = x * Bdata[slice(*sl_b)]
    return newdata


dot_dict = {(0, 0): lambda x, y: x @ y,
            (0, 1): lambda x, y: x @ y.conj(),
            (1, 0): lambda x, y: x.conj() @ y,
            (1, 1): lambda x, y: x.conj() @ y.conj()}


def apply_slice(data, slcn, slco):
    Dsize = slcn[-1][1] if len(slcn) > 0 else 0
    newdata = np.zeros((Dsize,), dtype=data.dtype)
    for sn, so in zip(slcn, slco):
        newdata[slice(*sn)] = data[slice(*so)]
    return newdata


def vdot(Adata, Bdata, cc):
    f = dot_dict[cc]  # proper conjugations
    return f(Adata, Bdata)


def diag_1dto2d(Adata, meta, Dsize):
    newdata = np.zeros((Dsize,), dtype=Adata.dtype)
    for sln, slo in meta:
        newdata[slice(*sln)] = np.diag(Adata[slice(*slo)]).ravel()
    return newdata


def diag_2dto1d(Adata, meta, Dsize):
    newdata = np.zeros((Dsize,), dtype=Adata.dtype)
    for sln, slo, Do in meta:
        newdata[slice(*sln)] = np.diag(Adata[slice(*slo)].reshape(Do))
    return newdata


def dot(A, B, cc, meta_dot):
    f = dot_dict[cc]  # proper conjugations
    C = {}
    for (out, ina, inb) in meta_dot:
        C[out] = f(A[ina], B[inb])
    return C


dotdiag_dict = {(0, 0): lambda x, y, dim: x * y.reshape(dim),
                (0, 1): lambda x, y, dim: x * y.reshape(dim).conj(),
                (1, 0): lambda x, y, dim: x.conj() * y.reshape(dim),
                (1, 1): lambda x, y, dim: x.conj() * y.reshape(dim).conj()}


def dot_diag(Adata, Bdata, cc, meta, Dsize, axis, a_ndim):
    dim = [1] * a_ndim
    dim[axis] = -1
    f = dotdiag_dict[cc]
    newdata = np.zeros((Dsize,), dtype=np.common_type(Adata, Bdata))
    for sln, sla, Da, slb in meta:
        newdata[slice(*sln)] = f(Adata[slice(*sla)].reshape(Da), Bdata[slice(*slb)], dim).ravel()
    return newdata


def mask_diag(Adata, Bdata, meta, Dsize, axis, a_ndim):
    slc1 = (slice(None),) * axis
    slc2 = (slice(None),) * (a_ndim - (axis + 1))
    newdata = np.zeros((Dsize,), dtype=Adata.dtype)
    for sln, sla, Da, slb in meta:
        cut = Bdata[slice(*slb)].nonzero()
        newdata[slice(*sln)] = Adata[slice(*sla)].reshape(Da)[slc1 + cut + slc2].ravel()
    return newdata


def dot_nomerge(Adata, Bdata, cc, oA, oB, meta, Dsize):
    f = dot_dict[cc]  # proper conjugations
    newdata = np.zeros((Dsize,), dtype=np.common_type(Adata, Bdata))
    for (sln, sla, Dao, Dan, slb, Dbo, Dbn) in meta:
        newdata[slice(*sln)] += f(Adata[slice(*sla)].reshape(Dao).transpose(oA).reshape(Dan), \
                                  Bdata[slice(*slb)].reshape(Dbo).transpose(oB).reshape(Dbn)).ravel()
    return newdata


def dot_nomerge_masks(Adata, Bdata, cc, oA, oB, meta, Dsize, tcon, ma, mb):
    f = dot_dict[cc]  # proper conjugations
    newdata = np.zeros((Dsize,), dtype=np.common_type(Adata, Bdata))
    for (sln, sla, Dao, Dan, slb, Dbo, Dbn), tt in zip(meta, tcon):
        newdata[slice(*sln)] += f(Adata[slice(*sla)].reshape(Dao).transpose(oA).reshape(Dan)[:, ma[tt]], \
                                  Bdata[slice(*slb)].reshape(Dbo).transpose(oB).reshape(Dbn)[mb[tt], :]).ravel()
    return newdata
#####################################################
#     block merging, truncations and un-merging     #
#####################################################


def merge_to_2d(data, order, meta_new, meta_mrg, *args, **kwargs):
    Anew = {u: np.zeros(Du, dtype=data.dtype) for u, Du in zip(*meta_new)}
    for (tn, slo, Do, Dslc, Drsh) in meta_mrg:
        Anew[tn][tuple(slice(*x) for x in Dslc)] = data[slice(*slo)].reshape(Do).transpose(order).reshape(Drsh)
    return Anew


def merge_to_1d(data, order, meta_new, meta_mrg, Dsize, *args, **kwargs):
    newdata = np.zeros((Dsize,), dtype=data.dtype)
    for (tn, Dn, sln), (t1, gr) in zip(zip(*meta_new), groupby(meta_mrg, key=lambda x: x[0])):
        assert tn == t1
        temp = np.zeros(Dn, dtype=data.dtype)
        for (_, slo, Do, Dslc, Drsh) in gr:
            temp[tuple(slice(*x) for x in Dslc)] = data[slice(*slo)].reshape(Do).transpose(order).reshape(Drsh)
        newdata[slice(*sln)] = temp.ravel()
    return newdata


def merge_to_dense(data, Dtot, meta, *args, **kwargs):
    newdata = np.zeros(Dtot, dtype=data.dtype)
    for (sl, Dss) in meta:
        newdata[tuple(slice(*Ds) for Ds in Dss)] = data[sl].reshape(tuple(Ds[1] - Ds[0] for Ds in Dss))
    return newdata.ravel()


def merge_super_blocks(pos_tens, meta_new, meta_block, Dsize):
    dtype = np.common_type(*list(a._data for a in pos_tens.values()))
    newdata = np.zeros((Dsize,), dtype=dtype)
    for (tn, Dn, sln), (t1, gr) in zip(meta_new, groupby(meta_block, key=lambda x: x[0])):
        assert tn == t1
        temp = np.zeros(Dn, dtype=dtype)
        for (_, slo, Do, pos, Dslc) in gr:
            slc = tuple(slice(*x) for x in Dslc)
            temp[slc] = pos_tens[pos]._data[slice(*slo)].reshape(Do)
        newdata[slice(*sln)] = temp.ravel()
    return newdata


def unmerge_from_2d(A, meta, new_sl, Dsize, *args, **kwargs):
    dtype = next(iter(A.values())).dtype if len(A) > 0 else np.float64
    newdata = np.zeros((Dsize,), dtype=dtype)
    for (indm, sl, sr), snew in zip(meta, new_sl):
        newdata[slice(*snew)] = A[indm][slice(*sl), slice(*sr)].ravel()
    return newdata


def unmerge_from_2ddiag(A, meta, new_sl, Dsize, *args, **kwargs):
    dtype = next(iter(A.values())).dtype if len(A) > 0 else np.float64
    newdata = np.zeros((Dsize,), dtype=dtype)
    for (_, iold, slc), snew in zip(meta, new_sl):
        newdata[slice(*snew)] = A[iold][slice(*slc)]
    return newdata


def unmerge_from_1d(data, meta, new_sl, Dsize):
    newdata = np.zeros((Dsize,), dtype=data.dtype)
    for (slo, Do, sub_slc), snew in zip(meta, new_sl):
        newdata[slice(*snew)] = data[slice(*slo)].reshape(Do)[tuple(slice(*x) for x in sub_slc)].ravel()
    return newdata


#############
#   tests   #
#############


def is_complex(x):
    return np.iscomplexobj(x)


def is_independent(x, y):
    """
    check if two arrays are identical, or share the same view.
    """ 
    return not ((x is y) or (x.base is y) or (x is y.base))
