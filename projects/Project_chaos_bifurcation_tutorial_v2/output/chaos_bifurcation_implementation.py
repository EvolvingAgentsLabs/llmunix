"""
Chaos and Bifurcation Analysis in Discrete Prey-Predator Models
================================================================

This module implements a comprehensive analysis toolkit for studying chaotic dynamics
and bifurcations in discrete-time prey-predator models using the Ricker formulation.

The model equations are:
    N(t+1) = N(t) * exp(r * (1 - N(t)/K - alpha*P(t)))
    P(t+1) = P(t) * exp(c * alpha * N(t) - d)

Where:
    N(t) = Prey population at time t
    P(t) = Predator population at time t
    r = Prey growth rate
    K = Prey carrying capacity
    alpha = Predation rate
    c = Conversion efficiency
    d = Predator death rate

Author: LLMunix Project
Date: 2025-09-29
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List, Dict, Optional, Callable
from dataclasses import dataclass
import warnings
from scipy.optimize import fsolve
from scipy.linalg import eig
from tqdm import tqdm
import sys

# Configure matplotlib for publication-quality figures
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['lines.linewidth'] = 2
plt.rcParams['lines.markersize'] = 6


@dataclass
class EquilibriumPoint:
    """Data class for storing equilibrium point information."""
    N: float
    P: float
    eigenvalues: np.ndarray
    stability: str
    description: str


class RickerPredatorPrey:
    """
    Ricker-type discrete prey-predator model with comprehensive analysis tools.

    This class implements the discrete-time prey-predator dynamics and provides
    methods for stability analysis, bifurcation diagrams, Lyapunov exponent
    calculation, and visualization.

    Attributes:
        r (float): Prey intrinsic growth rate
        K (float): Prey carrying capacity
        alpha (float): Predation rate coefficient
        c (float): Conversion efficiency (prey to predator)
        d (float): Predator death rate
    """

    def __init__(
        self,
        r: float = 2.5,
        K: float = 100.0,
        alpha: float = 0.01,
        c: float = 0.5,
        d: float = 0.1
    ):
        """
        Initialize the Ricker predator-prey model.

        Args:
            r: Prey growth rate (default: 2.5)
            K: Prey carrying capacity (default: 100.0)
            alpha: Predation rate (default: 0.01)
            c: Conversion efficiency (default: 0.5)
            d: Predator death rate (default: 0.1)

        Raises:
            ValueError: If any parameter is non-positive
        """
        if any(param <= 0 for param in [r, K, alpha, c, d]):
            raise ValueError("All parameters must be positive")

        self.r = r
        self.K = K
        self.alpha = alpha
        self.c = c
        self.d = d

        # Storage for simulation results
        self.time_series: Optional[np.ndarray] = None
        self.times: Optional[np.ndarray] = None

    def step(self, N: float, P: float) -> Tuple[float, float]:
        """
        Compute one time step of the model.

        Args:
            N: Current prey population
            P: Current predator population

        Returns:
            Tuple of (N_next, P_next)
        """
        # Prevent numerical overflow
        exponent_N = self.r * (1 - N/self.K - self.alpha * P)
        exponent_P = self.c * self.alpha * N - self.d

        # Clip exponents to prevent overflow
        exponent_N = np.clip(exponent_N, -20, 20)
        exponent_P = np.clip(exponent_P, -20, 20)

        N_next = N * np.exp(exponent_N)
        P_next = P * np.exp(exponent_P)

        # Ensure non-negative populations
        N_next = max(0, N_next)
        P_next = max(0, P_next)

        return N_next, P_next

    def simulate(
        self,
        N0: float,
        P0: float,
        steps: int = 1000,
        transient: int = 0
    ) -> np.ndarray:
        """
        Simulate the model for a given number of steps.

        Args:
            N0: Initial prey population
            P0: Initial predator population
            steps: Number of time steps to simulate
            transient: Number of initial steps to discard (for removing transients)

        Returns:
            Array of shape (steps, 2) containing [N, P] at each time step
        """
        total_steps = steps + transient
        trajectory = np.zeros((total_steps, 2))
        trajectory[0] = [N0, P0]

        for t in range(total_steps - 1):
            N, P = trajectory[t]
            trajectory[t + 1] = self.step(N, P)

        # Store results
        self.time_series = trajectory[transient:]
        self.times = np.arange(steps)

        return self.time_series

    def equilibria(self) -> List[EquilibriumPoint]:
        """
        Find all equilibrium points analytically and numerically.

        Returns:
            List of EquilibriumPoint objects containing equilibrium coordinates,
            eigenvalues, and stability classification
        """
        equilibria = []

        # Equilibrium 1: Extinction (0, 0)
        N1, P1 = 0.0, 0.0
        J1 = self.jacobian(N1, P1)
        evals1, _ = eig(J1)
        stab1 = self._classify_stability(evals1)
        equilibria.append(EquilibriumPoint(
            N=N1, P=P1, eigenvalues=evals1,
            stability=stab1, description="Extinction equilibrium"
        ))

        # Equilibrium 2: Predator-free (K, 0)
        N2, P2 = self.K, 0.0
        J2 = self.jacobian(N2, P2)
        evals2, _ = eig(J2)
        stab2 = self._classify_stability(evals2)
        equilibria.append(EquilibriumPoint(
            N=N2, P=P2, eigenvalues=evals2,
            stability=stab2, description="Predator-free equilibrium"
        ))

        # Equilibrium 3: Coexistence equilibrium (numerical)
        # At equilibrium: N(t+1) = N(t) and P(t+1) = P(t)
        # This gives: r * (1 - N*/K - alpha*P*) = 0
        #             c * alpha * N* - d = 0

        # From second equation: N* = d / (c * alpha)
        N_star = self.d / (self.c * self.alpha)

        # From first equation: P* = (1 - N*/K) / alpha
        if N_star < self.K:
            P_star = (1 - N_star/self.K) / self.alpha

            if P_star > 0:  # Valid coexistence equilibrium
                J3 = self.jacobian(N_star, P_star)
                evals3, _ = eig(J3)
                stab3 = self._classify_stability(evals3)
                equilibria.append(EquilibriumPoint(
                    N=N_star, P=P_star, eigenvalues=evals3,
                    stability=stab3, description="Coexistence equilibrium"
                ))

        return equilibria

    def jacobian(self, N: float, P: float) -> np.ndarray:
        """
        Compute the Jacobian matrix at a given point (N, P).

        The Jacobian matrix represents the linearization of the system
        around the point (N, P).

        Args:
            N: Prey population
            P: Predator population

        Returns:
            2x2 Jacobian matrix
        """
        # Avoid division by zero
        N = max(N, 1e-10)
        P = max(P, 1e-10)

        # Partial derivatives of N(t+1) w.r.t N and P
        exp_N = np.exp(self.r * (1 - N/self.K - self.alpha * P))

        dN_next_dN = exp_N * (1 + N * self.r * (-1/self.K))
        dN_next_dP = -N * self.alpha * self.r * exp_N

        # Partial derivatives of P(t+1) w.r.t N and P
        exp_P = np.exp(self.c * self.alpha * N - self.d)

        dP_next_dN = P * self.c * self.alpha * exp_P
        dP_next_dP = exp_P

        J = np.array([
            [dN_next_dN, dN_next_dP],
            [dP_next_dN, dP_next_dP]
        ])

        return J

    def stability_analysis(self, N: float, P: float) -> Dict[str, any]:
        """
        Perform stability analysis at a given point.

        Args:
            N: Prey population
            P: Predator population

        Returns:
            Dictionary containing:
                - jacobian: The Jacobian matrix
                - eigenvalues: Eigenvalues of the Jacobian
                - eigenvectors: Eigenvectors of the Jacobian
                - stability: Stability classification
                - details: Detailed stability information
        """
        J = self.jacobian(N, P)
        eigenvalues, eigenvectors = eig(J)
        stability = self._classify_stability(eigenvalues)

        # Compute spectral radius
        spectral_radius = np.max(np.abs(eigenvalues))

        # Detailed analysis
        details = {
            'spectral_radius': spectral_radius,
            'stable': spectral_radius < 1,
            'eigenvalue_magnitudes': np.abs(eigenvalues),
            'eigenvalue_phases': np.angle(eigenvalues)
        }

        return {
            'jacobian': J,
            'eigenvalues': eigenvalues,
            'eigenvectors': eigenvectors,
            'stability': stability,
            'details': details
        }

    def _classify_stability(self, eigenvalues: np.ndarray) -> str:
        """
        Classify stability based on eigenvalues.

        Args:
            eigenvalues: Array of eigenvalues

        Returns:
            Stability classification string
        """
        magnitudes = np.abs(eigenvalues)
        max_magnitude = np.max(magnitudes)

        if max_magnitude < 1:
            return "Stable (all |λ| < 1)"
        elif max_magnitude == 1:
            return "Marginally stable (|λ| = 1)"
        else:
            return "Unstable (some |λ| > 1)"

    def calculate_lyapunov_exponent(
        self,
        N0: float,
        P0: float,
        steps: int = 10000,
        transient: int = 1000
    ) -> float:
        """
        Calculate the largest Lyapunov exponent.

        A positive Lyapunov exponent indicates chaos, negative indicates
        convergence to a fixed point, and zero indicates periodic behavior.

        Args:
            N0: Initial prey population
            P0: Initial predator population
            steps: Number of iterations for calculation
            transient: Number of initial steps to discard

        Returns:
            Largest Lyapunov exponent
        """
        # Discard transient
        N, P = N0, P0
        for _ in range(transient):
            N, P = self.step(N, P)

        # Calculate Lyapunov exponent
        lyapunov_sum = 0.0

        for _ in range(steps):
            J = self.jacobian(N, P)
            eigenvalues, _ = eig(J)
            max_eigenvalue = np.max(np.abs(eigenvalues))

            if max_eigenvalue > 0:
                lyapunov_sum += np.log(max_eigenvalue)

            N, P = self.step(N, P)

        lyapunov_exponent = lyapunov_sum / steps

        return lyapunov_exponent

    def plot_time_series(
        self,
        N0: float = 50.0,
        P0: float = 10.0,
        steps: int = 500,
        figsize: Tuple[int, int] = (12, 6),
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Plot time series of prey and predator populations.

        Args:
            N0: Initial prey population
            P0: Initial predator population
            steps: Number of time steps
            figsize: Figure size
            save_path: Path to save figure (if provided)

        Returns:
            Matplotlib figure object
        """
        trajectory = self.simulate(N0, P0, steps)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)

        # Prey population
        ax1.plot(self.times, trajectory[:, 0], 'b-', label='Prey (N)', linewidth=2)
        ax1.set_ylabel('Prey Population', fontsize=12)
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)
        ax1.set_title(f'Time Series (r={self.r}, K={self.K}, α={self.alpha}, c={self.c}, d={self.d})',
                     fontsize=14)

        # Predator population
        ax2.plot(self.times, trajectory[:, 1], 'r-', label='Predator (P)', linewidth=2)
        ax2.set_xlabel('Time', fontsize=12)
        ax2.set_ylabel('Predator Population', fontsize=12)
        ax2.legend(loc='best')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Time series plot saved to {save_path}")

        return fig

    def plot_phase_portrait(
        self,
        initial_conditions: List[Tuple[float, float]],
        steps: int = 500,
        figsize: Tuple[int, int] = (10, 10),
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Plot phase portrait with multiple trajectories.

        Args:
            initial_conditions: List of (N0, P0) tuples
            steps: Number of time steps per trajectory
            figsize: Figure size
            save_path: Path to save figure (if provided)

        Returns:
            Matplotlib figure object
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Plot trajectories
        colors = plt.cm.viridis(np.linspace(0, 1, len(initial_conditions)))

        for i, (N0, P0) in enumerate(initial_conditions):
            trajectory = self.simulate(N0, P0, steps)
            ax.plot(trajectory[:, 0], trajectory[:, 1], '-',
                   color=colors[i], alpha=0.6, linewidth=1.5,
                   label=f'IC: ({N0:.1f}, {P0:.1f})')
            ax.plot(N0, P0, 'o', color=colors[i], markersize=8)
            ax.plot(trajectory[-1, 0], trajectory[-1, 1], 's',
                   color=colors[i], markersize=6)

        # Plot equilibria
        equilibria = self.equilibria()
        for eq in equilibria:
            marker = 'o' if 'Stable' in eq.stability else 'x'
            color = 'green' if 'Stable' in eq.stability else 'red'
            ax.plot(eq.N, eq.P, marker, color=color, markersize=12,
                   markeredgewidth=2, label=f'{eq.description} ({eq.stability})')

        ax.set_xlabel('Prey Population (N)', fontsize=12)
        ax.set_ylabel('Predator Population (P)', fontsize=12)
        ax.set_title(f'Phase Portrait (r={self.r})', fontsize=14)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=8)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Phase portrait saved to {save_path}")

        return fig

    def create_bifurcation_diagram(
        self,
        param_name: str = 'r',
        param_range: Tuple[float, float] = (1.5, 3.5),
        param_points: int = 500,
        N0: float = 50.0,
        P0: float = 10.0,
        transient: int = 2000,
        plot_points: int = 200,
        figsize: Tuple[int, int] = (14, 8),
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Create bifurcation diagram varying a parameter.

        Args:
            param_name: Name of parameter to vary ('r', 'K', 'alpha', 'c', or 'd')
            param_range: (min, max) range for parameter
            param_points: Number of parameter values to test
            N0: Initial prey population
            P0: Initial predator population
            transient: Number of steps to discard
            plot_points: Number of points to plot per parameter value
            figsize: Figure size
            save_path: Path to save figure (if provided)

        Returns:
            Matplotlib figure object
        """
        param_values = np.linspace(param_range[0], param_range[1], param_points)

        N_values = []
        P_values = []
        param_list = []

        print(f"\n{'='*60}")
        print(f"Generating Bifurcation Diagram for parameter '{param_name}'")
        print(f"Range: [{param_range[0]:.2f}, {param_range[1]:.2f}]")
        print(f"{'='*60}\n")

        original_param = getattr(self, param_name)

        for param_val in tqdm(param_values, desc="Computing bifurcation", ncols=80):
            # Set parameter
            setattr(self, param_name, param_val)

            # Simulate
            trajectory = self.simulate(N0, P0, transient + plot_points, transient)

            # Store last plot_points values
            for point in trajectory[-plot_points:]:
                N_values.append(point[0])
                P_values.append(point[1])
                param_list.append(param_val)

        # Restore original parameter
        setattr(self, param_name, original_param)

        # Create bifurcation diagram
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True)

        # Prey bifurcation
        ax1.plot(param_list, N_values, ',k', alpha=0.5, markersize=0.5)
        ax1.set_ylabel('Prey Population (N)', fontsize=12)
        ax1.set_title(f'Bifurcation Diagram: Varying {param_name}', fontsize=14)
        ax1.grid(True, alpha=0.3)

        # Predator bifurcation
        ax2.plot(param_list, P_values, ',k', alpha=0.5, markersize=0.5)
        ax2.set_xlabel(f'Parameter {param_name}', fontsize=12)
        ax2.set_ylabel('Predator Population (P)', fontsize=12)
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\n✓ Bifurcation diagram saved to {save_path}")

        return fig

    def plot_lyapunov_spectrum(
        self,
        param_name: str = 'r',
        param_range: Tuple[float, float] = (1.5, 3.5),
        param_points: int = 50,
        N0: float = 50.0,
        P0: float = 10.0,
        steps: int = 5000,
        transient: int = 1000,
        figsize: Tuple[int, int] = (12, 6),
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Plot Lyapunov exponent as a function of a parameter.

        Args:
            param_name: Name of parameter to vary
            param_range: (min, max) range for parameter
            param_points: Number of parameter values
            N0: Initial prey population
            P0: Initial predator population
            steps: Number of steps for Lyapunov calculation
            transient: Number of transient steps
            figsize: Figure size
            save_path: Path to save figure (if provided)

        Returns:
            Matplotlib figure object
        """
        param_values = np.linspace(param_range[0], param_range[1], param_points)
        lyapunov_exponents = []

        print(f"\n{'='*60}")
        print(f"Computing Lyapunov Spectrum for parameter '{param_name}'")
        print(f"Range: [{param_range[0]:.2f}, {param_range[1]:.2f}]")
        print(f"{'='*60}\n")

        original_param = getattr(self, param_name)

        for param_val in tqdm(param_values, desc="Computing Lyapunov", ncols=80):
            setattr(self, param_name, param_val)

            try:
                le = self.calculate_lyapunov_exponent(N0, P0, steps, transient)
                lyapunov_exponents.append(le)
            except:
                lyapunov_exponents.append(np.nan)

        # Restore original parameter
        setattr(self, param_name, original_param)

        # Create plot
        fig, ax = plt.subplots(figsize=figsize)

        ax.plot(param_values, lyapunov_exponents, 'b-', linewidth=2)
        ax.axhline(y=0, color='r', linestyle='--', linewidth=1, label='λ = 0 (boundary)')
        ax.fill_between(param_values, 0, lyapunov_exponents, where=np.array(lyapunov_exponents) > 0,
                        alpha=0.3, color='red', label='Chaotic regime (λ > 0)')
        ax.fill_between(param_values, lyapunov_exponents, 0, where=np.array(lyapunov_exponents) < 0,
                        alpha=0.3, color='green', label='Stable regime (λ < 0)')

        ax.set_xlabel(f'Parameter {param_name}', fontsize=12)
        ax.set_ylabel('Largest Lyapunov Exponent (λ)', fontsize=12)
        ax.set_title('Lyapunov Spectrum: Chaos Indicator', fontsize=14)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\n✓ Lyapunov spectrum saved to {save_path}")

        return fig

    def demonstrate_sensitivity(
        self,
        N0: float = 50.0,
        P0: float = 10.0,
        perturbation: float = 0.01,
        steps: int = 100,
        figsize: Tuple[int, int] = (14, 10),
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Demonstrate sensitive dependence on initial conditions (butterfly effect).

        Args:
            N0: Initial prey population
            P0: Initial predator population
            perturbation: Size of perturbation to initial conditions
            steps: Number of time steps
            figsize: Figure size
            save_path: Path to save figure (if provided)

        Returns:
            Matplotlib figure object
        """
        # Simulate original trajectory
        traj1 = self.simulate(N0, P0, steps)

        # Simulate perturbed trajectory
        traj2 = self.simulate(N0 + perturbation, P0, steps)

        # Calculate divergence
        divergence = np.sqrt((traj1[:, 0] - traj2[:, 0])**2 +
                            (traj1[:, 1] - traj2[:, 1])**2)

        # Create figure
        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

        # Time series comparison - Prey
        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(self.times, traj1[:, 0], 'b-', label=f'N₀ = {N0}', linewidth=2)
        ax1.plot(self.times, traj2[:, 0], 'r--', label=f'N₀ = {N0 + perturbation}', linewidth=2)
        ax1.set_ylabel('Prey Population', fontsize=12)
        ax1.set_title(f'Sensitivity to Initial Conditions (r={self.r})', fontsize=14)
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Time series comparison - Predator
        ax2 = fig.add_subplot(gs[1, :])
        ax2.plot(self.times, traj1[:, 1], 'b-', label=f'P₀ = {P0}', linewidth=2)
        ax2.plot(self.times, traj2[:, 1], 'r--', label=f'P₀ = {P0}', linewidth=2)
        ax2.set_ylabel('Predator Population', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Divergence
        ax3 = fig.add_subplot(gs[2, 0])
        ax3.semilogy(self.times, divergence + 1e-10, 'g-', linewidth=2)
        ax3.set_xlabel('Time', fontsize=12)
        ax3.set_ylabel('Euclidean Distance', fontsize=12)
        ax3.set_title('Trajectory Divergence (log scale)', fontsize=12)
        ax3.grid(True, alpha=0.3)

        # Phase portrait comparison
        ax4 = fig.add_subplot(gs[2, 1])
        ax4.plot(traj1[:, 0], traj1[:, 1], 'b-', alpha=0.6, linewidth=2, label='Original')
        ax4.plot(traj2[:, 0], traj2[:, 1], 'r--', alpha=0.6, linewidth=2, label='Perturbed')
        ax4.plot(N0, P0, 'bo', markersize=10, label='IC₁')
        ax4.plot(N0 + perturbation, P0, 'ro', markersize=10, label='IC₂')
        ax4.set_xlabel('Prey Population', fontsize=12)
        ax4.set_ylabel('Predator Population', fontsize=12)
        ax4.set_title('Phase Space Comparison', fontsize=12)
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Sensitivity analysis saved to {save_path}")

        return fig

    def compare_dynamical_regimes(
        self,
        stable_r: float = 1.8,
        periodic_r: float = 2.3,
        chaotic_r: float = 2.9,
        N0: float = 50.0,
        P0: float = 10.0,
        steps: int = 300,
        figsize: Tuple[int, int] = (18, 12),
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Compare stable, periodic, and chaotic dynamical regimes.

        Args:
            stable_r: Parameter value for stable regime
            periodic_r: Parameter value for periodic regime
            chaotic_r: Parameter value for chaotic regime
            N0: Initial prey population
            P0: Initial predator population
            steps: Number of time steps
            figsize: Figure size
            save_path: Path to save figure (if provided)

        Returns:
            Matplotlib figure object
        """
        original_r = self.r

        # Simulate three regimes
        regimes = [
            ('Stable', stable_r, 'blue'),
            ('Periodic', periodic_r, 'orange'),
            ('Chaotic', chaotic_r, 'red')
        ]

        trajectories = []
        lyapunov_exponents = []

        for name, r_val, _ in regimes:
            self.r = r_val
            traj = self.simulate(N0, P0, steps)
            trajectories.append(traj)

            le = self.calculate_lyapunov_exponent(N0, P0, steps=5000, transient=1000)
            lyapunov_exponents.append(le)

        # Create comprehensive comparison figure
        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        for i, ((name, r_val, color), traj, le) in enumerate(zip(regimes, trajectories, lyapunov_exponents)):
            # Time series
            ax_time = fig.add_subplot(gs[i, 0])
            ax_time.plot(range(steps), traj[:, 0], color=color, alpha=0.7, linewidth=1.5, label='Prey')
            ax_time.plot(range(steps), traj[:, 1], color=color, alpha=0.7, linewidth=1.5,
                        linestyle='--', label='Predator')
            ax_time.set_title(f'{name} (r={r_val}, λ={le:.4f})', fontsize=11)
            ax_time.set_ylabel('Population', fontsize=10)
            if i == 2:
                ax_time.set_xlabel('Time', fontsize=10)
            ax_time.legend(fontsize=8)
            ax_time.grid(True, alpha=0.3)

            # Phase portrait
            ax_phase = fig.add_subplot(gs[i, 1])
            ax_phase.plot(traj[:, 0], traj[:, 1], color=color, alpha=0.6, linewidth=1.5)
            ax_phase.plot(N0, P0, 'o', color=color, markersize=8, label='Start')
            ax_phase.plot(traj[-1, 0], traj[-1, 1], 's', color=color, markersize=8, label='End')
            ax_phase.set_title(f'Phase Portrait', fontsize=11)
            ax_phase.set_ylabel('Predator (P)', fontsize=10)
            if i == 2:
                ax_phase.set_xlabel('Prey (N)', fontsize=10)
            ax_phase.legend(fontsize=8)
            ax_phase.grid(True, alpha=0.3)

            # Return map (Poincaré section) - using prey maxima
            ax_return = fig.add_subplot(gs[i, 2])

            # Find local maxima in prey population
            prey = traj[:, 0]
            maxima_indices = []
            for j in range(1, len(prey) - 1):
                if prey[j] > prey[j-1] and prey[j] > prey[j+1]:
                    maxima_indices.append(j)

            if len(maxima_indices) > 1:
                maxima_values = prey[maxima_indices]
                ax_return.plot(maxima_values[:-1], maxima_values[1:], 'o',
                             color=color, alpha=0.6, markersize=4)

                # Add identity line
                max_val = np.max(maxima_values)
                ax_return.plot([0, max_val], [0, max_val], 'k--', alpha=0.3, linewidth=1)

            ax_return.set_title('Return Map (Prey Maxima)', fontsize=11)
            ax_return.set_ylabel('N(t+1)', fontsize=10)
            if i == 2:
                ax_return.set_xlabel('N(t)', fontsize=10)
            ax_return.grid(True, alpha=0.3)

        fig.suptitle('Comparison of Dynamical Regimes', fontsize=16, y=0.995)

        # Restore original r
        self.r = original_r

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Regime comparison saved to {save_path}")

        return fig


def print_analysis_header(title: str):
    """Print a formatted analysis section header."""
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print(f"{'='*80}\n")


def print_equilibrium_analysis(model: RickerPredatorPrey):
    """Print detailed equilibrium analysis."""
    print_analysis_header("EQUILIBRIUM ANALYSIS")

    equilibria = model.equilibria()

    for i, eq in enumerate(equilibria, 1):
        print(f"Equilibrium {i}: {eq.description}")
        print(f"  Coordinates: N* = {eq.N:.6f}, P* = {eq.P:.6f}")
        print(f"  Eigenvalues: λ₁ = {eq.eigenvalues[0]:.6f}, λ₂ = {eq.eigenvalues[1]:.6f}")
        print(f"  Magnitudes: |λ₁| = {abs(eq.eigenvalues[0]):.6f}, |λ₂| = {abs(eq.eigenvalues[1]):.6f}")
        print(f"  Stability: {eq.stability}")
        print()


def print_parameter_summary(model: RickerPredatorPrey):
    """Print model parameters."""
    print_analysis_header("MODEL PARAMETERS")

    print(f"  Prey growth rate (r):      {model.r}")
    print(f"  Carrying capacity (K):     {model.K}")
    print(f"  Predation rate (α):        {model.alpha}")
    print(f"  Conversion efficiency (c): {model.c}")
    print(f"  Predator death rate (d):   {model.d}")
    print()


def main():
    """
    Main demonstration function.

    Generates comprehensive analysis with 10+ publication-quality figures
    showing stable, periodic, and chaotic regimes.
    """
    print("\n" + "="*80)
    print(" "*20 + "CHAOS AND BIFURCATION ANALYSIS")
    print(" "*15 + "Discrete Prey-Predator Models (Ricker Type)")
    print("="*80 + "\n")

    # Output directory
    output_dir = "C:/projects/evolving-agents-labs/llmunix/projects/Project_chaos_bifurcation_tutorial_v2/output"

    # =========================================================================
    # STABLE REGIME (r = 1.8)
    # =========================================================================
    print_analysis_header("REGIME 1: STABLE DYNAMICS (r = 1.8)")

    model_stable = RickerPredatorPrey(r=1.8, K=100.0, alpha=0.01, c=0.5, d=0.1)
    print_parameter_summary(model_stable)
    print_equilibrium_analysis(model_stable)

    # Calculate Lyapunov exponent
    le_stable = model_stable.calculate_lyapunov_exponent(50.0, 10.0, steps=5000, transient=1000)
    print(f"Largest Lyapunov Exponent: λ = {le_stable:.6f}")
    print(f"Interpretation: {'Stable (convergence to equilibrium)' if le_stable < 0 else 'Not stable'}\n")

    # Generate figures for stable regime
    print("Generating figures for stable regime...")

    fig1 = model_stable.plot_time_series(
        N0=50, P0=10, steps=500,
        save_path=f"{output_dir}/fig01_stable_time_series.png"
    )
    plt.close(fig1)

    fig2 = model_stable.plot_phase_portrait(
        initial_conditions=[(30, 5), (50, 10), (70, 15), (90, 20)],
        steps=500,
        save_path=f"{output_dir}/fig02_stable_phase_portrait.png"
    )
    plt.close(fig2)

    fig3 = model_stable.demonstrate_sensitivity(
        N0=50, P0=10, perturbation=0.01, steps=200,
        save_path=f"{output_dir}/fig03_stable_sensitivity.png"
    )
    plt.close(fig3)

    # =========================================================================
    # PERIODIC REGIME (r = 2.3)
    # =========================================================================
    print_analysis_header("REGIME 2: PERIODIC DYNAMICS (r = 2.3)")

    model_periodic = RickerPredatorPrey(r=2.3, K=100.0, alpha=0.01, c=0.5, d=0.1)
    print_parameter_summary(model_periodic)
    print_equilibrium_analysis(model_periodic)

    le_periodic = model_periodic.calculate_lyapunov_exponent(50.0, 10.0, steps=5000, transient=1000)
    print(f"Largest Lyapunov Exponent: λ = {le_periodic:.6f}")
    print(f"Interpretation: {'Periodic oscillations' if abs(le_periodic) < 0.01 else 'Other dynamics'}\n")

    print("Generating figures for periodic regime...")

    fig4 = model_periodic.plot_time_series(
        N0=50, P0=10, steps=500,
        save_path=f"{output_dir}/fig04_periodic_time_series.png"
    )
    plt.close(fig4)

    fig5 = model_periodic.plot_phase_portrait(
        initial_conditions=[(30, 5), (50, 10), (70, 15), (90, 20)],
        steps=500,
        save_path=f"{output_dir}/fig05_periodic_phase_portrait.png"
    )
    plt.close(fig5)

    fig6 = model_periodic.demonstrate_sensitivity(
        N0=50, P0=10, perturbation=0.01, steps=200,
        save_path=f"{output_dir}/fig06_periodic_sensitivity.png"
    )
    plt.close(fig6)

    # =========================================================================
    # CHAOTIC REGIME (r = 2.9)
    # =========================================================================
    print_analysis_header("REGIME 3: CHAOTIC DYNAMICS (r = 2.9)")

    model_chaotic = RickerPredatorPrey(r=2.9, K=100.0, alpha=0.01, c=0.5, d=0.1)
    print_parameter_summary(model_chaotic)
    print_equilibrium_analysis(model_chaotic)

    le_chaotic = model_chaotic.calculate_lyapunov_exponent(50.0, 10.0, steps=5000, transient=1000)
    print(f"Largest Lyapunov Exponent: λ = {le_chaotic:.6f}")
    print(f"Interpretation: {'CHAOTIC (sensitive dependence on initial conditions)' if le_chaotic > 0 else 'Not chaotic'}\n")

    print("Generating figures for chaotic regime...")

    fig7 = model_chaotic.plot_time_series(
        N0=50, P0=10, steps=500,
        save_path=f"{output_dir}/fig07_chaotic_time_series.png"
    )
    plt.close(fig7)

    fig8 = model_chaotic.plot_phase_portrait(
        initial_conditions=[(30, 5), (50, 10), (70, 15), (90, 20)],
        steps=500,
        save_path=f"{output_dir}/fig08_chaotic_phase_portrait.png"
    )
    plt.close(fig8)

    fig9 = model_chaotic.demonstrate_sensitivity(
        N0=50, P0=10, perturbation=0.01, steps=200,
        save_path=f"{output_dir}/fig09_chaotic_sensitivity.png"
    )
    plt.close(fig9)

    # =========================================================================
    # COMPARATIVE ANALYSIS
    # =========================================================================
    print_analysis_header("COMPARATIVE ANALYSIS: ALL REGIMES")

    fig10 = model_chaotic.compare_dynamical_regimes(
        stable_r=1.8, periodic_r=2.3, chaotic_r=2.9,
        N0=50, P0=10, steps=300,
        save_path=f"{output_dir}/fig10_regime_comparison.png"
    )
    plt.close(fig10)

    # =========================================================================
    # BIFURCATION ANALYSIS
    # =========================================================================
    print_analysis_header("BIFURCATION ANALYSIS")

    model_bifurcation = RickerPredatorPrey(r=2.5, K=100.0, alpha=0.01, c=0.5, d=0.1)

    fig11 = model_bifurcation.create_bifurcation_diagram(
        param_name='r',
        param_range=(1.5, 3.5),
        param_points=500,
        N0=50, P0=10,
        transient=2000,
        plot_points=200,
        save_path=f"{output_dir}/fig11_bifurcation_diagram.png"
    )
    plt.close(fig11)

    # =========================================================================
    # LYAPUNOV SPECTRUM
    # =========================================================================
    print_analysis_header("LYAPUNOV SPECTRUM ANALYSIS")

    fig12 = model_bifurcation.plot_lyapunov_spectrum(
        param_name='r',
        param_range=(1.5, 3.5),
        param_points=50,
        N0=50, P0=10,
        steps=5000,
        transient=1000,
        save_path=f"{output_dir}/fig12_lyapunov_spectrum.png"
    )
    plt.close(fig12)

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print_analysis_header("ANALYSIS COMPLETE")

    print("Generated Figures:")
    print("  [1] Stable regime - Time series")
    print("  [2] Stable regime - Phase portrait")
    print("  [3] Stable regime - Sensitivity analysis")
    print("  [4] Periodic regime - Time series")
    print("  [5] Periodic regime - Phase portrait")
    print("  [6] Periodic regime - Sensitivity analysis")
    print("  [7] Chaotic regime - Time series")
    print("  [8] Chaotic regime - Phase portrait")
    print("  [9] Chaotic regime - Sensitivity analysis")
    print(" [10] Comparative analysis - All regimes")
    print(" [11] Bifurcation diagram")
    print(" [12] Lyapunov spectrum")
    print()

    print("Summary of Dynamical Regimes:")
    print(f"  Stable (r=1.8):   λ = {le_stable:+.6f} → Convergence to equilibrium")
    print(f"  Periodic (r=2.3): λ = {le_periodic:+.6f} → Limit cycles")
    print(f"  Chaotic (r=2.9):  λ = {le_chaotic:+.6f} → Deterministic chaos")
    print()

    print(f"All figures saved to: {output_dir}")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)