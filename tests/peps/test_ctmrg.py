""" ctmrg test on 2D Classical Ising model with CTMRG  """
""" Tests the expectation values with CTM using analytical dense psi tensors (upto numerical presisions) for 2D Ising model with 0 transverse field (Onsager solution) """
import logging
import numpy as np
import pytest
import yast
from yast import ncon, tensordot
import yast.tn.peps as peps
from yast.tn.peps.ctm import nn_avg, ctmrg_, init_rand

try:
    from .configs import config_dense as cfg
    # cfg is used by pytest to inject different backends and divices
except ImportError:
    from configs import config_dense as cfg

opt = yast.operators.Spin12(sym='dense', backend=cfg.backend, default_device=cfg.default_device)
sz, id = opt.z(), opt.I()
net = peps.Peps(lattice='checkerboard', boundary='infinite')


def create_ZZ_ten(sz, betas):
    """ Creates the psi tensor for a certain beta. """
    L = ncon((sz, sz), ((-0, -1), (-2, -3)))
    L = L.fuse_legs(axes = ((0, 2), (1, 3)))
    D, S = yast.eigh(L, axes = (0, 1))
    D = yast.exp(D, step=0.5*betas) 
    U = yast.ncon((S, D, S), ([-1, 1], [1, 2], [-3, 2]), conjs=(0, 0, 1))
    U = U.unfuse_legs(axes=(0, 1))
    U = U.transpose(axes=(0, 2, 1, 3))
    U, S, V = yast.svd_with_truncation(U, axes = ((0, 1), (2, 3)), sU = -1, tol = 1e-15, Uaxis=1, Vaxis=1)
    S = S.sqrt()
    GA = S.broadcast(U, axis=1)
    GB = S.broadcast(V, axis=1)

    T = yast.tensordot(GA, GB, axes=(2, 0))
    T = yast.tensordot(T, GB, axes=(3, 0))
    T = yast.tensordot(T, GA, axes=(4, 0))
    T = T.fuse_legs(axes=(1, 2, 3, 4, (0, 5)))

    return T


def matrix_inverse_random():
    """ Returns a n*n random matrix and its inverse """

    ss = (1,-1)
    a = yast.rand(config=cfg, s=ss, D=(2, 2))
    inv_tu = np.linalg.inv(a.to_numpy())
    b = yast.Tensor(config=cfg, s=ss)
    b.set_block(val=inv_tu, Ds=(2, 2))

    return a, b

def CTM_for_Onsager(psi, Z_exact):
    """ Asserts CTM expectation values with analytical values. """
    """ Convergence criteria based on energy """

    chi = 40 # max environmental bond dimension
    cutoff = 1e-10 # 
    tol=1e-7
    max_sweeps = 400
    
    cf_old = 0

    for step in ctmrg_(psi, chi, cutoff, max_sweeps, iterator_step=2, AAb_mode=0):
        assert step.sweeps % 2 == 0 # stop every 2nd step as iteration_step=2
        ops = {'magA1': {'l': sz, 'r': id},
           'magB1': {'l': id, 'r': sz}}

        ob_hor, ob_ver =  nn_avg(psi, step.env, ops)
        cf = 0.25 * (abs(ob_hor.get('magA1')) + abs(ob_hor.get('magB1')) +  abs(ob_ver.get('magA1'))+abs(ob_ver.get('magB1')))
        print("expectation value: ", cf)
        if abs(cf - cf_old) < tol:
            break # here break if the relative differnece is below tolerance
        cf_old = cf

    assert pytest.approx(cf, rel=1e-3) == Z_exact

    ops = {'magA1': {'l': sz, 'r': id},
           'magB1': {'l': id, 'r': sz}}
    ob_hor, ob_ver =  nn_avg(psi, step.env, ops)    
    cf = 0.25 * (abs(ob_hor.get('magA1')) + abs(ob_hor.get('magB1')) +  abs(ob_ver.get('magA1'))+abs(ob_ver.get('magB1')))
    print("expectation value: ", cf)
        
    assert pytest.approx(cf, rel=1e-3) == Z_exact


def test_CTM_loop_1():
    """ Calculate magnetization for classical 2D Ising model and compares with the exact result. """
    beta = 0.7  # check for a certain inverse temperature
    Z_exact = 0.99016253867 # analytical value of magnetization up to 4 decimal places for beta = 0.8 (2D Classical Ising)
    psi = peps.Peps(net.lattice, net.dims, net.boundary)

    for ms in psi.sites():
        psi[ms] = create_ZZ_ten(sz, beta) 
    CTM_for_Onsager(psi, Z_exact)


def not_working_test_CTM_loop_2():
    """ Calculate magnetization for classical 2D Ising model and compares with the exact result. """
    beta = 0.7 # check for a ceratin inverse temperature
    Z_exact = 0.99016253867 # analytical value of magnetization up to 4 decimal places for beta = 0.8 (2D Classical Ising)
    A = create_ZZ_ten(sz, beta)
    B = create_ZZ_ten(sz, beta)
    [h_rg1, inv_h_rg1] = matrix_inverse_random()
    [h_rg2, inv_h_rg2] = matrix_inverse_random()
    [v_rg1, inv_v_rg1] = matrix_inverse_random()
    [v_rg2, inv_v_rg2] = matrix_inverse_random()

    print(A.s)
    print(B.s)


    A = yast.ncon((A, h_rg1), ((-0, -1, -2, 1, -4), (1, -3)))
    A = yast.ncon((A, h_rg2), ((-0, 1, -2, -3, -4), (-1, 1)))
    A = yast.ncon((A, v_rg1), ((1, -1, -2, -3, -4), (1, -0)))
    A = yast.ncon((A, v_rg2), ((-0, -1, 1, -3, -4), (-2, 1)))

    B = yast.ncon((inv_h_rg1, B), ((-1, 1), (-0, 1, -2, -3, -4)))
    B = yast.ncon((inv_h_rg2, B), ((1, -3), (-0, -1, -2, 1, -4)))
    B = yast.ncon((inv_v_rg1, B), ((-2, 1), (-0, -1, 1, -3, -4)))
    B = yast.ncon((inv_v_rg2, B), ((1, -0), (1, -1, -2, -3, -4)))

    psi = peps.Peps(net.lattice, net.dims, net.boundary)

    print(A.s)
    print(B.s)

    psi[0,0] = A
    psi[0,1] = B
    # psi[1,0] = B
    # psi[1,1] = A

    CTM_for_Onsager(psi, Z_exact)


if __name__ == '__main__':
    logging.basicConfig(level='INFO')
    test_CTM_loop_1()
   # not_working_test_CTM_loop_2()

