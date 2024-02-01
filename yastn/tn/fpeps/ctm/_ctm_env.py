from typing import NamedTuple, Tuple
from itertools import accumulate
from dataclasses import dataclass
from ....tn import mps
from yastn.tn.fpeps import Peps
from yastn.tn.fpeps.gates._gates import match_ancilla_1s
from yastn import rand, tensordot, ones


class ctm_window(NamedTuple):
    """ elements of a 2x2 window for the CTM algorithm. """
    nw : tuple # north-west
    ne : tuple # north-east
    sw : Tuple # south-west
    se : Tuple # south-east


class CtmEnv(Peps):
    r""" Geometric information about the lattice provided to ctm tensors """
    def __init__(self, psi):
        super().__init__(psi.geometry)
        self.psi = psi

        windows = []
        for site in self.sites():
            win = [site]
            for d in ('r', 'b', 'br'):
                win.append(self.nn_site(site, d=d))
            if None not in win:
                windows.append(ctm_window(*win))
        self._windows = tuple(windows)

    def copy(self):
        env = CtmEnv(self)
        env._data = {k : v.copy() for k, v in self._data.items()}
        return env

    def tensors_CtmEnv(self):
        return self._windows

    def env2mps(self, n, dirn):
        """ Convert environmental tensors of Ctm to an MPS """
        if dirn == 'b':
            H = mps.Mps(N=self.Ny)
            for ny in range(self.Ny):
                H.A[ny] = self[n, ny].b.transpose(axes=(2,1,0))
            H = H.conj()
        elif dirn == 'r':
            H = mps.Mps(N=self.Nx)
            for nx in range(self.Nx):
                H.A[nx] = self[nx, n].r
        elif dirn == 't':
            H = mps.Mps(N=self.Ny)
            for ny in range(self.Ny):
                H.A[ny] = self[n, ny].t
        elif dirn == 'l':
            H = mps.Mps(N=self.Nx)
            for nx in range(self.Nx):
                H.A[nx] = self[nx, n].l.transpose(axes=(2,1,0))
            H = H.conj()
        return H


@dataclass()
class Local_Projector_Env(): # no more variables than the one given
    """ data class for projectors labelled by a single lattice site calculated during ctm renormalization step """

    hlt : any = None # horizontal left top
    hlb : any = None # horizontal left bottom
    hrt : any = None # horizontal right top
    hrb : any = None # horizontal right bottom
    vtl : any = None # vertical top left
    vtr : any = None # vertical top right
    vbl : any = None # vertical bottom left
    vbr : any = None # vertical bottom right

    def copy(self):
        return Local_Projector_Env(hlt=self.hlt, hlb=self.hlb, hrt=self.hrt, hrb=self.hrb, vtl=self.vtl, vtr=self.vtr, vbl=self.vbl, vbr=self.vbr)


@dataclass()
class Local_CTM_Env(): # no more variables than the one given
    """ data class for CTM environment tensors associated with each peps tensor """

    tl : any = None # top-left
    tr : any = None # top-right
    bl : any = None # bottom-left
    br : any = None # bottom-right
    t : any = None  # top
    b : any = None  # bottom
    l : any = None  # left
    r : any = None  # right

    def copy(self):
        return Local_CTM_Env(tl=self.tl, tr=self.tr, bl=self.bl, br=self.br, t=self.t, b=self.b, l=self.l, r=self.r)



def init_rand(A, tc, Dc):
    """ Initialize random CTMRG environments of peps tensors A. """

    config = A[(0,0)].config
    env= CtmEnv(A)

    for ms in A.sites():
        B = A[ms].copy()
        B = B.unfuse_legs(axes=(0,1))
        env[ms] = Local_CTM_Env()
        env[ms].tl = rand(config=config, s=(1, -1), t=(tc, tc), D=(Dc, Dc))
        env[ms].tr = rand(config=config, s=(1, -1), t=(tc, tc), D=(Dc, Dc))
        env[ms].bl = rand(config=config, s=(1, -1), t=(tc, tc), D=(Dc, Dc))
        env[ms].br = rand(config=config, s=(1, -1), t=(tc, tc), D=(Dc, Dc))
        legs = [env[ms].tl.get_legs(1).conj(),
                B.get_legs(0).conj(),
                B.get_legs(0),
                env[ms].tr.get_legs(0).conj()]
        env[ms].t = rand(config=config, legs=legs)
        legs = [env[ms].br.get_legs(1).conj(),
                B.get_legs(2).conj(),
                B.get_legs(2),
                env[ms].bl.get_legs(0).conj()]
        env[ms].b = rand(config=config, legs=legs)
        legs = [env[ms].bl.get_legs(1).conj(),
                B.get_legs(1).conj(),
                B.get_legs(1),
                env[ms].tl.get_legs(0).conj()]
        env[ms].l = rand(config=config, legs=legs)
        legs = [env[ms].tr.get_legs(1).conj(),
                B.get_legs(3).conj(),
                B.get_legs(3),
                env[ms].br.get_legs(0).conj()]
        env[ms].r = rand(config=config, legs=legs)
        env[ms].t = env[ms].t.fuse_legs(axes=(0, (1, 2), 3))
        env[ms].b = env[ms].b.fuse_legs(axes=(0, (1, 2), 3))
        env[ms].l = env[ms].l.fuse_legs(axes=(0, (1, 2), 3))
        env[ms].r = env[ms].r.fuse_legs(axes=(0, (1, 2), 3))

    return env


def init_ones(A):
    """ Initialize CTMRG environments of peps tensors A with trivial tensors. """

    config = A[(0,0)].config

    tc = ((0,) * config.sym.NSYM,)
    Dc = (1,)

    env= CtmEnv(A)

    for ms in A.sites():
        B = A[ms].copy()
        B = B.unfuse_legs(axes=(0,1))
        env[ms] = Local_CTM_Env()
        env[ms].tl = ones(config=config, s=(1, -1), t=(tc, tc), D=(Dc, Dc))
        env[ms].tr = ones(config=config, s=(1, -1), t=(tc, tc), D=(Dc, Dc))
        env[ms].bl = ones(config=config, s=(1, -1), t=(tc, tc), D=(Dc, Dc))
        env[ms].br = ones(config=config, s=(1, -1), t=(tc, tc), D=(Dc, Dc))
        legs = [env[ms].tl.get_legs(1).conj(),
                B.get_legs(0).conj(),
                B.get_legs(0),
                env[ms].tr.get_legs(0).conj()]
        env[ms].t = ones(config=config, legs=legs)
        legs = [env[ms].br.get_legs(1).conj(),
                B.get_legs(2).conj(),
                B.get_legs(2),
                env[ms].bl.get_legs(0).conj()]
        env[ms].b = ones(config=config, legs=legs)
        legs = [env[ms].bl.get_legs(1).conj(),
                B.get_legs(1).conj(),
                B.get_legs(1),
                env[ms].tl.get_legs(0).conj()]
        env[ms].l = ones(config=config, legs=legs)
        legs = [env[ms].tr.get_legs(1).conj(),
                B.get_legs(3).conj(),
                B.get_legs(3),
                env[ms].br.get_legs(0).conj()]
        env[ms].r = rand(config=config, legs=legs)
        env[ms].t = env[ms].t.fuse_legs(axes=(0, (1, 2), 3))
        env[ms].b = env[ms].b.fuse_legs(axes=(0, (1, 2), 3))
        env[ms].l = env[ms].l.fuse_legs(axes=(0, (1, 2), 3))
        env[ms].r = env[ms].r.fuse_legs(axes=(0, (1, 2), 3))

    return env

def sample(state, CTMenv, projectors, opts_svd=None, opts_var=None):
    """
    Sample a random configuration from a finite peps.

    Takes  CTM emvironments and a complete list of projectors to sample from.
    """

    config = state[0, 0].config
    rands = (config.backend.rand(state.Nx * state.Ny) + 1) / 2

    out = {}
    count = 0
    vR = CTMenv.env2mps(n=state.Ny-1, dirn='r') # right boundary of indexed column through CTM environment tensors

    for ny in range(state.Ny - 1, -1, -1):

        Os = state.transfer_mpo(n=ny, dirn='v') # converts ny colum of PEPS to MPO
        vL = CTMenv.env2mps(n=ny, dirn='l') # left boundary of indexed column through CTM environment tensors

        env = mps.Env3(vL, Os, vR).setup_(to = 'first')

        for nx in range(0, state.Nx):
            dpt = Os[nx].copy()
            loc_projectors = projectors[nx, ny] # [match_ancilla_1s(pr, dpt.A) for pr in projectors]
            prob = []
            norm_prob = env.measure(bd=(nx - 1, nx))
            for proj in loc_projectors:
                dpt_pr = dpt.copy()
                dpt_pr.A = tensordot(dpt_pr.A, proj, axes=(4, 1))
                Os[nx] = dpt_pr
                env.update_env_(nx, to='last')
                prob.append(env.measure(bd=(nx, nx+1)) / norm_prob)

            assert abs(sum(prob) - 1) < 1e-12
            rand = rands[count]
            ind = sum(apr < rand for apr in accumulate(prob))
            out[(nx, ny)] = ind
            dpt.A = tensordot(dpt.A, loc_projectors[ind], axes=(4, 1))
            Os[nx] = dpt               # updated with the new collapse
            env.update_env_(nx, to='last')
            count += 1

        if opts_svd is None:
            opts_svd = {'D_total': max(vL.get_bond_dimensions())}

        vRnew = mps.zipper(Os, vR, opts_svd=opts_svd)
        if opts_var is None:
            opts_var = {}

        mps.compression_(vRnew, (Os, vR), method='1site', **opts_var)
        vR = vRnew
    return out


def _clear_operator_input(op, sites):
    op_dict = op.copy() if isinstance(op, dict) else {site: op for site in sites}
    for k, v in op_dict.items():
        if isinstance(v, dict):
            op_dict[k] = {(i,): vi for i, vi in v.items()}
        elif isinstance(v, dict):
            op_dict[k] = {(): v}
        else: # is iterable
            op_dict[k] = {(i,): vi for i, vi in enumerate(v)}
    return op_dict


def measure_2site(state, CTMenv, op1, op2, opts_svd, opts_var=None):
    """
    Calculate all 2-point correlations <o1 o2> in a finite peps.

    Takes CTM emvironments and operators.

    o1 and o2 are given as dict[tuple[int, int], dict[int, operators]],
    mapping sites with list of operators at each site.
    """
    out = {}
    if opts_var is None:
        opts_var =  {'max_sweeps': 2}

    Nx, Ny = state.Nx, state.Ny
    sites = [(nx, ny) for ny in range(Ny-1, -1, -1) for nx in range(Nx)]
    op1dict = _clear_operator_input(op1, sites)
    op2dict = _clear_operator_input(op2, sites)

    for nx1, ny1 in sites:
        print( f"Correlations from {nx1} {ny1} ... ")
        for nz1, o1 in op1dict[nx1, ny1].items():
            vR = CTMenv.env2mps(n=ny1, dirn='r')
            vL = CTMenv.env2mps(n=ny1, dirn='l')
            Os = state.transfer_mpo(n=ny1, dirn='v')
            env = mps.Env3(vL, Os, vR).setup_(to='first').setup_(to='last')
            norm_env = env.measure(bd=(-1, 0))

            if ny1 > 0:
                vRnext = mps.zipper(Os, vR, opts_svd=opts_svd)
                mps.compression_(vRnext, (Os, vR), method='1site', normalize=False, **opts_var)

            # first calculate on-site correlations
            Osnx1A = Os[nx1].A
            for nz2, o2 in op2dict[nx1, ny1].items():
                loc_o = match_ancilla_1s(o1 @ o2, Osnx1A)
                Os[nx1].A = tensordot(Osnx1A, loc_o, axes=(4, 1))
                env.update_env_(nx1, to='last')
                out[(nx1, ny1) + nz1, (nx1, ny1) + nz2] = env.measure(bd=(nx1, nx1+1)) / norm_env

            loc_o1 = match_ancilla_1s(o1, Osnx1A)
            Os[nx1].A = tensordot(Osnx1A, loc_o1, axes=(4, 1))
            env.setup_(to='last')

            if ny1 > 0:
                vRo1next = mps.zipper(Os, vR, opts_svd=opts_svd)
                mps.compression_(vRo1next, (Os, vR), method='1site', normalize=False, **opts_var)

            # calculate correlations along the row
            for nx2 in range(nx1 + 1, Nx):
                Osnx2A = Os[nx2].A
                for nz2, o2 in op2dict[nx2, ny1].items():
                    loc_o2 = match_ancilla_1s(o2, Osnx2A)
                    Os[nx2].A = tensordot(Osnx2A, loc_o2, axes=(4, 1))
                    env.update_env_(nx2, to='first')
                    out[(nx1, ny1) + nz1, (nx2, ny1) + nz2] = env.measure(bd=(nx2-1, nx2)) / norm_env

            # and all subsequent rows
            for ny2 in range(ny1-1, -1, -1):
                vR = vRnext
                vRo1 = vRo1next
                vL = CTMenv.env2mps(n=ny2, dirn='l')
                Os = state.transfer_mpo(n=ny2, dirn='v')
                env = mps.Env3(vL, Os, vR).setup_(to='first')
                norm_env = env.measure(bd=(-1, 0))

                if ny2 > 0:
                    vRnext = mps.zipper(Os, vR, opts_svd=opts_svd)
                    mps.compression_(vRnext, (Os, vR), method='1site', normalize=False, **opts_var)
                    vRo1next = mps.zipper(Os, vRo1, opts_svd=opts_svd)
                    mps.compression_(vRo1next, (Os, vRo1), method='1site', normalize=False, **opts_var)

                env = mps.Env3(vL, Os, vRo1).setup_(to='first').setup_(to='last')
                for nx2 in range(state.Nx):
                    Osnx2A = Os[nx2].A
                    for nz2, o2 in op2dict[nx2, ny2].items():
                        loc_o2 = match_ancilla_1s(o2, Osnx2A)
                        Os[nx2].A = tensordot(Osnx2A, loc_o2, axes=(4, 1))
                        env.update_env_(nx2, to='first')
                        out[(nx1, ny1) + nz1, (nx2, ny2) + nz2] = env.measure(bd=(nx2-1, nx2)) / norm_env
    return out


def measure_1site(state, CTMenv, op):
    """
    Calculate all 1-point expectation values <o> in a finite peps.

    Takes CTM emvironments and operators.

    o1 are given as dict[tuple[int, int], dict[int, operators]],
    mapping sites with list of operators at each site.
    """
    out = {}

    Nx, Ny = state.Nx, state.Ny
    sites = [(nx, ny) for ny in range(Ny-1, -1, -1) for nx in range(Nx)]
    opdict = _clear_operator_input(op, sites)

    for ny in range(Ny-1, -1, -1):
        vR = CTMenv.env2mps(n=ny, dirn='r')
        vL = CTMenv.env2mps(n=ny, dirn='l')
        Os = state.transfer_mpo(n=ny, dirn='v')
        env = mps.Env3(vL, Os, vR).setup_(to='first').setup_(to='last')
        norm_env = env.measure()
        for nx in range(Nx):
            if (nx, ny) in opdict:
                Osnx1A = Os[nx].A
                for nz, o in opdict[nx, ny].items():
                    loc_o = match_ancilla_1s(o, Osnx1A)
                    Os[nx].A = tensordot(Osnx1A, loc_o, axes=(4, 1))
                    env.update_env_(nx, to='first')
                    out[(nx, ny) + nz] = env.measure(bd=(nx-1, nx)) / norm_env
    return out


def match_ancilla_projectors(psi, projectors):
    loc_proj = {}
    for k, proj in projectors.items():
        loc_proj[k] = [match_ancilla_1s(pr, psi[k]) for pr in proj]
    return loc_proj


def _sample_MC_column_local(ny, proj_psi, proj_env, st0, st1, psi, projectors, rands):
    # update is proposed based on local probabilies
    vR = proj_env.env2mps(n=ny, dirn='r')
    Os = proj_psi.transfer_mpo(n=ny, dirn='v', one_layer=True)
    vL = proj_env.env2mps(n=ny, dirn='l')
    env = mps.Env3(vL, Os, vR).setup_(to='first')
    for nx in range(psi.Nx):
        amp = env.hole(nx).tensordot(psi[nx, ny], axes=((0, 1, 2, 3), (0, 1, 2, 3)))
        prob = [abs(amp.vdot(pr, conj=(0, 0))) ** 2 for pr in projectors[nx, ny]]
        sumprob = sum(prob)
        prob = [x / sumprob for x in prob]
        rand = next(rands)
        ind = sum(x < rand for x in accumulate(prob))
        st1[nx, ny] = ind
        proj_psi[nx, ny] = tensordot(psi[nx, ny], projectors[nx, ny][ind], axes=(4, 0))
        Os[nx] = proj_psi[nx, ny]
        env.update_env_(nx, to='last')
    accept = psi.Nx
    return vR, Os, vL, accept


def _sample_MC_column_uniform(ny, proj_psi, proj_env, st0, st1, psi, projectors, rands):
    # update is proposed from uniform local distribution
    config = proj_psi[0, 0].config
    accept = 0
    vR = proj_env.env2mps(n=ny, dirn='r')
    Os = proj_psi.transfer_mpo(n=ny, dirn='v', one_layer=True)
    vL = proj_env.env2mps(n=ny, dirn='l')
    env = mps.Env3(vL, Os, vR).setup_(to='first')
    for nx in range(psi.Nx):
        A = psi[nx, ny]
        ind0 = st0[nx, ny]

        ind1 = config.backend.randint(0, len(projectors[nx, ny]))

        pr0 = projectors[nx, ny][ind0]
        pr1 = projectors[nx, ny][ind1]

        A0 = tensordot(A, pr0, axes=(4, 0))
        A1 = tensordot(A, pr1, axes=(4, 0))

        Os[nx] = A1
        env.update_env_(nx, to='last')
        prob_new = abs(env.measure(bd=(nx, nx+1))) ** 2

        Os[nx] = A0
        env.update_env_(nx, to='last')
        prob_old = abs(env.measure(bd=(nx, nx+1))) ** 2

        if next(rands) < prob_new / prob_old:  # accept
            accept += 1
            st1[nx, ny] = ind1
            proj_psi[nx, ny] = A1
            Os[nx] = A1
            env.update_env_(nx, to='last')
        else:  # reject
            st1[nx, ny] = ind0
    return vR, Os, vL, accept


def sample_MC_(proj_psi, proj_env, st0, st1, st2, psi, projectors, opts_svd, opts_var, trial="local"):
    """
    MC steps in a finite peps. Makes two steps
    while sweeping finite lattice back and forth.

    Takes emvironments and a complete list of projectors to sample from.

    proj_psi, proj_env, st1, st2 are updated in place
    """

    if trial == "local":
        _sample_MC_column = _sample_MC_column_local
    elif trial == "uniform":
        _sample_MC_column = _sample_MC_column_uniform
    else:
        raise ValueError(f"trial = {trial} not supported.")

    Nx, Ny = psi.Nx, psi.Ny
    config = psi[0, 0].config
    # pre-draw uniformly distributed random numbers as iterator;
    rands = iter((config.backend.rand(2 * Nx * Ny) + 1) / 2)  # in [0, 1]

    # sweep though the lattice
    accept = 0
    for ny in range(Ny-1, -1, -1):
        vR, Os, _, astep = _sample_MC_column(ny, proj_psi, proj_env, st0, st1, psi, projectors, rands)
        accept += astep
        if ny > 0:
            vRnew = mps.zipper(Os, vR, opts_svd=opts_svd)
            mps.compression_(vRnew, (Os, vR), method='1site', **opts_var)
            proj_env._env['r', ny-1] = vRnew
            proj_env._env.pop(('l', ny))

    for ny in range(Ny):
        _, Os, vL, astep = _sample_MC_column(ny, proj_psi, proj_env, st1, st2, psi, projectors, rands)
        accept += astep
        if ny < Ny - 1:
            OsT = Os.T.conj()
            vLnew = mps.zipper(OsT, vL, opts_svd=opts_svd)
            mps.compression_(vLnew, (OsT, vL), method='1site', **opts_var)
            proj_env._env['l', ny+1] = vLnew
            proj_env._env.pop(('r', ny))

    return accept / (2 * Nx * Ny)  # acceptance rate
