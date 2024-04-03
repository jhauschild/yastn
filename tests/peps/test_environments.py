""" Test the expectation values of spinless fermions with analytical values of fermi sea for finite and infinite lattices """
import numpy as np
import yastn
import yastn.tn.fpeps as fpeps
import yastn.tn.mps as mps

try:
    from .configs import config_U1xU1_R_fermionic as cfg
    # cfg is used by pytest to inject different backends and divices
except ImportError:
    from configs import config_U1xU1_R_fermionic as cfg


def test_finite_spinless_boundary_mps_ctmrg():

    boundary = 'obc'
    Nx, Ny = 3, 2
    geometry = fpeps.SquareLattice(dims=(Nx, Ny), boundary=boundary)

    mu = 0  # chemical potential
    t = 1  # hopping amplitude
    beta = 0.2
    dbeta = 0.025

    D = 6

    ops = yastn.operators.SpinlessFermions(sym='U1', backend=cfg.backend, default_device=cfg.default_device)
    fid, fc, fcdag = ops.I(), ops.c(), ops.cp()

    g_hop = fpeps.gates.gate_nn_hopping(t, dbeta / 2, fid, fc, fcdag)  # nn gate for 2D fermi sea
    gates = fpeps.gates_homogeneous(geometry, gates_nn=g_hop)

    psi = fpeps.product_peps(geometry, fid) # initialized at infinite temperature
    env = fpeps.EnvNTU(psi, which='NN+')

    opts_svd = {'D_total': D, 'tol_block': 1e-15}
    steps = round((beta / 2) / dbeta)
    for step in range(steps):
        print(f"beta = {(step + 1) * dbeta:0.3f}" )
        fpeps.evolution_step_(env, gates, opts_svd=opts_svd, initialization="EAT")


    # convergence criteria for CTM based on total energy
    energy_old, tol_exp = 0, 1e-7

    env = fpeps.EnvCTM(psi)
    opts_svd_ctm = {'D_total': 30, 'tol': 1e-10}
    for step in fpeps.ctmrg_(env, max_sweeps=50, iterator_step=1, opts_svd=opts_svd_ctm):
        cdagc = env.measure_nn(fcdag, fc)
        energy = -2 * np.mean([*cdagc.values()])

        print("energy: ", energy)
        if abs(energy - energy_old) < tol_exp:
            break
        energy_old = energy

    mpsenv = fpeps.EnvBoundaryMps(psi, opts_svd=opts_svd_ctm, setup='tlbr')

    for ny in range(psi.Ny):
        vR0 = step.env.boundary_mps(n=ny, dirn='r')
        vR1 = mpsenv.boundary_mps(n=ny, dirn='r')
        vL0 = step.env.boundary_mps(n=ny, dirn='l')
        vL1 = mpsenv.boundary_mps(n=ny, dirn='l')

        print(mps.vdot(vR0, vR1) / (vR0.norm() * vR1.norm()))  # problem with phase in peps?
        print(mps.vdot(vL0, vL1) / (vL0.norm() * vL1.norm()))
        assert abs(abs(mps.vdot(vR0, vR1)) / (vR0.norm() * vR1.norm()) - 1) < 1e-7
        assert abs(abs(mps.vdot(vL0, vL1)) / (vL0.norm() * vL1.norm()) - 1) < 1e-7

    for nx in range(psi.Nx):
        vT0 = step.env.boundary_mps(n=nx, dirn='t')
        vT1 = mpsenv.boundary_mps(n=nx, dirn='t')
        vB0 = step.env.boundary_mps(n=nx, dirn='b')
        vB1 = mpsenv.boundary_mps(n=nx, dirn='b')

        print(mps.vdot(vT0, vT1) / (vT0.norm() * vT1.norm()))  # problem with phase in peps?
        print(mps.vdot(vB0, vB1) / (vB0.norm() * vB1.norm()))
        assert abs(abs(mps.vdot(vT0, vT1)) / (vT0.norm() * vT1.norm()) - 1) < 1e-7
        assert abs(abs(mps.vdot(vB0, vB1)) / (vB0.norm() * vB1.norm()) - 1) < 1e-7


def test_spinless_infinite_approx():
    """ Simulate purification of free fermions in an infinite system.s """
    geometry = fpeps.SquareLattice(dims=(3, 3), boundary='infinite')

    mu, t, beta = 0, 1, 0.5  # chemical potential
    D = 6
    dbeta = 0.05

    ops = yastn.operators.SpinlessFermions(sym='U1', backend=cfg.backend, default_device=cfg.default_device)
    fid, fc, fcdag = ops.I(), ops.c(), ops.cp()
    g_hop = fpeps.gates.gate_nn_hopping(t, dbeta / 2, fid, fc, fcdag)  # nn gate for 2D fermi sea
    gates = fpeps.gates_homogeneous(geometry, gates_nn=g_hop)

    psi = fpeps.product_peps(geometry, fid) # initialized at infinite temperature
    env = fpeps.EnvNTU(psi, which='NN+')

    opts_svd = {"D_total": D , 'tol_block': 1e-15}
    steps = round((beta / 2) / dbeta)
    for step in range(steps):
        print(f"beta = {(step + 1) * dbeta:0.3f}" )
        fpeps.evolution_step_(env, gates, opts_svd=opts_svd, initialization="SVD")

    opts_svd = {"D_total": 2 * D, 'tol_block': 1e-15}

    envs = {}
    for k in ['NN', 'NN+', 'NN++', 'NNN', 'NNN+', 'NNN++']:
        envs[k] = fpeps.EnvNTU(psi, which=k)

    for k in ['43', '43h', '65', '65h', '87', '87h']:
        envs[k] = fpeps.EnvApproximate(psi,
                                       which=k,
                                       opts_svd=opts_svd,
                                       update_sweeps=1)

    for st0, st1 in [[(0, 0), (0, 1)], [(0, 1), (1, 1)]]:
        bd = fpeps.Bond(st0, st1)
        QA, QB = psi[st0], psi[st1]
        Gs = {k: env.bond_metric(bd, QA, QB) for k, env in envs.items()}
        Gs = {k: v / v.norm() for k, v in Gs.items()}
        assert (Gs['NN'] - Gs['NN+']).norm() < 2e-3
        assert (Gs['NN+'] - Gs['NN++']).norm() < 1e-4
        assert (Gs['NN++'] - Gs['NNN++']).norm() < 1e-3
        assert (Gs['NNN'] - Gs['43']).norm() < 1e-6
        assert (Gs['NNN+'] - Gs['43h']).norm() < 1e-6
        assert (Gs['NNN+'] - Gs['NNN+']).norm() < 1e-4
        assert (Gs['43'] - Gs['43h']).norm() < 1e-3
        assert (Gs['43h'] - Gs['65']).norm() < 1e-4
        assert (Gs['65'] - Gs['65h']).norm() < 1e-5
        assert (Gs['65h'] - Gs['87']).norm() < 1e-6
        assert (Gs['87'] - Gs['87h']).norm() < 1e-6

        Gs2 = {k: envs[k].bond_metric(bd, QA, QB)
               for k in ['43', '43h', '65', '65h', '87', '87h']}
        Gs2 = {k: v / v.norm() for k, v in Gs2.items()}
        for k in Gs2:
            assert 1e-15 < (Gs[k] - Gs2[k]).norm() < 1e-10


if __name__ == '__main__':
    test_finite_spinless_boundary_mps_ctmrg()
    test_spinless_infinite_approx()
