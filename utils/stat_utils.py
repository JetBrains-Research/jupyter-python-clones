import numpy as np
import matplotlib.pyplot as plt

from typing import Tuple, Any
from pandas import DataFrame
from scipy import stats


def stats_to_distribution(stats: DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    stats_tmp = stats.groupby("min_length").mean().reset_index()

    x, y = stats_tmp.min_length.to_numpy(), stats_tmp.clones_cnt.to_numpy()
    y = y / sum(y)

    return x, y


def generate_discrete_distribution(xk, pk) -> Any:
    dist = stats.rv_discrete(name='custm', values=(xk, pk))
    return dist


def plot_statistics(
        xk_s, xk_n, pk_s, pk_n, dist_s, dist_n,
        clone_length_limits=(3, 90), size=10_000,
        save_path=None
):
    size = size
    plt.rcParams["font.family"] = "Times New Roman"

    np.random.seed(seed=42)
    Rs, Rn = dist_s.rvs(size=size), dist_n.rvs(size=size)

    width = 1
    length = 4

    q_scr = 45
    prob_scripts = np.sum([dist_s.pmf(i) for i in range(3, q_scr + 1)])
    q_ntb = np.quantile(Rn, prob_scripts)

    min_clone_length, max_clone_length = clone_length_limits

    print(f"{np.round(prob_scripts, 2)}-Quantile of scripts distribution is {q_scr}")
    print(f"{np.round(prob_scripts, 2)}-Quantile of notebooks distribution is {q_ntb}")

    cm = 1 / 2.54
    figsize = (6 * cm * 2, 6 * cm)
    fig, (ax1, ax) = plt.subplots(1, 2, figsize=figsize)

    ax.set_aspect('equal')

    ax.scatter(sorted(Rn), sorted(Rs), color='grey', alpha=0.1, edgecolors='black', s=5)
    ax.plot([0, max_clone_length + 2], [0, max_clone_length + 2], color='black', linewidth=1)

    ax.set_xlim(2, max_clone_length + 1)
    ax.set_ylim(2, max_clone_length + 1)

    ax.set_xlabel("Quantiles (Notebooks)", fontsize=12)
    ax.set_ylabel("Quantiles (Scripts)", fontsize=12)

    ax.axhline(45, color='grey', linestyle='--', dashes=(8, 8), alpha=0.5)
    ax.axvline(q_ntb, color='grey', linestyle='--', dashes=(8, 8), alpha=0.5)
    ax.scatter(q_ntb, 45, color='r', s=50, marker='s')

    ax.tick_params(direction="in", length=length, width=width, labelsize=10)
    ax.yaxis.set_ticks_position('both')
    ax.xaxis.set_ticks_position('both')

    ax.xaxis.set_ticks(list(np.arange(0, max_clone_length + 1, 90)) + [int(q_ntb)])
    ax.yaxis.set_ticks(list(np.arange(0, max_clone_length + 1, 90)) + [45])
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(width)
        ax1.spines[axis].set_linewidth(width)

    ax1.plot(xk_s, pk_s, color='b', linewidth=2, label='Scripts')
    ax1.plot(xk_n, pk_n, color='r', linewidth=2, label='Notebooks')
    legend = ax1.legend()
    legend.get_frame().set_facecolor('none')
    legend.get_frame().set_linewidth(0.0)

    ax1.tick_params(direction="in", length=length, width=width, labelsize=10)
    ax1.tick_params(direction="in", which='minor', labelsize=10)

    ax1.yaxis.set_ticks_position('both')
    ax1.xaxis.set_ticks_position('both')

    ax1.xaxis.set_ticks(list(np.arange(0, max_clone_length + 1, 45)) + [45, 54])

    ax1.set_ylabel('Probability density function', fontsize=12)
    ax1.set_xlabel('Min. duplicate length', fontsize=12)

    ax1.set_yscale('log')
    fig.tight_layout()

    ax1.text(-0.2, 1.1, '(a)', transform=ax1.transAxes, fontsize=12, weight="bold")
    ax.text(-0.2, 1.1, '(b)', transform=ax.transAxes, fontsize=12, weight="bold")

    ax1.fill_between(xk_s[45 - 3:], pk_s[45 - 3:], step="pre", alpha=0.2, color='blue')
    ax1.fill_between(xk_n[54 - 3:], pk_n[54 - 3:], step="pre", alpha=0.2, color='red')
    if save_path:
        plt.savefig(save_path / 'quantiles_distribution.pdf', dpi=200, bbox_inches='tight')

    plt.show()
