import os.path

import numpy as np
import matplotlib.pyplot as plt

# Parameters
E_max_kWh = 13.5
E_max_Wh = E_max_kWh
SOC_max = 1.0
eta_charger = 0.95
dt_h = 1
P_charger_fixed = 5

# Curves
soc_vals = np.linspace(0.5, 1.0, 20)
E_avail_ch_Wh = (SOC_max - soc_vals) * E_max_Wh
P_avail_ch_W = E_avail_ch_Wh / (eta_charger * dt_h)
Pch_max_W = np.minimum(P_charger_fixed, P_avail_ch_W)

plt.rcParams.update({
    "font.size": 12,
    "axes.titlesize": 12,
    "axes.labelsize": 12,
    "legend.fontsize": 10,
    "figure.dpi": 400
})

fig, ax = plt.subplots(figsize=(7, 4))

ax.plot(soc_vals, P_avail_ch_W, '-', linewidth=2, label=r'$P^{\mathrm{avail}}$')
ax.plot(soc_vals, Pch_max_W, '--', linewidth=2, label=r'$P^{ch\text{-}max}$')
ax.axhline(P_charger_fixed, linestyle=':', linewidth=2,
           label=f'Charger rating')

ax.set_xlabel('State of charge')
ax.set_ylabel('Power [kW]')
ax.set_xlim(0.5, 1)
ax.grid(True, linestyle=':', linewidth=0.5)

# legend above, horizontal
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.20), ncol=3)

plt.tight_layout()
plt.savefig(os.path.dirname(__file__) + '/Pch_max_fixed_5kW.pdf', bbox_inches='tight')
plt.show()
