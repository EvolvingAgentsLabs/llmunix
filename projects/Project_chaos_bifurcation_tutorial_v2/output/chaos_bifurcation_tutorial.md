# Chaos and Bifurcation in Discrete Prey-Predator Models
## A Comprehensive Tutorial

### Table of Contents
1. [Introduction](#introduction)
2. [Mathematical Foundations](#mathematical-foundations)
3. [Computational Implementation](#computational-implementation)
4. [Exploring Dynamics](#exploring-dynamics)
5. [Ecological Applications](#ecological-applications)
6. [Advanced Topics](#advanced-topics)
7. [Conclusion](#conclusion)

---

## 1. Introduction

### 1.1 Motivation: Why Study Chaos in Ecological Systems?

Nature is full of surprising patterns. Some populations remain remarkably stable over decades, while others fluctuate wildly from year to year. Understanding these dynamics is crucial for:

- **Conservation biology**: Predicting extinction risks
- **Resource management**: Sustainable harvesting strategies
- **Ecosystem stability**: Understanding resilience to perturbations
- **Climate change impacts**: Anticipating regime shifts

Consider the classic case of **lynx and snowshoe hare populations** in Canada. Historical records from the Hudson's Bay Company show dramatic oscillations with roughly 10-year cycles. But why? And under what conditions might these cycles become irregular or even chaotic?

### 1.2 Real-World Examples

**1. Lynx-Hare Cycles (Canada)**
- Regular 9-11 year population cycles
- Predator numbers lag behind prey
- Classic example of predator-prey dynamics

**2. Larch Budmoth Outbreaks (Swiss Alps)**
- 8-9 year cycles transitioning to irregular patterns
- Climate change may be disrupting regular cycles
- Economic impacts on forestry

**3. Plankton Dynamics (Marine Ecosystems)**
- Complex multi-species interactions
- Can exhibit chaotic fluctuations
- Affects entire food web structure

### 1.3 Learning Objectives

By the end of this tutorial, you will be able to:

1. Understand discrete-time dynamical systems and their ecological interpretation
2. Analyze equilibrium points and their stability
3. Identify different types of bifurcations in predator-prey models
4. Recognize chaotic dynamics and quantify chaos using Lyapunov exponents
5. Implement and visualize these concepts using Python
6. Apply these tools to real ecological questions

### 1.4 Prerequisites

**Mathematics:**
- Calculus (derivatives, chain rule)
- Linear algebra (eigenvalues, eigenvectors)
- Basic differential/difference equations

**Programming:**
- Python basics (functions, loops, arrays)
- NumPy for numerical computation
- Matplotlib for visualization

**Biology:**
- Basic ecology concepts (predation, competition, carrying capacity)

---

## 2. Mathematical Foundations

### 2.1 Discrete-Time Dynamical Systems

#### 2.1.1 What is a Discrete-Time System?

Many ecological populations reproduce in **discrete generations** rather than continuously:
- Annual plants (one generation per year)
- Insects with seasonal life cycles
- Forest stands measured at yearly intervals

We model these using **difference equations** rather than differential equations.

**General Form:**
```
x(t+1) = f(x(t))
```

Where:
- `x(t)` is the state at time step t (e.g., population density)
- `f` is the update function (governs dynamics)
- Time advances in discrete steps: t = 0, 1, 2, 3, ...

**Example:** Logistic map (single species with crowding)
```
N(t+1) = r·N(t)·(1 - N(t)/K)
```
- r: growth rate
- K: carrying capacity
- N(t): population at time t

#### 2.1.2 Orbits and Trajectories

An **orbit** is the sequence of states produced by iterating the map:
```
x(0) → x(1) → x(2) → x(3) → ...
```

Different initial conditions can lead to:
- **Fixed points**: x* where f(x*) = x* (population remains constant)
- **Periodic cycles**: x(t+p) = x(t) for some period p
- **Chaotic trajectories**: seemingly random, sensitive to initial conditions

### 2.2 The Ricker Prey-Predator Model

#### 2.2.1 Biological Background

The **Ricker model** (1954) was originally developed for fish populations. For prey-predator systems, we extend it to two coupled equations:

**Prey equation:**
```
N(t+1) = N(t)·exp(r·(1 - N(t)/K - α·P(t)))
```

**Predator equation:**
```
P(t+1) = N(t)·(1 - exp(-α·P(t)))
```

**Parameters:**
- `N(t)`: Prey density at time t
- `P(t)`: Predator density at time t
- `r`: Prey intrinsic growth rate (how fast prey reproduce)
- `K`: Prey carrying capacity (resource limitation)
- `α`: Predation efficiency (how effectively predators capture prey)

#### 2.2.2 Biological Interpretation

**Prey dynamics:**
- `exp(r·(1 - N/K))`: Exponential growth with intraspecific competition
- `-α·P`: Reduction due to predation
- When P = 0, prey follow Ricker model alone

**Predator dynamics:**
- `1 - exp(-α·P)`: Conversion efficiency (prey consumed → predator offspring)
- Predator reproduction proportional to prey available
- No predator death term (simplification for short timescales)

**Why exponential forms?**
- More realistic than polynomial models for high growth rates
- Naturally ensures non-negative populations
- Better captures overcompensation effects

### 2.3 Equilibrium Analysis

#### 2.3.1 Finding Fixed Points

An **equilibrium** (N*, P*) satisfies:
```
N* = N*·exp(r·(1 - N*/K - α·P*))
P* = N*·(1 - exp(-α·P*))
```

**Trivial equilibrium:** (0, 0)
- No prey, no predators
- Always exists, usually unstable

**Boundary equilibrium:** (K, 0)
- Prey at carrying capacity, no predators
- Predators can invade if conditions right

**Coexistence equilibrium:** (N*, P*) with both > 0
- Both species persist
- Requires solving coupled nonlinear equations

**Finding coexistence equilibrium:**

From prey equation:
```
1 = exp(r·(1 - N*/K - α·P*))
0 = r·(1 - N*/K - α·P*)
P* = (1/α)·(1 - N*/K)
```

From predator equation:
```
P* = N*·(1 - exp(-α·P*))
```

Substituting and solving (often requires numerical methods):
```
(1/α)·(1 - N*/K) = N*·(1 - exp(-α·(1/α)·(1 - N*/K)))
```

#### 2.3.2 Stability Intuition

An equilibrium is **stable** if small perturbations decay back to equilibrium:
- Imagine a marble in a bowl (stable) vs. on a hilltop (unstable)
- Mathematically: eigenvalues of Jacobian matrix determine stability

### 2.4 Stability Theory

#### 2.4.1 Linearization

To analyze stability, we **linearize** around the equilibrium by computing the **Jacobian matrix**:

```
J = [∂f/∂N  ∂f/∂P]
    [∂g/∂N  ∂g/∂P]
```

Evaluated at (N*, P*), where:
- f(N,P) = N·exp(r·(1 - N/K - α·P))
- g(N,P) = N·(1 - exp(-α·P))

**Partial derivatives:**

```
∂f/∂N = exp(r·(1 - N/K - α·P))·(1 - r·N/K - r·α·P)
∂f/∂P = -r·α·N·exp(r·(1 - N/K - α·P))
∂g/∂N = 1 - exp(-α·P)
∂g/∂P = α·N·exp(-α·P)
```

#### 2.4.2 Eigenvalue Analysis

The **eigenvalues** λ₁, λ₂ of the Jacobian determine stability:

**Stability conditions:**
- **Stable node**: |λ₁|, |λ₂| < 1 (both real, perturbations decay)
- **Stable spiral**: |λ₁| = |λ₂| < 1 (complex conjugates, oscillatory decay)
- **Unstable**: Any |λᵢ| > 1 (perturbations grow)
- **Neutral**: |λᵢ| = 1 (boundary case, bifurcation)

**Complex eigenvalues:**
When λ = a ± bi (complex conjugates):
- Modulus: |λ| = √(a² + b²)
- If b ≠ 0: oscillatory approach/departure
- If |λ| < 1: spiral into equilibrium
- If |λ| > 1: spiral away from equilibrium

#### 2.4.3 The Routh-Hurwitz Criterion

For 2D discrete systems, we can use simpler stability conditions:

Let trace T = λ₁ + λ₂ and determinant D = λ₁·λ₂ of Jacobian.

**Stability requires:**
1. |D| < 1 (product of eigenvalue magnitudes < 1)
2. |T| < 1 + D (ensures both eigenvalues inside unit circle)

This is easier to compute than eigenvalues directly!

### 2.5 Bifurcation Theory

#### 2.5.1 What is a Bifurcation?

A **bifurcation** is a qualitative change in system behavior when a parameter crosses a critical value:
- Stable equilibrium becomes unstable
- New equilibria or cycles appear
- Chaos emerges or disappears

**Biological significance:**
- Regime shifts in ecosystems
- Sudden population collapses
- Transition from stability to oscillations

#### 2.5.2 Types of Bifurcations

**1. Saddle-Node Bifurcation**
- Two equilibria collide and annihilate
- Example: Predator invasion threshold
- Condition: One eigenvalue passes through +1

**2. Period-Doubling Bifurcation (Flip Bifurcation)**
- Fixed point loses stability, period-2 cycle appears
- Then period-4, period-8, ... → chaos (Feigenbaum cascade)
- Condition: One eigenvalue passes through -1
- **Most common route to chaos in ecology**

**3. Neimark-Sacker Bifurcation (Hopf for discrete systems)**
- Fixed point becomes unstable, invariant circle appears
- Creates quasi-periodic or periodic oscillations
- Condition: Complex conjugate eigenvalues with |λ| = 1

#### 2.5.3 Bifurcation Diagrams

A **bifurcation diagram** shows how attractors change with a parameter:
- X-axis: Parameter value (e.g., growth rate r)
- Y-axis: Long-term behavior (equilibria, cycle points)
- Reveals sequence of bifurcations leading to chaos

**How to construct:**
1. Choose parameter range
2. For each parameter value:
   - Start with initial condition
   - Iterate map many times (transient)
   - Plot subsequent points (attractor)
3. Connect points to visualize transitions

### 2.6 Chaos Theory

#### 2.6.1 Defining Chaos

**Mathematical definition** (Devaney, 1989):
A system is chaotic if it exhibits:
1. **Sensitivity to initial conditions**: Small differences grow exponentially
2. **Topological transitivity**: System explores entire phase space
3. **Dense periodic orbits**: Arbitrarily close to any point is a periodic orbit

**Practical definition for ecologists:**
- Deterministic (no randomness in equations)
- Appears random (irregular, unpredictable over long times)
- Bounded (doesn't go to infinity)
- Sensitive to initial conditions (butterfly effect)

#### 2.6.2 The Butterfly Effect

**Sensitivity to initial conditions** means:
```
If |x(0) - y(0)| = ε (small difference)
Then |x(t) - y(t)| ≈ ε·exp(λ·t) (grows exponentially)
```

Where λ is the **Lyapunov exponent**.

**Ecological implications:**
- Long-term prediction impossible (even with perfect model!)
- Small measurement errors → large forecast errors
- Population management requires adaptive strategies

#### 2.6.3 Lyapunov Exponents

The **largest Lyapunov exponent** (LLE) quantifies chaos:

```
λ = lim(t→∞) (1/t)·∑log|f'(x(i))|
```

**Interpretation:**
- λ < 0: Stable fixed point (perturbations shrink)
- λ = 0: Periodic orbit or neutral stability
- λ > 0: **Chaos** (perturbations grow exponentially)

**Computing LLE numerically:**

```python
def lyapunov_exponent(r, alpha, K, N0, P0, num_iterations=10000):
    """
    Compute largest Lyapunov exponent for Ricker prey-predator model.
    """
    N, P = N0, P0
    lyap_sum = 0.0

    # Discard transient
    for _ in range(1000):
        N, P = ricker_step(N, P, r, alpha, K)

    # Compute Jacobian and sum logarithms
    for _ in range(num_iterations):
        J = jacobian(N, P, r, alpha, K)
        eigenvalues = np.linalg.eigvals(J)
        max_eigenvalue = np.max(np.abs(eigenvalues))
        lyap_sum += np.log(max_eigenvalue)
        N, P = ricker_step(N, P, r, alpha, K)

    return lyap_sum / num_iterations
```

#### 2.6.4 Routes to Chaos

**Period-doubling route** (Feigenbaum cascade):
```
Fixed point → Period-2 → Period-4 → Period-8 → ... → Chaos
```
- Most common in 1D and 2D maps
- Universal scaling: ratio of bifurcation intervals approaches 4.669...

**Intermittency route:**
- Nearly periodic with random chaotic bursts
- Bursts become more frequent as parameter changes

**Crisis route:**
- Sudden expansion of chaotic attractor
- Can cause sudden ecological regime shifts

---

## 3. Computational Implementation

### 3.1 Model Implementation

#### 3.1.1 Core Simulation Functions

```python
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eig

def ricker_prey_predator(N, P, r, alpha, K):
    """
    Single iteration of Ricker prey-predator model.

    Parameters:
    -----------
    N : float
        Current prey density
    P : float
        Current predator density
    r : float
        Prey intrinsic growth rate
    alpha : float
        Predation efficiency
    K : float
        Prey carrying capacity

    Returns:
    --------
    N_next, P_next : tuple of floats
        Next prey and predator densities
    """
    N_next = N * np.exp(r * (1 - N/K - alpha*P))
    P_next = N * (1 - np.exp(-alpha * P))
    return N_next, P_next

def simulate_dynamics(N0, P0, r, alpha, K, num_steps=500):
    """
    Simulate prey-predator dynamics for specified number of steps.

    Parameters:
    -----------
    N0, P0 : float
        Initial prey and predator densities
    r, alpha, K : float
        Model parameters
    num_steps : int
        Number of time steps to simulate

    Returns:
    --------
    times, N_values, P_values : arrays
        Time points, prey densities, predator densities
    """
    times = np.arange(num_steps)
    N_values = np.zeros(num_steps)
    P_values = np.zeros(num_steps)

    N_values[0] = N0
    P_values[0] = P0

    for t in range(num_steps - 1):
        N_values[t+1], P_values[t+1] = ricker_prey_predator(
            N_values[t], P_values[t], r, alpha, K
        )

    return times, N_values, P_values
```

#### 3.1.2 Equilibrium Computation

```python
from scipy.optimize import fsolve

def find_coexistence_equilibrium(r, alpha, K):
    """
    Find coexistence equilibrium numerically.

    Returns:
    --------
    N_star, P_star : tuple of floats
        Equilibrium prey and predator densities
    """
    def equations(state):
        N, P = state
        # From N* = N*·exp(r·(1 - N*/K - α·P*))
        eq1 = r * (1 - N/K - alpha*P)
        # From P* = N*·(1 - exp(-α·P*))
        eq2 = P - N * (1 - np.exp(-alpha * P))
        return [eq1, eq2]

    # Initial guess (roughly mid-carrying capacity)
    initial_guess = [K/2, 0.5]
    solution = fsolve(equations, initial_guess)

    N_star, P_star = solution

    # Check if solution is valid (positive densities)
    if N_star > 0 and P_star > 0:
        return N_star, P_star
    else:
        return None, None
```

#### 3.1.3 Jacobian and Stability Analysis

```python
def compute_jacobian(N, P, r, alpha, K):
    """
    Compute Jacobian matrix at given point.

    Returns:
    --------
    J : 2x2 numpy array
        Jacobian matrix
    """
    exp_term = np.exp(r * (1 - N/K - alpha*P))

    # Partial derivatives
    df_dN = exp_term * (1 - r*N/K - r*alpha*P)
    df_dP = -r * alpha * N * exp_term
    dg_dN = 1 - np.exp(-alpha * P)
    dg_dP = alpha * N * np.exp(-alpha * P)

    J = np.array([[df_dN, df_dP],
                  [dg_dN, dg_dP]])

    return J

def analyze_stability(N_star, P_star, r, alpha, K):
    """
    Analyze stability of equilibrium point.

    Returns:
    --------
    stable : bool
        True if equilibrium is stable
    eigenvalues : array
        Eigenvalues of Jacobian
    stability_type : str
        Description of stability type
    """
    J = compute_jacobian(N_star, P_star, r, alpha, K)
    eigenvalues, eigenvectors = eig(J)

    # Compute moduli of eigenvalues
    moduli = np.abs(eigenvalues)
    max_modulus = np.max(moduli)

    # Determine stability
    stable = max_modulus < 1.0

    # Classify stability type
    if stable:
        if np.all(np.isreal(eigenvalues)):
            stability_type = "Stable node"
        else:
            stability_type = "Stable spiral"
    else:
        if np.all(np.isreal(eigenvalues)):
            stability_type = "Unstable node"
        else:
            stability_type = "Unstable spiral"

    return stable, eigenvalues, stability_type
```

### 3.2 Analysis Methods

#### 3.2.1 Time Series Analysis

```python
def plot_time_series(times, N_values, P_values, title="Population Dynamics"):
    """
    Plot prey and predator time series.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(times, N_values, 'b-', linewidth=2, label='Prey (N)')
    ax.plot(times, P_values, 'r-', linewidth=2, label='Predator (P)')

    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Population Density', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig, ax
```

#### 3.2.2 Phase Space Analysis

```python
def plot_phase_space(N_values, P_values, N_star=None, P_star=None,
                     title="Phase Space Portrait"):
    """
    Plot phase space trajectory with equilibrium point.
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    # Plot trajectory
    ax.plot(N_values, P_values, 'b-', linewidth=1.5, alpha=0.7)
    ax.plot(N_values[0], P_values[0], 'go', markersize=10, label='Start')
    ax.plot(N_values[-1], P_values[-1], 'rs', markersize=10, label='End')

    # Plot equilibrium if provided
    if N_star is not None and P_star is not None:
        ax.plot(N_star, P_star, 'k*', markersize=15, label='Equilibrium')

    ax.set_xlabel('Prey Density (N)', fontsize=12)
    ax.set_ylabel('Predator Density (P)', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig, ax
```

#### 3.2.3 Bifurcation Diagram Construction

```python
def create_bifurcation_diagram(param_range, alpha, K, N0, P0,
                               variable='N', transient=500, plot_points=200):
    """
    Create bifurcation diagram varying growth rate r.

    Parameters:
    -----------
    param_range : tuple
        (r_min, r_max) range for growth rate
    variable : str
        'N' for prey, 'P' for predator
    transient : int
        Number of initial iterations to discard
    plot_points : int
        Number of points to plot after transient

    Returns:
    --------
    r_values, attractors : arrays
        Parameter values and corresponding attractor points
    """
    r_min, r_max = param_range
    num_params = 500
    r_values = np.linspace(r_min, r_max, num_params)

    all_r = []
    all_values = []

    for r in r_values:
        N, P = N0, P0

        # Discard transient
        for _ in range(transient):
            N, P = ricker_prey_predator(N, P, r, alpha, K)

        # Collect attractor points
        for _ in range(plot_points):
            N, P = ricker_prey_predator(N, P, r, alpha, K)
            if variable == 'N':
                all_values.append(N)
            else:
                all_values.append(P)
            all_r.append(r)

    return np.array(all_r), np.array(all_values)

def plot_bifurcation_diagram(r_values, attractors, variable='N'):
    """
    Plot bifurcation diagram.
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    ax.plot(r_values, attractors, 'b,', markersize=0.5, alpha=0.5)

    ax.set_xlabel('Growth Rate (r)', fontsize=12)
    ax.set_ylabel(f'{"Prey" if variable == "N" else "Predator"} Density',
                  fontsize=12)
    ax.set_title(f'Bifurcation Diagram - {variable}', fontsize=14)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig, ax
```

#### 3.2.4 Lyapunov Exponent Calculation

```python
def compute_lyapunov_exponent(r, alpha, K, N0, P0,
                              num_iterations=10000, transient=1000):
    """
    Compute largest Lyapunov exponent.

    Returns:
    --------
    lyapunov : float
        Largest Lyapunov exponent (positive indicates chaos)
    """
    N, P = N0, P0

    # Discard transient
    for _ in range(transient):
        N, P = ricker_prey_predator(N, P, r, alpha, K)

    # Accumulate logarithms of maximum eigenvalue magnitudes
    lyap_sum = 0.0

    for _ in range(num_iterations):
        J = compute_jacobian(N, P, r, alpha, K)
        eigenvalues, _ = eig(J)
        max_eigenvalue_modulus = np.max(np.abs(eigenvalues))

        # Avoid log(0)
        if max_eigenvalue_modulus > 1e-10:
            lyap_sum += np.log(max_eigenvalue_modulus)

        N, P = ricker_prey_predator(N, P, r, alpha, K)

    return lyap_sum / num_iterations

def lyapunov_spectrum(param_range, alpha, K, N0, P0):
    """
    Compute Lyapunov exponent over parameter range.

    Returns:
    --------
    r_values, lyapunov_values : arrays
    """
    r_min, r_max = param_range
    r_values = np.linspace(r_min, r_max, 100)
    lyapunov_values = []

    for r in r_values:
        lyap = compute_lyapunov_exponent(r, alpha, K, N0, P0)
        lyapunov_values.append(lyap)

    return r_values, np.array(lyapunov_values)

def plot_lyapunov_spectrum(r_values, lyapunov_values):
    """
    Plot Lyapunov exponent vs parameter.
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(r_values, lyapunov_values, 'b-', linewidth=2)
    ax.axhline(y=0, color='r', linestyle='--', linewidth=1, label='λ = 0')

    # Shade chaotic region (λ > 0)
    ax.fill_between(r_values, 0, lyapunov_values,
                    where=(lyapunov_values > 0),
                    alpha=0.3, color='red', label='Chaotic (λ > 0)')

    ax.set_xlabel('Growth Rate (r)', fontsize=12)
    ax.set_ylabel('Largest Lyapunov Exponent (λ)', fontsize=12)
    ax.set_title('Lyapunov Spectrum', fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig, ax
```

### 3.3 Visualization Techniques

#### 3.3.1 Combined Analysis Dashboard

```python
def create_analysis_dashboard(r, alpha, K, N0, P0, num_steps=500):
    """
    Create comprehensive analysis dashboard with multiple plots.
    """
    # Simulate dynamics
    times, N_values, P_values = simulate_dynamics(N0, P0, r, alpha, K, num_steps)

    # Find equilibrium
    N_star, P_star = find_coexistence_equilibrium(r, alpha, K)

    # Create figure with subplots
    fig = plt.figure(figsize=(16, 10))

    # Time series
    ax1 = plt.subplot(2, 3, 1)
    ax1.plot(times, N_values, 'b-', linewidth=2, label='Prey')
    ax1.plot(times, P_values, 'r-', linewidth=2, label='Predator')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Density')
    ax1.set_title('Time Series')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Phase space
    ax2 = plt.subplot(2, 3, 2)
    ax2.plot(N_values, P_values, 'b-', linewidth=1.5, alpha=0.7)
    ax2.plot(N_values[0], P_values[0], 'go', markersize=10, label='Start')
    if N_star and P_star:
        ax2.plot(N_star, P_star, 'k*', markersize=15, label='Equilibrium')
    ax2.set_xlabel('Prey Density')
    ax2.set_ylabel('Predator Density')
    ax2.set_title('Phase Space')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Return map for prey
    ax3 = plt.subplot(2, 3, 3)
    ax3.plot(N_values[:-1], N_values[1:], 'b.', markersize=2, alpha=0.5)
    ax3.plot([0, max(N_values)], [0, max(N_values)], 'r--', linewidth=1)
    ax3.set_xlabel('N(t)')
    ax3.set_ylabel('N(t+1)')
    ax3.set_title('Return Map - Prey')
    ax3.grid(True, alpha=0.3)

    # Bifurcation diagram
    ax4 = plt.subplot(2, 3, 4)
    r_vals, attractors = create_bifurcation_diagram(
        (r*0.5, r*1.5), alpha, K, N0, P0, transient=300, plot_points=100
    )
    ax4.plot(r_vals, attractors, 'b,', markersize=0.5)
    ax4.axvline(x=r, color='r', linestyle='--', linewidth=2, label=f'Current r={r:.2f}')
    ax4.set_xlabel('Growth Rate (r)')
    ax4.set_ylabel('Prey Density')
    ax4.set_title('Bifurcation Diagram')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    # Lyapunov spectrum
    ax5 = plt.subplot(2, 3, 5)
    r_lyap, lyap_vals = lyapunov_spectrum((r*0.5, r*1.5), alpha, K, N0, P0)
    ax5.plot(r_lyap, lyap_vals, 'b-', linewidth=2)
    ax5.axhline(y=0, color='r', linestyle='--', linewidth=1)
    ax5.axvline(x=r, color='g', linestyle='--', linewidth=2, label=f'Current r={r:.2f}')
    ax5.fill_between(r_lyap, 0, lyap_vals, where=(lyap_vals > 0),
                     alpha=0.3, color='red')
    ax5.set_xlabel('Growth Rate (r)')
    ax5.set_ylabel('Lyapunov Exponent')
    ax5.set_title('Lyapunov Spectrum')
    ax5.legend()
    ax5.grid(True, alpha=0.3)

    # Parameter info
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')

    info_text = f"""
    MODEL PARAMETERS
    ─────────────────
    Growth rate (r): {r:.3f}
    Predation (α): {alpha:.3f}
    Carrying capacity (K): {K:.1f}

    EQUILIBRIUM
    ─────────────────
    Prey (N*): {N_star:.3f if N_star else 'N/A'}
    Predator (P*): {P_star:.3f if P_star else 'N/A'}

    STABILITY ANALYSIS
    ─────────────────
    """

    if N_star and P_star:
        stable, eigenvals, stab_type = analyze_stability(N_star, P_star, r, alpha, K)
        info_text += f"Type: {stab_type}\n"
        info_text += f"Eigenvalues: {eigenvals[0]:.3f}, {eigenvals[1]:.3f}\n"
        info_text += f"Max |λ|: {np.max(np.abs(eigenvals)):.3f}\n\n"

    # Lyapunov exponent
    lyap = compute_lyapunov_exponent(r, alpha, K, N0, P0, num_iterations=5000)
    info_text += f"CHAOS INDICATOR\n─────────────────\n"
    info_text += f"Lyapunov exp: {lyap:.4f}\n"
    if lyap > 0.01:
        info_text += "Status: CHAOTIC ⚠️"
    elif lyap > -0.01:
        info_text += "Status: PERIODIC"
    else:
        info_text += "Status: STABLE"

    ax6.text(0.1, 0.9, info_text, fontsize=11, verticalalignment='top',
             fontfamily='monospace')

    plt.tight_layout()
    return fig
```

---

## 4. Exploring Dynamics

### 4.1 Stable Equilibrium Regime

#### 4.1.1 Low Growth Rate Scenario

**Parameters:**
```python
r = 1.0      # Low growth rate
alpha = 0.05 # Moderate predation
K = 100.0    # Carrying capacity
N0, P0 = 50.0, 0.5
```

**Expected behavior:**
- Equilibrium exists and is stable
- Both eigenvalues have modulus < 1
- Small perturbations decay back to equilibrium
- Populations converge smoothly (node) or with damped oscillations (spiral)

**Code example:**
```python
# Simulate stable regime
times, N_vals, P_vals = simulate_dynamics(50.0, 0.5, 1.0, 0.05, 100.0, 500)

# Find and analyze equilibrium
N_star, P_star = find_coexistence_equilibrium(1.0, 0.05, 100.0)
stable, eigenvals, stab_type = analyze_stability(N_star, P_star, 1.0, 0.05, 100.0)

print(f"Equilibrium: N* = {N_star:.2f}, P* = {P_star:.2f}")
print(f"Stability: {stab_type}")
print(f"Eigenvalues: {eigenvals}")
print(f"Moduli: {np.abs(eigenvals)}")

# Visualize
plot_time_series(times, N_vals, P_vals, "Stable Equilibrium Regime")
plot_phase_space(N_vals, P_vals, N_star, P_star)
```

**Ecological interpretation:**
- Predator-prey system self-regulates
- Sustainable coexistence
- Predictable long-term dynamics
- Good for conservation planning

### 4.2 Periodic Oscillations

#### 4.2.1 Moderate Growth Rate Scenario

**Parameters:**
```python
r = 2.0      # Moderate growth rate
alpha = 0.05
K = 100.0
N0, P0 = 50.0, 0.5
```

**Expected behavior:**
- Equilibrium becomes unstable
- Period-2 cycle emerges (populations alternate between two states)
- Eigenvalues: one or both have |λ| > 1
- Regular oscillations persist indefinitely

**Period-doubling cascade:**
As r increases further:
- Period-2 → Period-4 → Period-8 → ...
- Cascade converges to chaos at critical value
- **Feigenbaum constant**: ratio of intervals ≈ 4.669

**Code example:**
```python
# Simulate periodic regime
times, N_vals, P_vals = simulate_dynamics(50.0, 0.5, 2.0, 0.05, 100.0, 500)

# Check equilibrium stability
N_star, P_star = find_coexistence_equilibrium(2.0, 0.05, 100.0)
stable, eigenvals, stab_type = analyze_stability(N_star, P_star, 2.0, 0.05, 100.0)

print(f"Equilibrium stable: {stable}")
print(f"Eigenvalue moduli: {np.abs(eigenvals)}")

# Detect period
from scipy.signal import find_peaks
peaks, _ = find_peaks(N_vals[200:], distance=10)
if len(peaks) > 2:
    periods = np.diff(peaks)
    avg_period = np.mean(periods)
    print(f"Detected period: {avg_period:.1f}")

# Visualize
plot_time_series(times, N_vals, P_vals, "Periodic Oscillations")
plot_phase_space(N_vals, P_vals, N_star, P_star)
```

**Ecological interpretation:**
- Regular boom-bust cycles
- Predator numbers lag behind prey
- Still predictable, but more variable
- Harvesting should account for oscillations

### 4.3 Chaotic Dynamics

#### 4.3.1 High Growth Rate Scenario

**Parameters:**
```python
r = 2.8      # High growth rate
alpha = 0.05
K = 100.0
N0, P0 = 50.0, 0.5
```

**Expected behavior:**
- No stable equilibrium or periodic cycle
- Sensitive dependence on initial conditions
- Lyapunov exponent > 0
- Bounded but apparently random fluctuations

**Code example:**
```python
# Simulate chaotic regime
times, N_vals, P_vals = simulate_dynamics(50.0, 0.5, 2.8, 0.05, 100.0, 500)

# Compute Lyapunov exponent
lyap = compute_lyapunov_exponent(2.8, 0.05, 100.0, 50.0, 0.5)
print(f"Lyapunov exponent: {lyap:.4f}")
if lyap > 0:
    print("System is CHAOTIC")

# Demonstrate sensitivity to initial conditions
N0_perturbed = 50.001  # Tiny perturbation
times2, N_vals2, P_vals2 = simulate_dynamics(N0_perturbed, 0.5, 2.8, 0.05, 100.0, 500)

# Plot divergence
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

ax1.plot(times, N_vals, 'b-', label='Original', linewidth=2)
ax1.plot(times2, N_vals2, 'r--', label='Perturbed (ΔN₀=0.001)', linewidth=2)
ax1.set_ylabel('Prey Density')
ax1.set_title('Sensitivity to Initial Conditions')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot absolute difference
diff = np.abs(N_vals - N_vals2)
ax2.semilogy(times, diff, 'g-', linewidth=2)
ax2.set_xlabel('Time')
ax2.set_ylabel('|ΔN(t)|')
ax2.set_title('Exponential Divergence')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Visualize
plot_time_series(times, N_vals, P_vals, "Chaotic Dynamics")
plot_phase_space(N_vals, P_vals)
```

**Ecological interpretation:**
- Unpredictable population fluctuations
- High extinction risk during low-density episodes
- Long-term forecasting impossible
- Requires precautionary management

### 4.4 Bifurcation Diagrams

#### 4.4.1 Complete Bifurcation Analysis

**Goal:** Map out all dynamical regimes as function of r.

**Code example:**
```python
# Create bifurcation diagram for wide parameter range
r_vals, attractors = create_bifurcation_diagram(
    param_range=(0.5, 3.5),
    alpha=0.05,
    K=100.0,
    N0=50.0,
    P0=0.5,
    variable='N',
    transient=1000,
    plot_points=300
)

# Plot
fig, ax = plot_bifurcation_diagram(r_vals, attractors, 'N')

# Add annotations for key bifurcations
ax.axvline(x=1.5, color='green', linestyle='--', alpha=0.5,
          label='First bifurcation')
ax.axvline(x=2.5, color='orange', linestyle='--', alpha=0.5,
          label='Onset of chaos')
ax.legend()

plt.show()
```

**Regions to identify:**
1. **Stable fixed point** (low r): Single line
2. **Period-2** (moderate r): Two lines
3. **Period-4, 8, ...**: Cascade of doublings
4. **Chaos** (high r): Dense cloud of points
5. **Periodic windows**: Narrow periodic bands within chaos

#### 4.4.2 Two-Parameter Bifurcation Diagrams

**Goal:** Explore how dynamics vary with both r and α.

**Code example:**
```python
def two_parameter_bifurcation(r_range, alpha_range, K, N0, P0):
    """
    Create 2D bifurcation diagram showing dynamical regimes.
    """
    r_values = np.linspace(r_range[0], r_range[1], 100)
    alpha_values = np.linspace(alpha_range[0], alpha_range[1], 100)

    lyap_grid = np.zeros((len(alpha_values), len(r_values)))

    for i, alpha in enumerate(alpha_values):
        for j, r in enumerate(r_values):
            lyap = compute_lyapunov_exponent(r, alpha, K, N0, P0,
                                            num_iterations=3000)
            lyap_grid[i, j] = lyap

    return r_values, alpha_values, lyap_grid

# Compute
r_vals, alpha_vals, lyap_grid = two_parameter_bifurcation(
    r_range=(0.5, 3.5),
    alpha_range=(0.01, 0.15),
    K=100.0,
    N0=50.0,
    P0=0.5
)

# Plot
fig, ax = plt.subplots(figsize=(12, 8))
im = ax.contourf(r_vals, alpha_vals, lyap_grid, levels=20, cmap='RdYlBu_r')
ax.contour(r_vals, alpha_vals, lyap_grid, levels=[0], colors='black',
          linewidths=2)
ax.set_xlabel('Growth Rate (r)', fontsize=12)
ax.set_ylabel('Predation Efficiency (α)', fontsize=12)
ax.set_title('Two-Parameter Bifurcation Diagram\n(Lyapunov Exponent)',
            fontsize=14)
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Lyapunov Exponent', fontsize=11)
plt.tight_layout()
plt.show()
```

**Interpretation:**
- **Blue regions**: Stable/periodic (λ < 0)
- **Red regions**: Chaotic (λ > 0)
- **Black contour**: Bifurcation boundary (λ = 0)

### 4.5 Lyapunov Exponents

#### 4.5.1 Computing and Visualizing Lyapunov Spectrum

**Code example:**
```python
# Compute Lyapunov spectrum over parameter range
r_vals, lyap_vals = lyapunov_spectrum(
    param_range=(0.5, 3.5),
    alpha=0.05,
    K=100.0,
    N0=50.0,
    P0=0.5
)

# Plot
fig, ax = plot_lyapunov_spectrum(r_vals, lyap_vals)

# Add annotations
ax.text(1.0, -0.3, 'Stable\nEquilibrium', fontsize=11, ha='center')
ax.text(2.0, -0.15, 'Periodic\nOscillations', fontsize=11, ha='center')
ax.text(3.0, 0.15, 'Chaos', fontsize=11, ha='center', color='red')

plt.show()
```

#### 4.5.2 Relationship to Bifurcation Diagram

**Key observation:** Lyapunov exponent crosses zero at bifurcation points!

**Combined visualization:**
```python
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

# Bifurcation diagram on top
r_bif, attr_bif = create_bifurcation_diagram((0.5, 3.5), 0.05, 100.0,
                                              50.0, 0.5, transient=1000)
ax1.plot(r_bif, attr_bif, 'b,', markersize=0.5)
ax1.set_ylabel('Prey Density', fontsize=12)
ax1.set_title('Bifurcation Diagram and Lyapunov Spectrum', fontsize=14)
ax1.grid(True, alpha=0.3)

# Lyapunov spectrum on bottom
r_lyap, lyap_vals = lyapunov_spectrum((0.5, 3.5), 0.05, 100.0, 50.0, 0.5)
ax2.plot(r_lyap, lyap_vals, 'r-', linewidth=2)
ax2.axhline(y=0, color='k', linestyle='--', linewidth=1)
ax2.fill_between(r_lyap, 0, lyap_vals, where=(lyap_vals > 0),
                alpha=0.3, color='red')
ax2.set_xlabel('Growth Rate (r)', fontsize=12)
ax2.set_ylabel('Lyapunov Exponent', fontsize=12)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

**Interpretation:**
- Period-doubling bifurcations: λ jumps from negative to less negative
- Onset of chaos: λ crosses zero and becomes positive
- Periodic windows in chaos: λ dips below zero briefly

---

## 5. Ecological Applications

### 5.1 Population Management

#### 5.1.1 Harvesting Strategies

**Problem:** How much can we harvest without destabilizing the system?

**Model with harvesting:**
```python
def ricker_with_harvest(N, P, r, alpha, K, h_N, h_P):
    """
    Ricker model with constant harvesting rates.

    Parameters:
    -----------
    h_N : float
        Prey harvesting rate (fraction removed)
    h_P : float
        Predator harvesting rate (fraction removed)
    """
    N_next = N * np.exp(r * (1 - N/K - alpha*P)) * (1 - h_N)
    P_next = N * (1 - np.exp(-alpha * P)) * (1 - h_P)
    return N_next, P_next
```

**Analysis questions:**
1. How does harvesting affect equilibrium densities?
2. Can harvesting stabilize chaotic dynamics?
3. What is the maximum sustainable yield?

**Example analysis:**
```python
# Compare no harvest vs. moderate harvest
r, alpha, K = 2.8, 0.05, 100.0
N0, P0 = 50.0, 0.5

# No harvest (chaotic)
times1, N_no_h, P_no_h = simulate_dynamics(N0, P0, r, alpha, K, 500)

# With harvest (potentially stabilizing)
h_N, h_P = 0.1, 0.05  # 10% prey, 5% predator
times2 = np.arange(500)
N_with_h = np.zeros(500)
P_with_h = np.zeros(500)
N_with_h[0], P_with_h[0] = N0, P0

for t in range(499):
    N_with_h[t+1], P_with_h[t+1] = ricker_with_harvest(
        N_with_h[t], P_with_h[t], r, alpha, K, h_N, h_P
    )

# Compute Lyapunov exponents
lyap_no_h = compute_lyapunov_exponent(r, alpha, K, N0, P0)
# (Would need to modify function for harvest case)

# Compare
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.plot(times1, N_no_h, 'b-', label='No harvest')
ax1.set_xlabel('Time')
ax1.set_ylabel('Prey Density')
ax1.set_title(f'No Harvest (λ = {lyap_no_h:.3f})')
ax1.grid(True, alpha=0.3)

ax2.plot(times2, N_with_h, 'r-', label='With harvest')
ax2.set_xlabel('Time')
ax2.set_ylabel('Prey Density')
ax2.set_title(f'With Harvest (h_N={h_N}, h_P={h_P})')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

**Key findings:**
- Moderate harvesting can stabilize chaos (Schaffer effect)
- Over-harvesting destabilizes or causes extinction
- Optimal harvest balances yield and stability

#### 5.1.2 Regime Shift Detection

**Problem:** Early warning signals before population collapse.

**Indicators of approaching bifurcation:**
1. **Critical slowing down**: Recovery from perturbations takes longer
2. **Increased variance**: Population fluctuations grow
3. **Increased autocorrelation**: Current state more similar to past

**Code example:**
```python
def compute_early_warning_signals(N_values, window=50):
    """
    Compute early warning signals from time series.

    Returns:
    --------
    variance, autocorr_lag1 : arrays
        Rolling variance and lag-1 autocorrelation
    """
    n = len(N_values)
    variance = np.zeros(n - window)
    autocorr = np.zeros(n - window)

    for i in range(n - window):
        segment = N_values[i:i+window]

        # Variance
        variance[i] = np.var(segment)

        # Lag-1 autocorrelation
        autocorr[i] = np.corrcoef(segment[:-1], segment[1:])[0, 1]

    return variance, autocorr

# Simulate approaching bifurcation
r_values = np.linspace(1.5, 2.5, 1000)  # Gradually increasing
N, P = 50.0, 0.5
N_series = []

for r in r_values:
    N, P = ricker_prey_predator(N, P, r, 0.05, 100.0)
    N_series.append(N)

N_series = np.array(N_series)

# Compute warning signals
variance, autocorr = compute_early_warning_signals(N_series, window=50)

# Plot
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

ax1.plot(N_series, 'b-', linewidth=1)
ax1.set_ylabel('Prey Density')
ax1.set_title('Population Dynamics Approaching Bifurcation')
ax1.grid(True, alpha=0.3)

ax2.plot(variance, 'r-', linewidth=2)
ax2.set_ylabel('Variance')
ax2.set_title('Early Warning Signal: Increasing Variance')
ax2.grid(True, alpha=0.3)

ax3.plot(autocorr, 'g-', linewidth=2)
ax3.set_xlabel('Time Step')
ax3.set_ylabel('Lag-1 Autocorrelation')
ax3.set_title('Early Warning Signal: Increasing Autocorrelation')
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

**Management implications:**
- Monitor variance and autocorrelation as leading indicators
- Implement precautionary measures when signals detected
- Reduce stressors to move system away from bifurcation

### 5.2 Conservation Implications

#### 5.2.1 Minimum Viable Population Size

**Problem:** What population size ensures low extinction risk in chaotic systems?

**Approach:**
1. Simulate dynamics with demographic stochasticity
2. Measure extinction probability vs. population size
3. Determine threshold for acceptable risk

**Stochastic model:**
```python
def ricker_stochastic(N, P, r, alpha, K, sigma=0.1):
    """
    Ricker model with demographic stochasticity.

    Parameters:
    -----------
    sigma : float
        Environmental noise strength
    """
    # Environmental stochasticity (affects growth rate)
    r_noisy = r + np.random.normal(0, sigma)

    N_next = N * np.exp(r_noisy * (1 - N/K - alpha*P))
    P_next = N * (1 - np.exp(-alpha * P))

    # Demographic stochasticity (binomial sampling)
    if N_next > 0:
        N_next = np.random.binomial(int(N_next * 100),
                                    min(1.0, 1/100)) * 100
    if P_next > 0:
        P_next = np.random.binomial(int(P_next * 100),
                                    min(1.0, 1/100)) * 100

    return max(0, N_next), max(0, P_next)

def extinction_probability(N0_range, P0, r, alpha, K, sigma,
                          num_replicates=100, num_steps=500):
    """
    Estimate extinction probability vs. initial population size.
    """
    extinction_prob = []

    for N0 in N0_range:
        extinctions = 0

        for _ in range(num_replicates):
            N, P = N0, P0

            for t in range(num_steps):
                N, P = ricker_stochastic(N, P, r, alpha, K, sigma)

                # Extinction threshold
                if N < 1.0 or P < 0.1:
                    extinctions += 1
                    break

        extinction_prob.append(extinctions / num_replicates)

    return extinction_prob

# Analyze
N0_range = np.linspace(10, 100, 20)
ext_prob = extinction_probability(N0_range, 0.5, 2.5, 0.05, 100.0, 0.2)

# Plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(N0_range, ext_prob, 'ro-', linewidth=2, markersize=8)
ax.axhline(y=0.05, color='g', linestyle='--', linewidth=2,
          label='5% risk threshold')
ax.set_xlabel('Initial Prey Population Size', fontsize=12)
ax.set_ylabel('Extinction Probability', fontsize=12)
ax.set_title('Minimum Viable Population Analysis', fontsize=14)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

**Conservation guidelines:**
- Chaotic systems require larger buffer populations
- Account for environmental variability (σ)
- Regular monitoring to detect approaching thresholds

### 5.3 Climate Change Effects

#### 5.3.1 Shifting Parameter Values

**Problem:** How do changing environmental conditions alter dynamics?

**Scenarios:**
1. **Warming temperatures**: Increase r (faster prey reproduction)
2. **Habitat loss**: Decrease K (lower carrying capacity)
3. **Phenological mismatch**: Change α (altered predation efficiency)

**Analysis:**
```python
def climate_change_scenario(r_trajectory, alpha, K, N0, P0):
    """
    Simulate dynamics with time-varying growth rate.

    Parameters:
    -----------
    r_trajectory : array
        Growth rate values over time (e.g., gradual increase)
    """
    num_steps = len(r_trajectory)
    N_values = np.zeros(num_steps)
    P_values = np.zeros(num_steps)
    lyap_values = np.zeros(num_steps)

    N_values[0], P_values[0] = N0, P0

    for t in range(num_steps - 1):
        r = r_trajectory[t]
        N_values[t+1], P_values[t+1] = ricker_prey_predator(
            N_values[t], P_values[t], r, alpha, K
        )

        # Compute local Lyapunov exponent
        if t > 100:  # After transient
            lyap_values[t] = compute_lyapunov_exponent(
                r, alpha, K, N_values[t], P_values[t],
                num_iterations=1000, transient=0
            )

    return N_values, P_values, lyap_values

# Climate warming scenario: gradual increase in r
num_years = 500
r_trajectory = np.linspace(1.5, 3.0, num_years)  # Warming over 500 years

N_vals, P_vals, lyap_vals = climate_change_scenario(
    r_trajectory, 0.05, 100.0, 50.0, 0.5
)

# Visualize
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

ax1.plot(r_trajectory, 'k-', linewidth=2)
ax1.set_ylabel('Growth Rate (r)')
ax1.set_title('Climate Change Scenario: Increasing Growth Rate')
ax1.grid(True, alpha=0.3)

ax2.plot(N_vals, 'b-', linewidth=1.5, label='Prey')
ax2.plot(P_vals, 'r-', linewidth=1.5, label='Predator')
ax2.set_ylabel('Density')
ax2.set_title('Population Dynamics')
ax2.legend()
ax2.grid(True, alpha=0.3)

ax3.plot(lyap_vals, 'g-', linewidth=2)
ax3.axhline(y=0, color='r', linestyle='--', linewidth=1)
ax3.set_xlabel('Time (years)')
ax3.set_ylabel('Lyapunov Exponent')
ax3.set_title('Dynamical Regime Shifts')
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

**Key findings:**
- System transitions through multiple dynamical regimes
- May cross bifurcation points suddenly (regime shifts)
- Management strategies must adapt to changing baselines

#### 5.3.2 Tipping Points and Hysteresis

**Problem:** Can ecosystems return to previous states when conditions improve?

**Hysteresis:** System state depends on history, not just current parameters.

**Code example:**
```python
def hysteresis_analysis(r_range, alpha, K, N0, P0, direction='up'):
    """
    Analyze hysteresis by gradually changing parameter.

    Parameters:
    -----------
    direction : str
        'up' for increasing r, 'down' for decreasing r
    """
    r_values = r_range if direction == 'up' else r_range[::-1]
    N, P = N0, P0
    equilibria = []

    for r in r_values:
        # Simulate to equilibrium/attractor
        for _ in range(1000):  # Transient
            N, P = ricker_prey_predator(N, P, r, alpha, K)

        # Record attractor
        attractor_N = []
        for _ in range(100):
            N, P = ricker_prey_predator(N, P, r, alpha, K)
            attractor_N.append(N)

        equilibria.append(np.mean(attractor_N))

    return r_values, equilibria

# Forward (increasing r)
r_range_up = np.linspace(1.0, 3.0, 100)
r_up, eq_up = hysteresis_analysis(r_range_up, 0.05, 100.0, 50.0, 0.5, 'up')

# Backward (decreasing r)
r_range_down = np.linspace(3.0, 1.0, 100)
r_down, eq_down = hysteresis_analysis(r_range_down, 0.05, 100.0,
                                      eq_up[-1], 0.5, 'down')

# Plot hysteresis loop
fig, ax = plt.subplots(figsize=(10, 7))
ax.plot(r_up, eq_up, 'b-', linewidth=2, label='Increasing r (degradation)')
ax.plot(r_down, eq_down, 'r-', linewidth=2, label='Decreasing r (restoration)')
ax.set_xlabel('Growth Rate (r)', fontsize=12)
ax.set_ylabel('Mean Prey Density', fontsize=12)
ax.set_title('Hysteresis in Ecosystem Response', fontsize=14)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

# Annotate tipping points
ax.annotate('Tipping point', xy=(2.5, eq_up[75]), xytext=(2.7, 80),
            arrowprops=dict(arrowstyle='->', lw=2), fontsize=11)

plt.tight_layout()
plt.show()
```

**Conservation implications:**
- Restoration may not simply reverse degradation
- Need to reduce stressors beyond original threshold
- Prevent crossing tipping points in first place

---

## 6. Advanced Topics

### 6.1 Spatial Extensions

#### 6.1.1 Metapopulation Dynamics

**Concept:** Multiple local populations connected by dispersal.

**Model:**
```python
def ricker_metapopulation(N_patches, P_patches, r, alpha, K, dispersal):
    """
    Ricker model on multiple patches with dispersal.

    Parameters:
    -----------
    N_patches, P_patches : arrays
        Prey and predator densities in each patch
    dispersal : float
        Fraction of individuals dispersing to neighboring patches
    """
    num_patches = len(N_patches)
    N_next = np.zeros(num_patches)
    P_next = np.zeros(num_patches)

    for i in range(num_patches):
        # Local dynamics
        N_local, P_local = ricker_prey_predator(
            N_patches[i], P_patches[i], r, alpha, K
        )

        # Dispersal (simple nearest-neighbor)
        neighbors = [(i-1) % num_patches, (i+1) % num_patches]

        # Emigration
        N_stay = N_local * (1 - dispersal)
        P_stay = P_local * (1 - dispersal)

        # Immigration
        N_immigrants = dispersal * (N_patches[neighbors[0]] +
                                    N_patches[neighbors[1]]) / 2
        P_immigrants = dispersal * (P_patches[neighbors[0]] +
                                    P_patches[neighbors[1]]) / 2

        N_next[i] = N_stay + N_immigrants
        P_next[i] = P_stay + P_immigrants

    return N_next, P_next

# Simulate metapopulation
num_patches = 10
N_init = np.random.uniform(30, 70, num_patches)
P_init = np.random.uniform(0.3, 0.7, num_patches)

num_steps = 500
N_meta = np.zeros((num_steps, num_patches))
P_meta = np.zeros((num_steps, num_patches))
N_meta[0] = N_init
P_meta[0] = P_init

for t in range(num_steps - 1):
    N_meta[t+1], P_meta[t+1] = ricker_metapopulation(
        N_meta[t], P_meta[t], 2.5, 0.05, 100.0, dispersal=0.1
    )

# Visualize space-time dynamics
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

im1 = ax1.imshow(N_meta.T, aspect='auto', cmap='Blues', origin='lower')
ax1.set_xlabel('Time')
ax1.set_ylabel('Patch')
ax1.set_title('Prey Density in Metapopulation')
plt.colorbar(im1, ax=ax1)

im2 = ax2.imshow(P_meta.T, aspect='auto', cmap='Reds', origin='lower')
ax2.set_xlabel('Time')
ax2.set_ylabel('Patch')
ax2.set_title('Predator Density in Metapopulation')
plt.colorbar(im2, ax=ax2)

plt.tight_layout()
plt.show()
```

**Key insights:**
- Dispersal can synchronize or desynchronize patches
- Local chaos may be stabilized by spatial coupling
- Extinction risk reduced by rescue effect

#### 6.1.2 Spatially Extended Systems

**Partial Differential Equations (PDEs):**
Continuous space, diffusion-reaction systems.

**Discrete approximation:**
```python
def ricker_spatial_2d(N_grid, P_grid, r, alpha, K, diffusion):
    """
    Ricker model on 2D grid with diffusion.

    Parameters:
    -----------
    N_grid, P_grid : 2D arrays
        Spatial distribution of prey and predators
    diffusion : float
        Diffusion coefficient (0 = no movement, 1 = high dispersal)
    """
    from scipy.ndimage import laplace

    # Local dynamics
    N_new = N_grid * np.exp(r * (1 - N_grid/K - alpha*P_grid))
    P_new = N_grid * (1 - np.exp(-alpha * P_grid))

    # Diffusion (Laplacian operator)
    N_diffused = N_new + diffusion * laplace(N_new)
    P_diffused = P_new + diffusion * laplace(P_new)

    return np.clip(N_diffused, 0, None), np.clip(P_diffused, 0, None)

# Example: spatially heterogeneous initial conditions
grid_size = 50
N_grid = np.random.uniform(20, 80, (grid_size, grid_size))
P_grid = np.random.uniform(0.2, 0.8, (grid_size, grid_size))

# Add localized disturbance
N_grid[20:30, 20:30] = 5.0  # Local prey depletion

# Simulate
num_steps = 200
for t in range(num_steps):
    N_grid, P_grid = ricker_spatial_2d(N_grid, P_grid, 2.0, 0.05, 100.0, 0.05)

# Visualize final state
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

im1 = ax1.imshow(N_grid, cmap='Blues', origin='lower')
ax1.set_title('Prey Distribution')
plt.colorbar(im1, ax=ax1)

im2 = ax2.imshow(P_grid, cmap='Reds', origin='lower')
ax2.set_title('Predator Distribution')
plt.colorbar(im2, ax=ax2)

plt.tight_layout()
plt.show()
```

**Emergent patterns:**
- Spiral waves (rotating predator-prey fronts)
- Patchy distributions (spatial chaos)
- Range boundaries (invasion fronts)

### 6.2 Stochastic Perturbations

#### 6.2.1 Environmental Stochasticity

**Sources of randomness:**
1. Weather variability (affects r)
2. Resource fluctuations (affects K)
3. Migration events (affects initial conditions)

**Model:**
```python
def ricker_environmental_stochasticity(N, P, r, alpha, K, sigma_r, sigma_K):
    """
    Ricker model with environmental stochasticity.

    Parameters:
    -----------
    sigma_r : float
        Standard deviation of growth rate fluctuations
    sigma_K : float
        Standard deviation of carrying capacity fluctuations
    """
    # Random parameter fluctuations
    r_noisy = r + np.random.normal(0, sigma_r)
    K_noisy = K + np.random.normal(0, sigma_K)
    K_noisy = max(1.0, K_noisy)  # Ensure positive

    N_next = N * np.exp(r_noisy * (1 - N/K_noisy - alpha*P))
    P_next = N * (1 - np.exp(-alpha * P))

    return N_next, P_next

# Compare deterministic vs. stochastic
r, alpha, K = 2.0, 0.05, 100.0
N0, P0 = 50.0, 0.5
num_steps = 500

# Deterministic
times_det, N_det, P_det = simulate_dynamics(N0, P0, r, alpha, K, num_steps)

# Stochastic ensemble
num_replicates = 50
N_stoch_ensemble = np.zeros((num_replicates, num_steps))
P_stoch_ensemble = np.zeros((num_replicates, num_steps))

for rep in range(num_replicates):
    N, P = N0, P0
    for t in range(num_steps):
        N_stoch_ensemble[rep, t] = N
        P_stoch_ensemble[rep, t] = P
        N, P = ricker_environmental_stochasticity(N, P, r, alpha, K,
                                                  sigma_r=0.1, sigma_K=5.0)

# Plot ensemble
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Prey
for rep in range(num_replicates):
    ax1.plot(N_stoch_ensemble[rep], 'b-', linewidth=0.5, alpha=0.3)
ax1.plot(N_det, 'r-', linewidth=3, label='Deterministic')
ax1.set_xlabel('Time')
ax1.set_ylabel('Prey Density')
ax1.set_title('Stochastic Ensemble - Prey')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Predator
for rep in range(num_replicates):
    ax2.plot(P_stoch_ensemble[rep], 'r-', linewidth=0.5, alpha=0.3)
ax2.plot(P_det, 'b-', linewidth=3, label='Deterministic')
ax2.set_xlabel('Time')
ax2.set_ylabel('Predator Density')
ax2.set_title('Stochastic Ensemble - Predator')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

**Observations:**
- Stochasticity increases variability
- Extinction risk higher than deterministic prediction
- Chaos interacts with noise: can amplify or suppress

#### 6.2.2 Stochastic Resonance

**Phenomenon:** Noise enhances signal detection or pattern formation.

**Example:** Periodic environmental signal + noise → enhanced cycles.

```python
def ricker_with_periodic_forcing(N, P, r, alpha, K, t, period, amplitude, sigma):
    """
    Ricker model with periodic forcing and noise.
    """
    # Periodic signal (e.g., seasonal variation)
    r_forced = r + amplitude * np.sin(2 * np.pi * t / period)

    # Environmental noise
    r_noisy = r_forced + np.random.normal(0, sigma)

    N_next = N * np.exp(r_noisy * (1 - N/K - alpha*P))
    P_next = N * (1 - np.exp(-alpha * P))

    return N_next, P_next

# Simulate with different noise levels
noise_levels = [0.0, 0.05, 0.15, 0.3]
num_steps = 500

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

for idx, sigma in enumerate(noise_levels):
    N, P = 50.0, 0.5
    N_vals = np.zeros(num_steps)

    for t in range(num_steps):
        N_vals[t] = N
        N, P = ricker_with_periodic_forcing(N, P, 1.5, 0.05, 100.0,
                                           t, period=50, amplitude=0.3,
                                           sigma=sigma)

    axes[idx].plot(N_vals, 'b-', linewidth=1)
    axes[idx].set_title(f'Noise level σ = {sigma:.2f}')
    axes[idx].set_xlabel('Time')
    axes[idx].set_ylabel('Prey Density')
    axes[idx].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

**Finding:** Intermediate noise levels can optimize response to periodic signals!

### 6.3 Multi-Species Systems

#### 6.3.1 Three-Species Food Chain

**Model:**
- Resource (R) → Prey (N) → Predator (P)
- More complex dynamics: multiple attractors, strange attractors

```python
def three_species_ricker(R, N, P, r_R, r_N, alpha_RN, alpha_NP, K_R):
    """
    Three-level food chain with Ricker dynamics.

    R: Resource (e.g., plants)
    N: Prey (e.g., herbivores)
    P: Predator (e.g., carnivores)
    """
    # Resource
    R_next = R * np.exp(r_R * (1 - R/K_R - alpha_RN*N))

    # Prey
    N_next = N * np.exp(r_N * (1 - alpha_RN*R - alpha_NP*P))

    # Predator
    P_next = N * (1 - np.exp(-alpha_NP * P))

    return R_next, N_next, P_next

# Simulate
num_steps = 1000
R, N, P = 50.0, 30.0, 0.5
R_vals = np.zeros(num_steps)
N_vals = np.zeros(num_steps)
P_vals = np.zeros(num_steps)

for t in range(num_steps):
    R_vals[t], N_vals[t], P_vals[t] = R, N, P
    R, N, P = three_species_ricker(R, N, P, r_R=1.5, r_N=1.8,
                                   alpha_RN=0.01, alpha_NP=0.05, K_R=100.0)

# 3D phase space plot
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

ax.plot(R_vals, N_vals, P_vals, 'b-', linewidth=0.5, alpha=0.7)
ax.plot([R_vals[0]], [N_vals[0]], [P_vals[0]], 'go', markersize=10, label='Start')
ax.plot([R_vals[-1]], [N_vals[-1]], [P_vals[-1]], 'ro', markersize=10, label='End')

ax.set_xlabel('Resource (R)')
ax.set_ylabel('Prey (N)')
ax.set_zlabel('Predator (P)')
ax.set_title('Three-Species Food Chain Dynamics')
ax.legend()

plt.tight_layout()
plt.show()
```

**Complex phenomena:**
- **Chaos in higher dimensions**: More routes to chaos
- **Multiple attractors**: Outcome depends on initial conditions (basins)
- **Trophic cascades**: Top predator affects resource through indirect effects

#### 6.3.2 Intraguild Predation

**Model:** Predator competes with prey AND eats it.

```python
def intraguild_predation(N, P, r_N, r_P, alpha, beta, K_N, K_P):
    """
    Intraguild predation model.

    Parameters:
    -----------
    N: Prey (also competes with predator)
    P: Predator (also competes with prey)
    beta: Competition coefficient
    """
    N_next = N * np.exp(r_N * (1 - N/K_N - beta*P/K_P - alpha*P))
    P_next = P * np.exp(r_P * (1 - P/K_P - beta*N/K_N)) + N * (1 - np.exp(-alpha*P))

    return N_next, P_next

# Explore parameter space
# (code similar to bifurcation analysis above)
```

**Ecological questions:**
- When can predator and prey coexist?
- Does competition stabilize or destabilize?
- Role of intraguild predation in biodiversity

---

## 7. Conclusion

### 7.1 Key Takeaways

**1. Discrete-time models capture essential dynamics:**
- Simple difference equations produce rich behavior
- Equilibria, cycles, and chaos all possible
- Biologically relevant for many species

**2. Stability analysis reveals system behavior:**
- Linearization around equilibria (Jacobian)
- Eigenvalues determine stability
- Bifurcations mark qualitative transitions

**3. Chaos is deterministic but unpredictable:**
- Lyapunov exponents quantify sensitivity
- Long-term forecasting impossible
- Short-term patterns still exist

**4. Bifurcation diagrams map parameter space:**
- Period-doubling cascade to chaos (Feigenbaum)
- Multiple routes to chaos
- Windows of periodic behavior in chaotic regions

**5. Ecological applications are profound:**
- Population management must account for nonlinear dynamics
- Early warning signals can detect approaching regime shifts
- Climate change may push systems through bifurcations
- Spatial structure and stochasticity add complexity

**6. Computational tools enable exploration:**
- Numerical simulation for complex systems
- Visualization reveals hidden patterns
- Parameter scans identify critical thresholds

### 7.2 Connections to Broader Theory

**Mathematics:**
- Dynamical systems theory
- Nonlinear dynamics and chaos theory
- Bifurcation theory
- Stochastic processes

**Ecology:**
- Population ecology
- Community ecology
- Conservation biology
- Ecosystem dynamics

**Interdisciplinary:**
- Complex systems science
- Network theory
- Statistical physics
- Climate science

### 7.3 Further Reading

#### Foundational Texts

**Dynamical Systems and Chaos:**
1. Strogatz, S. H. (2015). *Nonlinear Dynamics and Chaos*. Westview Press.
   - Excellent introduction with biological examples

2. Devaney, R. L. (2003). *An Introduction to Chaotic Dynamical Systems*. Westview Press.
   - Rigorous mathematical treatment

3. Alligood, K. T., Sauer, T. D., & Yorke, J. A. (1996). *Chaos: An Introduction to Dynamical Systems*. Springer.
   - Comprehensive coverage with computational examples

**Ecological Applications:**
4. Hastings, A., et al. (1993). "Chaos in ecology: Is mother nature a strange attractor?" *Annual Review of Ecology and Systematics*, 24, 1-33.
   - Classic review of chaos in ecology

5. Turchin, P. (2003). *Complex Population Dynamics*. Princeton University Press.
   - Ecological time series analysis

6. Scheffer, M. (2009). *Critical Transitions in Nature and Society*. Princeton University Press.
   - Regime shifts and early warning signals

#### Research Articles

7. May, R. M. (1976). "Simple mathematical models with very complicated dynamics." *Nature*, 261, 459-467.
   - Seminal paper on chaos in logistic map

8. Ricker, W. E. (1954). "Stock and recruitment." *Journal of the Fisheries Research Board of Canada*, 11(5), 559-623.
   - Original Ricker model

9. Ives, A. R., & Jansen, V. A. (1998). "Complex dynamics in stochastic tritrophic models." *Ecology*, 79(3), 1039-1052.
   - Food chain chaos and stochasticity

10. Dakos, V., et al. (2012). "Methods for detecting early warnings of critical transitions in time series." *PLoS ONE*, 7(7), e41010.
    - Early warning signal methods

#### Online Resources

11. **Complexity Explorer** (complexityexplorer.org)
    - Free online courses on complex systems

12. **NetLogo Models Library** (ccl.northwestern.edu/netlogo/)
    - Agent-based predator-prey models

13. **Scholarpedia** (scholarpedia.org)
    - Peer-reviewed encyclopedia of dynamical systems

### 7.4 Exercises for Exploration

#### Beginner Level

**Exercise 1: Equilibrium Analysis**
- Find the coexistence equilibrium for r=2.0, α=0.05, K=100.0
- Compute the Jacobian and eigenvalues
- Determine if equilibrium is stable
- Verify by simulating from nearby initial conditions

**Exercise 2: Period Detection**
- Simulate dynamics with r=2.2
- Use autocorrelation or peak detection to find the period
- How does period change as r increases?

**Exercise 3: Phase Space Portraits**
- Create phase space plots for r = 1.0, 2.0, 2.5, 3.0
- Describe qualitative differences
- Identify attractors in each case

#### Intermediate Level

**Exercise 4: Bifurcation Diagram**
- Construct bifurcation diagram for r ∈ [0.5, 3.5]
- Identify first bifurcation point (where equilibrium loses stability)
- Find parameter values for period-4 oscillations
- Locate chaotic regions

**Exercise 5: Lyapunov Exponent Calculation**
- Compute Lyapunov exponent for r = 1.5, 2.0, 2.5, 3.0
- Compare with bifurcation diagram
- Verify that λ > 0 corresponds to chaos

**Exercise 6: Two-Parameter Analysis**
- Create 2D bifurcation diagram in (r, α) space
- Identify regions of stability, periodic, and chaotic behavior
- How does increased predation efficiency affect dynamics?

#### Advanced Level

**Exercise 7: Harvesting Optimization**
- Implement harvesting model
- Find optimal constant harvest rate that maximizes yield while maintaining stability
- Compare constant vs. periodic harvesting strategies
- Analyze sustainability under uncertainty

**Exercise 8: Stochastic Dynamics**
- Add environmental stochasticity to model
- Compare extinction probabilities for stable, periodic, and chaotic regimes
- How does noise strength affect dynamics?
- Investigate stochastic resonance with periodic forcing

**Exercise 9: Metapopulation Patterns**
- Implement spatial model with multiple patches
- Vary dispersal rate and local parameters
- Identify conditions for synchrony vs. asynchrony
- Test how spatial structure affects extinction risk

**Exercise 10: Three-Species Food Chain**
- Extend model to three trophic levels
- Explore parameter space for coexistence
- Find conditions for chaos
- Compare 2-species vs. 3-species complexity

### 7.5 Final Thoughts

The journey from simple difference equations to chaotic dynamics illustrates a profound principle: **complexity emerges from simplicity**. A predator-prey system with just two variables and a handful of parameters can produce behaviors ranging from stable equilibrium to complex chaos.

For ecologists and conservation biologists, these insights are both humbling and empowering:

**Humbling** because:
- Perfect prediction is impossible in chaotic systems
- Small uncertainties grow exponentially
- Systems can shift suddenly and unexpectedly

**Empowering** because:
- We can identify when systems approach critical transitions
- Management interventions can stabilize dynamics
- Understanding mechanisms enables adaptive strategies

As you apply these tools to real ecosystems, remember:

1. **Models are simplifications**: Real ecosystems have many more species, spatial structure, environmental variability, and evolutionary dynamics. Start simple, add complexity as needed.

2. **Data inform models**: Parameter estimation from real populations is crucial. Bayesian methods and time series analysis connect models to data.

3. **Multiple models provide perspective**: No single model is "true." Compare alternative models to understand robustness of conclusions.

4. **Communication matters**: Translate mathematical insights into actionable management recommendations. Visualizations help stakeholders understand nonlinear dynamics.

5. **Uncertainty is unavoidable**: Embrace probabilistic thinking. Focus on risk management rather than precise prediction.

The mathematical and computational tools you've learned here are foundational. They apply far beyond ecology—to epidemiology, economics, neuroscience, climate science, and more. The unifying theme is **nonlinear dynamics**: systems where small changes can have large effects, where the whole is more than the sum of parts.

Continue exploring, simulating, and questioning. The patterns you discover may reveal universal principles of complex systems, or unique features of specific ecological communities. Either way, you're contributing to our understanding of the natural world and our ability to protect it.

**Welcome to the fascinating world of nonlinear dynamics!**

---

## Appendix: Complete Python Implementation

### Full Working Code

Below is a complete, self-contained Python script implementing all major concepts:

```python
"""
Chaos and Bifurcation in Discrete Prey-Predator Models
Complete Implementation

Author: Educational Tutorial
Date: 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eig
from scipy.optimize import fsolve
from scipy.signal import find_peaks

# ============================================================================
# CORE MODEL FUNCTIONS
# ============================================================================

def ricker_prey_predator(N, P, r, alpha, K):
    """Single iteration of Ricker prey-predator model."""
    N_next = N * np.exp(r * (1 - N/K - alpha*P))
    P_next = N * (1 - np.exp(-alpha * P))
    return N_next, P_next

def simulate_dynamics(N0, P0, r, alpha, K, num_steps=500):
    """Simulate prey-predator dynamics."""
    times = np.arange(num_steps)
    N_values = np.zeros(num_steps)
    P_values = np.zeros(num_steps)

    N_values[0] = N0
    P_values[0] = P0

    for t in range(num_steps - 1):
        N_values[t+1], P_values[t+1] = ricker_prey_predator(
            N_values[t], P_values[t], r, alpha, K
        )

    return times, N_values, P_values

# ============================================================================
# EQUILIBRIUM AND STABILITY ANALYSIS
# ============================================================================

def find_coexistence_equilibrium(r, alpha, K):
    """Find coexistence equilibrium numerically."""
    def equations(state):
        N, P = state
        eq1 = r * (1 - N/K - alpha*P)
        eq2 = P - N * (1 - np.exp(-alpha * P))
        return [eq1, eq2]

    initial_guess = [K/2, 0.5]
    solution = fsolve(equations, initial_guess)

    N_star, P_star = solution

    if N_star > 0 and P_star > 0:
        return N_star, P_star
    else:
        return None, None

def compute_jacobian(N, P, r, alpha, K):
    """Compute Jacobian matrix at given point."""
    exp_term = np.exp(r * (1 - N/K - alpha*P))

    df_dN = exp_term * (1 - r*N/K - r*alpha*P)
    df_dP = -r * alpha * N * exp_term
    dg_dN = 1 - np.exp(-alpha * P)
    dg_dP = alpha * N * np.exp(-alpha * P)

    J = np.array([[df_dN, df_dP],
                  [dg_dN, dg_dP]])

    return J

def analyze_stability(N_star, P_star, r, alpha, K):
    """Analyze stability of equilibrium point."""
    J = compute_jacobian(N_star, P_star, r, alpha, K)
    eigenvalues, eigenvectors = eig(J)

    moduli = np.abs(eigenvalues)
    max_modulus = np.max(moduli)

    stable = max_modulus < 1.0

    if stable:
        if np.all(np.isreal(eigenvalues)):
            stability_type = "Stable node"
        else:
            stability_type = "Stable spiral"
    else:
        if np.all(np.isreal(eigenvalues)):
            stability_type = "Unstable node"
        else:
            stability_type = "Unstable spiral"

    return stable, eigenvalues, stability_type

# ============================================================================
# BIFURCATION ANALYSIS
# ============================================================================

def create_bifurcation_diagram(param_range, alpha, K, N0, P0,
                               variable='N', transient=500, plot_points=200):
    """Create bifurcation diagram varying growth rate r."""
    r_min, r_max = param_range
    num_params = 500
    r_values = np.linspace(r_min, r_max, num_params)

    all_r = []
    all_values = []

    for r in r_values:
        N, P = N0, P0

        for _ in range(transient):
            N, P = ricker_prey_predator(N, P, r, alpha, K)

        for _ in range(plot_points):
            N, P = ricker_prey_predator(N, P, r, alpha, K)
            if variable == 'N':
                all_values.append(N)
            else:
                all_values.append(P)
            all_r.append(r)

    return np.array(all_r), np.array(all_values)

# ============================================================================
# CHAOS ANALYSIS
# ============================================================================

def compute_lyapunov_exponent(r, alpha, K, N0, P0,
                              num_iterations=10000, transient=1000):
    """Compute largest Lyapunov exponent."""
    N, P = N0, P0

    for _ in range(transient):
        N, P = ricker_prey_predator(N, P, r, alpha, K)

    lyap_sum = 0.0

    for _ in range(num_iterations):
        J = compute_jacobian(N, P, r, alpha, K)
        eigenvalues, _ = eig(J)
        max_eigenvalue_modulus = np.max(np.abs(eigenvalues))

        if max_eigenvalue_modulus > 1e-10:
            lyap_sum += np.log(max_eigenvalue_modulus)

        N, P = ricker_prey_predator(N, P, r, alpha, K)

    return lyap_sum / num_iterations

def lyapunov_spectrum(param_range, alpha, K, N0, P0):
    """Compute Lyapunov exponent over parameter range."""
    r_min, r_max = param_range
    r_values = np.linspace(r_min, r_max, 100)
    lyapunov_values = []

    for r in r_values:
        lyap = compute_lyapunov_exponent(r, alpha, K, N0, P0)
        lyapunov_values.append(lyap)

    return r_values, np.array(lyapunov_values)

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def plot_time_series(times, N_values, P_values, title="Population Dynamics"):
    """Plot prey and predator time series."""
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(times, N_values, 'b-', linewidth=2, label='Prey (N)')
    ax.plot(times, P_values, 'r-', linewidth=2, label='Predator (P)')

    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Population Density', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig, ax

def plot_phase_space(N_values, P_values, N_star=None, P_star=None,
                     title="Phase Space Portrait"):
    """Plot phase space trajectory with equilibrium point."""
    fig, ax = plt.subplots(figsize=(8, 8))

    ax.plot(N_values, P_values, 'b-', linewidth=1.5, alpha=0.7)
    ax.plot(N_values[0], P_values[0], 'go', markersize=10, label='Start')
    ax.plot(N_values[-1], P_values[-1], 'rs', markersize=10, label='End')

    if N_star is not None and P_star is not None:
        ax.plot(N_star, P_star, 'k*', markersize=15, label='Equilibrium')

    ax.set_xlabel('Prey Density (N)', fontsize=12)
    ax.set_ylabel('Predator Density (P)', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig, ax

def plot_bifurcation_diagram(r_values, attractors, variable='N'):
    """Plot bifurcation diagram."""
    fig, ax = plt.subplots(figsize=(12, 7))

    ax.plot(r_values, attractors, 'b,', markersize=0.5, alpha=0.5)

    ax.set_xlabel('Growth Rate (r)', fontsize=12)
    ax.set_ylabel(f'{"Prey" if variable == "N" else "Predator"} Density',
                  fontsize=12)
    ax.set_title(f'Bifurcation Diagram - {variable}', fontsize=14)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig, ax

def plot_lyapunov_spectrum(r_values, lyapunov_values):
    """Plot Lyapunov exponent vs parameter."""
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(r_values, lyapunov_values, 'b-', linewidth=2)
    ax.axhline(y=0, color='r', linestyle='--', linewidth=1, label='λ = 0')

    ax.fill_between(r_values, 0, lyapunov_values,
                    where=(lyapunov_values > 0),
                    alpha=0.3, color='red', label='Chaotic (λ > 0)')

    ax.set_xlabel('Growth Rate (r)', fontsize=12)
    ax.set_ylabel('Largest Lyapunov Exponent (λ)', fontsize=12)
    ax.set_title('Lyapunov Spectrum', fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    return fig, ax

# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

def main():
    """Run complete demonstration of chaos and bifurcation analysis."""

    print("="*70)
    print("Chaos and Bifurcation in Discrete Prey-Predator Models")
    print("="*70)

    # Parameters
    r = 2.5
    alpha = 0.05
    K = 100.0
    N0, P0 = 50.0, 0.5

    print(f"\nModel Parameters:")
    print(f"  Growth rate (r): {r}")
    print(f"  Predation efficiency (α): {alpha}")
    print(f"  Carrying capacity (K): {K}")
    print(f"  Initial conditions: N0={N0}, P0={P0}")

    # 1. Simulate dynamics
    print("\n1. Simulating population dynamics...")
    times, N_vals, P_vals = simulate_dynamics(N0, P0, r, alpha, K, 500)

    # 2. Find equilibrium
    print("2. Finding coexistence equilibrium...")
    N_star, P_star = find_coexistence_equilibrium(r, alpha, K)
    if N_star:
        print(f"   Equilibrium: N* = {N_star:.3f}, P* = {P_star:.3f}")

        # 3. Stability analysis
        print("3. Analyzing stability...")
        stable, eigenvals, stab_type = analyze_stability(N_star, P_star, r, alpha, K)
        print(f"   Stability: {stab_type}")
        print(f"   Eigenvalues: {eigenvals[0]:.3f}, {eigenvals[1]:.3f}")
        print(f"   Max |λ|: {np.max(np.abs(eigenvals)):.3f}")

    # 4. Lyapunov exponent
    print("4. Computing Lyapunov exponent...")
    lyap = compute_lyapunov_exponent(r, alpha, K, N0, P0, num_iterations=5000)
    print(f"   Lyapunov exponent: {lyap:.4f}")
    if lyap > 0.01:
        print("   Status: CHAOTIC")
    elif lyap > -0.01:
        print("   Status: PERIODIC")
    else:
        print("   Status: STABLE")

    # 5. Create visualizations
    print("\n5. Creating visualizations...")

    # Time series
    plot_time_series(times, N_vals, P_vals)
    plt.savefig('time_series.png', dpi=150)
    print("   Saved: time_series.png")

    # Phase space
    plot_phase_space(N_vals, P_vals, N_star, P_star)
    plt.savefig('phase_space.png', dpi=150)
    print("   Saved: phase_space.png")

    # Bifurcation diagram
    print("   Computing bifurcation diagram (this may take a moment)...")
    r_vals, attractors = create_bifurcation_diagram(
        (0.5, 3.5), alpha, K, N0, P0, transient=500, plot_points=200
    )
    plot_bifurcation_diagram(r_vals, attractors)
    plt.savefig('bifurcation_diagram.png', dpi=150)
    print("   Saved: bifurcation_diagram.png")

    # Lyapunov spectrum
    print("   Computing Lyapunov spectrum...")
    r_lyap, lyap_vals = lyapunov_spectrum((0.5, 3.5), alpha, K, N0, P0)
    plot_lyapunov_spectrum(r_lyap, lyap_vals)
    plt.savefig('lyapunov_spectrum.png', dpi=150)
    print("   Saved: lyapunov_spectrum.png")

    print("\n" + "="*70)
    print("Analysis complete! Check the generated PNG files.")
    print("="*70)

if __name__ == "__main__":
    main()
```

### Usage Instructions

Save the complete code above as `chaos_bifurcation_tutorial.py` and run:

```bash
python chaos_bifurcation_tutorial.py
```

This will:
1. Simulate the predator-prey dynamics
2. Analyze equilibria and stability
3. Compute Lyapunov exponents
4. Generate bifurcation diagrams
5. Save all visualizations as PNG files

Modify parameters at the top of `main()` to explore different regimes!

---

*End of Tutorial*