""" examples for addition of the Mps-s """
import pytest
import yastn.tn.mps as mps
import yastn
try:
    from .configs import config_dense as cfg
    # pytest modifies cfg to inject different backends and devices during tests
except ImportError:
    from configs import config_dense as cfg

tol = 1e-8

def check_add(psi0, psi1):
    """ series of test of mps.add performed on provided psi0 and psi1"""
    out1 = mps.add(psi0, psi1, amplitudes=[1., 2.])
    out2 = (1.0 * psi0) + (2.0 * psi1)
    p0 = mps.measure_overlap(psi0, psi0)
    p1 = mps.measure_overlap(psi1, psi1)
    p01 = mps.measure_overlap(psi0, psi1)
    p10 = mps.measure_overlap(psi1, psi0)
    for out in (out1, out2):
        o1 = mps.measure_overlap(out, out)
        assert abs(o1 - p0 - 4 * p1 - 2 * p01 - 2 * p10) < tol


def test_addition_basic():
    import yastn.tn.mps as mps
    import yastn

    # Define random MPS's without any symmetry
    #
    config_dense = yastn.make_config()
    psi0 = mps.random_dense_mps(N=8, D=5, d=2)
    psi1 = mps.random_dense_mps(N=8, D=5, d=2)
     
    # We want to calculate: res = psi0 + 2 * psi1. There is a couple of ways:
    # A/
    resA = mps.add(psi0, 2.0 * psi1)
     
    # B/
    resB = mps.add(psi0, psi1, amplitudes=[1.0, 2.0])
     
    # C/
    resC = psi0 + 2.0 * psi1

    nresA, nresB, nresC = resA.norm(), resB.norm(), resC.norm()
    assert abs(mps.vdot(resA, resB) / (nresA * nresB) - 1) < tol
    assert abs(mps.vdot(resA, resC) / (nresA * nresC) - 1) < tol


def test_addition():
    """Create two Mps-s and add them to each other."""

    operators = yastn.operators.SpinfulFermions(sym='U1xU1', backend=cfg.backend, default_device=cfg.default_device)
    generate = mps.Generator(N=9, operators=operators)

    psi0 = generate.random_mps(D_total=15, n=(3, 5))
    psi1 = generate.random_mps(D_total=19, n=(3, 5))
    check_add(psi0, psi1)

    psi0 = generate.random_mpo(D_total=12)
    psi1 = generate.random_mpo(D_total=11)
    check_add(psi0, psi1)


def test_multiplication():
    # Calculate ground state and checks mps.multiply(), __mul__() and mps.zipper()
    # and mps.add() within eigen-condition.
    #
    # This test presents a multiplication as a part of DMRG study. 
    # We use multiplication to get expectation values from a state.
    # Knowing exact solution we will compare it to the value we obtain.
    N = 7
    Eng = -3.427339492125848
    #
    operators = yastn.operators.SpinlessFermions(sym='U1', backend=cfg.backend, default_device=cfg.default_device)
    generate = mps.Generator(N=N, operators=operators)
    #
    # The Hamiltonian is obtained with automatic generator (see source file).
    #
    parameters = {"t": 1.0, "mu": 0.2, "rangeN": range(N), "rangeNN": zip(range(N-1),range(1,N))}
    H_str = "\sum_{i,j \in rangeNN} t ( cp_{i} c_{j} + cp_{j} c_{i} ) + \sum_{j\in rangeN} mu cp_{j} c_{j}"
    H = generate.mpo_from_latex(H_str, parameters)
    #
    # To standardize this test we will fix a seed for random MPS we use.
    #
    generate.random_seed(seed=0)
    #
    # In this example we use yastn.Tensor's with U(1) symmetry. 
    #
    total_charge = 3
    psi = generate.random_mps(D_total=8, n=total_charge)
    #
    # We set truncation for DMRG and run the algorithm in '2site' version.
    #
    opts_svd = {'D_total': 8} 
    out = mps.dmrg_(psi, H, method='2site', max_sweeps=20, Schmidt_tol=1e-14, opts_svd=opts_svd)
    out = mps.dmrg_(psi, H, method='1site', max_sweeps=20, Schmidt_tol=1e-14)
    #
    # Test if we obtained exact solution for the energy?:
    #
    assert pytest.approx(out.energy.item(), rel=tol) == Eng
    #
    # If the code didn't break then we should get a ground state.
    # Now we calculate the variation of energy <H^2>-<H>^2=<(H-Eng)^2>
    # to check if DMRG converged properly to tol.
    # We have two equivalent ways to do that:
    # (case 2 and 3 are not most efficient - we use them here for testing)
    #
    # case 1/
    print(psi.get_bond_charges_dimensions())
    Hpsi = mps.zipper(H, psi, opts={"D_total": 8})
    mps.compression_(Hpsi, (H, psi), method='2site', max_sweeps=5, Schmidt_tol=1e-6, opts_svd={"D_total": 8}, normalize=False)
    print(Hpsi.get_bond_charges_dimensions())
    #
    # Use mps.norm() to get variation. 
    # Norm canonizes copy of the state and, close to zero, is more precise than vdot.
    #
    p0 = Eng * psi - Hpsi
    assert p0.norm() < tol
    #
    # case 2/
    Hpsi = mps.multiply(H, psi)
    p0 = Eng * psi - Hpsi
    assert p0.norm() < tol
    #
    # case 3/
    Hpsi = H @ psi
    p0 = Eng * psi - Hpsi
    assert p0.norm() < tol


if __name__ == "__main__":
    test_addition()
    test_addition_basic()
    test_multiplication()
