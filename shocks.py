# to code the shock condition . Mainly it will occcur at the inlet
# Normal Shock (M1>1, M2<1)

import math

def normal_shock(M1: float, gamma: float = 1.4):
    """
    Normal shock relations (perfect gas).
    Inputs:
        M1    : upstream Mach number (>1)
        gamma : specific heat ratio
    Returns dict with:
        M2, p2_p1, T2_T1, rho2_rho1, pt2_pt1, Tt2_Tt1(=1.0)
    """
    if M1 <= 1.0:
        raise ValueError("normal_shock: M1 must be > 1")

    g = gamma
    M1sq = M1 * M1

    # Static jumps
    p2_p1 = 1 + 2 * g / (g + 1) * (M1sq - 1)
    rho2_rho1 = ((g + 1) * M1sq) / (2 + (g - 1) * M1sq)
    T2_T1 = p2_p1 / rho2_rho1

    # Downstream Mach
    M2sq = (1 + 0.5 * (g - 1) * M1sq) / (g * M1sq - 0.5 * (g - 1))
    if M2sq <= 0:
        raise RuntimeError("normal_shock: computed negative M2^2 (check inputs).")
    M2 = math.sqrt(M2sq)

    # Stagnation (total) property changes
    # Tt is constant across an adiabatic shock with no work
    Tt2_Tt1 = 1.0
    # Pt drop (use isentropic Pt/P based on M1 and M2 with static ratio p2/p1)
    f = lambda M: (1 + 0.5 * (g - 1) * M * M) ** (g / (g - 1))
    pt2_pt1 = (p2_p1 * f(M2) / f(M1))

    return {
        "M2": M2,
        "p2_p1": p2_p1,
        "T2_T1": T2_T1,
        "rho2_rho1": rho2_rho1,
        "pt2_pt1": pt2_pt1,
        "Tt2_Tt1": Tt2_Tt1,
    }

# -------------------------------------------
# Theta–beta–M for attached oblique shocks
# -------------------------------------------
def _tbm_residual(beta: float, M1: float, theta: float, gamma: float):
    """Residual of the theta–beta–M equation at angle beta."""
    g = gamma
    Mn1 = M1 * math.sin(beta)
    num = 2 * (Mn1 * Mn1 - 1)
    den = M1 * M1 * (g + math.cos(2 * beta)) + 2
    rhs = num / den * (1 / math.tan(beta))
    return math.tan(theta) - rhs

def oblique_shock(M1: float, theta: float, gamma: float = 1.4, weak: bool = True, tol: float = 1e-10, max_iter: int = 100):
    """
    Solve oblique shock for given upstream Mach M1 and flow deflection theta (radians).
    Finds shock angle beta (attached solution if exists), then downstream state.

    Inputs:
        M1     : upstream Mach (>1)
        theta  : flow deflection angle [rad] (>0)
        gamma  : specific heat ratio
        weak   : choose weak (default) or strong branch when two solutions exist
    Returns dict:
        beta, M2, p2_p1, T2_T1, rho2_rho1, pt2_pt1
    Notes:
        - If theta exceeds theta_max for given M1,gamma, shock detaches; this solver
          raises ValueError in that case.
    """
    if M1 <= 1.0:
        raise ValueError("oblique_shock: M1 must be > 1")
    if theta <= 0:
        # No deflection -> no shock (or Mach wave at theta=0)
        raise ValueError("oblique_shock: theta must be > 0 for finite shock.")

    g = gamma
    # Beta must be between the Mach angle and 90 deg
    beta_min = math.asin(1 / M1) + 1e-9
    beta_max = 0.5 * math.pi - 1e-9

    # Check for attachment: theta <= theta_max(M1,gamma)
    # theta_max occurs where dtheta/dbeta=0; use standard approximation by scanning
    # (cheap & robust for our purposes)
    def theta_for_beta(b):
        Mn1 = M1 * math.sin(b)
        num = 2 * (Mn1 * Mn1 - 1)
        den = M1 * M1 * (g + math.cos(2 * b)) + 2
        return math.atan2(num, den * math.tan(b))

    # quick scan for theta_max
    samples = 200
    thetas = []
    betas = [beta_min + (beta_max - beta_min) * i / (samples - 1) for i in range(samples)]
    for b in betas:
        try:
            thetas.append(theta_for_beta(b))
        except Exception:
            thetas.append(float("nan"))
    theta_max = max([t for t in thetas if not math.isnan(t)], default=0.0)

    if theta > theta_max + 1e-9:
        raise ValueError("oblique_shock: theta exceeds attachment limit; shock detaches.")

    # There are two solutions (weak/strong) when theta < theta_max: pick one by interval.
    # Residual function:
    def F(b): return _tbm_residual(b, M1, theta, g)

    # Find root intervals by splitting [beta_min, beta_max] at beta_star (near max)
    beta_star = betas[thetas.index(theta_max)] if theta_max > 0 else (beta_min + beta_max) / 2

    # weak branch near beta ~ Mach angle -> beta in [beta_min, beta_star]
    # strong branch near normal -> beta in [beta_star, beta_max]
    if weak:
        a, b = beta_min, beta_star
    else:
        a, b = beta_star, beta_max

    Fa, Fb = F(a), F(b)
    # If the endpoints don't bracket, expand slightly or fallback to global bisection
    if Fa * Fb > 0:
        # try whole interval
        a, b = beta_min, beta_max
        Fa, Fb = F(a), F(b)
        if Fa * Fb > 0:
            # Last resort: pick beta that minimizes |residual| in coarse grid
            beta_guess = min(betas, key=lambda x: abs(F(x)))
            a = beta_guess * (1 - 1e-6)
            b = beta_guess * (1 + 1e-6)
            Fa, Fb = F(a), F(b)

    # Bisection
    it = 0
    while it < max_iter:
        m = 0.5 * (a + b)
        Fm = F(m)
        if abs(Fm) < tol or abs(b - a) < tol:
            beta = m
            break
        if Fa * Fm <= 0:
            b, Fb = m, Fm
        else:
            a, Fa = m, Fm
        it += 1
    else:
        raise RuntimeError("oblique_shock: bisection did not converge")

    beta = 0.5 * (a + b)

    # Use normal-shock relations with Mn1, then convert to full M2
    Mn1 = M1 * math.sin(beta)
    ns = normal_shock(Mn1, g)
    Mn2 = ns["M2"]
    # Relation between Mn2 and M2: Mn2 = M2 * sin(beta - theta)
    s = math.sin(beta - theta)
    if abs(s) < 1e-12:
        raise RuntimeError("oblique_shock: degenerate geometry (beta ~ theta).")
    M2 = Mn2 / s

    # Static ratios across oblique shock are same as normal shock using Mn1
    p2_p1 = ns["p2_p1"]
    T2_T1 = ns["T2_T1"]
    rho2_rho1 = ns["rho2_rho1"]

    # Total pressure drop across oblique shock (use full M1 and M2)
    f = lambda M: (1 + 0.5 * (g - 1) * M * M) ** (g / (g - 1))
    pt2_pt1 = p2_p1 * f(M2) / f(M1)

    return {
        "beta": beta,
        "M2": M2,
        "p2_p1": p2_p1,
        "T2_T1": T2_T1,
        "rho2_rho1": rho2_rho1,
        "pt2_pt1": pt2_pt1,
        "weak": weak,
        "theta_max": theta_max,
    }

# -------------------------------------------
# Convenience: cascade oblique shocks (ramps)
# -------------------------------------------
def cascade_ramps(M1: float, thetas, gamma: float = 1.4, weak: bool = True):
    """
    Apply a series of ramp deflections (angles in radians) to an upstream supersonic flow.
    Returns list of stage dictionaries (from oblique_shock) and final M.
    """
    M = M1
    stages = []
    for th in thetas:
        st = oblique_shock(M, th, gamma=gamma, weak=weak)
        stages.append(st)
        M = st["M2"]
    return stages, M

