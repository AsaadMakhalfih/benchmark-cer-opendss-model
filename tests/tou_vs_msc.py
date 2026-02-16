import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import matplotlib.ticker as ticker

# Time parameters (24 hours)
hours = np.arange(0, 24, 0.25)
n_points = len(hours)
dt = 0.25  # Time step in hours

pv_power = 4.0 * np.exp(-((hours - 12) ** 2) / 18)
pv_power = np.clip(pv_power, 0, None)

# Load profile (typical household with higher evening peak)
load_base = 0.8
load_power = load_base + 1.2 * np.exp(-((hours - 8) ** 2) / 8) + \
             3.0 * np.exp(-((hours - 19) ** 2) / 4)

# TOU pricing periods - charging during solar hours
charging_intervals = [(9, 15)]  # Charging during solar production
discharging_intervals = [(17, 21)]  # Discharging during peak

# Battery parameters
P_ch_max = 5  # kW
P_disch_max = 5  # kW
E_battery = 13.5  # kWh - battery capacity
SOC_min = 0.2  # Minimum SOC matches initial SOC
SOC_max = 1.0
eta_inv = 0.95  # Inverter efficiency

# Initialize arrays for both modes
msc_battery = np.zeros(n_points)
msc_soc = np.zeros(n_points)
msc_grid = np.zeros(n_points)

tou_battery = np.zeros(n_points)
tou_soc = np.zeros(n_points)
tou_grid = np.zeros(n_points)

# Initial SOC for both modes
initial_soc = 0.2
msc_soc[0] = initial_soc
tou_soc[0] = initial_soc


# Helper function to calculate available charge/discharge power based on SOC
def get_available_charge_power(soc, P_ch_max, E_battery, SOC_max):
    if soc >= SOC_max:
        return 0
    available_energy = (SOC_max - soc) * E_battery
    return min(P_ch_max, available_energy / dt)


def get_available_discharge_power(soc, P_disch_max, E_battery, SOC_min):
    if soc <= SOC_min:
        return 0
    available_energy = (soc - SOC_min) * E_battery
    return min(P_disch_max, available_energy / dt)


# ==================== Maximise Self-Consumption Mode ====================
for i in range(n_points):
    # PV power and load on DC side
    p_dc_pv = pv_power[i]
    p_dc_load = load_power[i] / eta_inv

    # Calculate surplus/deficit
    surplus = p_dc_pv - p_dc_load

    if surplus > 0:  # Surplus PV - charge battery
        P_ch_available = get_available_charge_power(msc_soc[i], P_ch_max, E_battery, SOC_max)
        p_ch = min(surplus, P_ch_available)
        msc_battery[i] = p_ch

        # Update SOC for next time step
        if i < n_points - 1:
            msc_soc[i + 1] = msc_soc[i] + (p_ch * dt) / E_battery

        # Grid export (remaining surplus after charging)
        msc_grid[i] = (surplus - p_ch) * eta_inv

    else:  # Deficit - discharge battery to meet load
        deficit = abs(surplus)  # How much power is needed
        P_disch_available = get_available_discharge_power(msc_soc[i], P_disch_max, E_battery, SOC_min)
        p_disch = min(deficit, P_disch_available)
        msc_battery[i] = -p_disch

        # Update SOC for next time step
        if i < n_points - 1:
            msc_soc[i + 1] = msc_soc[i] - (p_disch * dt) / E_battery

        # Grid import (remaining deficit after battery discharge)
        msc_grid[i] = (deficit - p_disch) * eta_inv

# ==================== TOU Mode (REPLACEMENT WITH DIAGNOSTICS) ====================
print("\n--- TOU loop debug start ---")
debug_printed = 0
stagnant_warnings = 0

for i in range(n_points):
    h = hours[i]

    # Current SOC at the start of this timestep (preserve previous step's value)
    current_soc = tou_soc[i]  # tou_soc[0] already initialised; later indexes populated as loop proceeds

    # default change in SOC this step (in fraction of capacity)
    delta_soc = 0.0

    # Check intervals (same logic)
    in_charging = any(start <= h < end for start, end in charging_intervals)
    in_discharging = any(start <= h < end for start, end in discharging_intervals)

    # Prepare diagnostic placeholders (in case not defined in a branch)
    P_ch_available = 'N/A'
    P_disch_available = 'N/A'

    if in_charging:
        # Charge battery - can use PV + grid
        P_ch_available = get_available_charge_power(current_soc, P_ch_max, E_battery, SOC_max)

        # Maximum DC power the inverter can handle (kept as you had it)
        p_dc_limit = eta_inv * 10.0

        # Allow charging from PV first; grid can top up. The actual charge power cannot exceed P_ch_available.
        # Here charging can use PV + grid, so maximum potential is PV + p_dc_limit (grid capability),
        # but final charge limited by battery availability.
        p_ch = min(pv_power[i] + p_dc_limit, P_ch_available)
        # Avoid negative charge (shouldn't happen) and numeric issues:
        p_ch = max(p_ch, 0.0)
        tou_battery[i] = p_ch

        # compute SOC delta (kW * h -> kWh, divided by battery kWh -> fraction)
        delta_soc = (p_ch * dt) / E_battery

        # Grid power (positive = import, negative = export)
        # If p_ch > pv, the difference is imported from grid; otherwise battery charges from PV (no import).
        grid_import = max(p_ch - pv_power[i], 0.0)
        tou_grid[i] = load_power[i] + grid_import * eta_inv

    elif in_discharging:
        # Discharge battery
        P_disch_available = get_available_discharge_power(current_soc, P_disch_max, E_battery, SOC_min)

        deficit = max(load_power[i] / eta_inv - pv_power[i], 0)
        p_disch = min(deficit, P_disch_available)
        p_disch = max(p_disch, 0.0)
        tou_battery[i] = -p_disch

        # compute SOC delta (negative for discharge)
        delta_soc = - (p_disch * dt) / E_battery

        # Grid import if needed (positive import)
        tou_grid[i] = max(load_power[i] - pv_power[i] * eta_inv - p_disch * eta_inv, 0)

    else:
        # Idle - no battery power change this step
        tou_battery[i] = 0
        tou_grid[i] = load_power[i] - pv_power[i] * eta_inv
        delta_soc = 0.0

    # Explicit SOC update for the next time index
    if i < n_points - 1:
        new_soc = current_soc + delta_soc

        # Clip to [SOC_min, SOC_max] (exactly as recommended)
        if new_soc > SOC_max:
            new_soc = SOC_max
        if new_soc < SOC_min:
            new_soc = SOC_min

        tou_soc[i + 1] = new_soc

    # --- Diagnostic printing: show the first few iterations and any suspicious ones ---
    if debug_printed < 6:
        print(f"i={i:02d} h={h:4.2f} pv={pv_power[i]:5.3f} load={load_power[i]:5.3f} "
              f"Pch_avail={P_ch_available if in_charging else 'N/A':>7} "
              f"Pdis_avail={P_disch_available if in_discharging else 'N/A':>7} "
              f"p_batt={tou_battery[i]:6.3f} delta_soc={delta_soc:6.4f} soc-> {current_soc:.3f} -> {tou_soc[i + 1] if i < n_points - 1 else 'END'}")
        debug_printed += 1

    # If we expected SOC to change but it didn't, print a warning line (helpful for debugging)
    if (in_charging or in_discharging) and i < n_points - 1:
        if abs(tou_soc[i + 1] - current_soc) < 1e-12:
            stagnant_warnings += 1
            if stagnant_warnings <= 10:
                print(f"  WARNING: expected SOC change at i={i} (in_charging={in_charging}, in_discharging={in_discharging}) "
                      f"but delta_soc ~ 0. Check P_ch_available and P_disch_available. "
                      f"(pv={pv_power[i]:.3f}, load={load_power[i]:.3f}, tou_batt={tou_battery[i]:.3f})")

print(f"--- TOU loop debug end (printed {debug_printed} steps, {stagnant_warnings} stagnant warnings) ---\n")

# Colors
color_pv = '#FF8C00'
color_load = '#1E90FF'
color_battery = '#32CD32'
color_charging = 'lightblue'
color_discharging = 'lightcoral'

# common fontsize
FS = 14

# ==================== FIGURE 1: Maximise Self-Consumption ====================
fig1, ax1 = plt.subplots(figsize=(10, 6))

ax1.plot(hours, pv_power, color=color_pv, linewidth=2.5, label='$p^{dc-pv}$', linestyle='-')
ax1.plot(hours, load_power, color=color_load, linewidth=2.5, label='$p^{ac-load}$', linestyle='-')
ax1.plot(hours, msc_battery, color=color_battery, linewidth=2.5,
         label='$p^{dc-battery}$', linestyle='-')

ax1.axhline(y=0, color='k', linestyle='-', linewidth=0.8, alpha=0.5)
ax1.set_xlabel('Time (hours)', fontsize=FS, fontweight='bold')
ax1.set_ylabel('Power (kW)', fontsize=FS, fontweight='bold')
ax1.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=3, fontsize=FS, frameon=False)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.set_ylim(-5, 5)
ax1.set_xlim(0, 24)
ax1.tick_params(axis='both', labelsize=FS)


def format_time(x, pos):
    h = int(x)
    m = int((x - h) * 60)
    return f"{h:02d}:{m:02d}"


ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_time))
plt.setp(ax1.get_xticklabels(), rotation=45)

# give space at top so legend isn't clipped
fig1.subplots_adjust(top=0.88)

plt.tight_layout()
output_path_msc = os.path.join(os.path.dirname(__file__), "maximise_self_consumption.pdf")
plt.savefig(output_path_msc, format='pdf', bbox_inches='tight', dpi=300)
print(f"Saved: {output_path_msc}")
plt.close()

# ==================== FIGURE 2: TOU Mode (fixed saving so legends aren't cropped) ====================
fig2, ax2 = plt.subplots(figsize=(10, 6))

# Add shaded regions for TOU periods WITHOUT labels (we'll make a separate legend)
for start, end in charging_intervals:
    ax2.axvspan(start, end, alpha=0.15, color=color_charging, zorder=0)

for start, end in discharging_intervals:
    ax2.axvspan(start, end, alpha=0.15, color=color_discharging, zorder=0)

# Plot main lines
l1, = ax2.plot(hours, pv_power, color=color_pv, linewidth=2.5, label='$p^{dc-pv}$', linestyle='-')
l2, = ax2.plot(hours, load_power, color=color_load, linewidth=2.5, label='$p^{ac-load}$', linestyle='-')
l3, = ax2.plot(hours, tou_battery, color=color_battery, linewidth=2.5,
               label='$p^{dc-battery}$', linestyle='-')

ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.8, alpha=0.5)
ax2.set_xlabel('Time (hours)', fontsize=FS, fontweight='bold')
ax2.set_ylabel('Power (kW)', fontsize=FS, fontweight='bold')

# First legend: lines (place slightly above the plot area)
lines_handles = [l1, l2, l3]
lines_labels = [h.get_label() for h in lines_handles]
legend_lines = ax2.legend(lines_handles, lines_labels,
                          loc='upper center', bbox_to_anchor=(0.5, 1.10),
                          ncol=3, fontsize=FS, frameon=False)

# Second legend: intervals (create custom patches)
charging_patch = mpatches.Patch(color=color_charging, alpha=0.15, label='Charging Interval')
discharging_patch = mpatches.Patch(color=color_discharging, alpha=0.15, label='Discharging Interval')

# Place the interval legend inside the plot at lower left to avoid overlap
legend_intervals = ax2.legend(handles=[charging_patch, discharging_patch],
                              loc='lower left', bbox_to_anchor=(0.01, 0.01),
                              ncol=2, fontsize=FS, frameon=False)

# Ensure both legends are shown
ax2.add_artist(legend_lines)
ax2.add_artist(legend_intervals)

ax2.grid(True, alpha=0.3, linestyle='--')
ax2.set_ylim(-6, 6)
ax2.set_xlim(0, 24)
ax2.tick_params(axis='both', labelsize=FS)

ax2.xaxis.set_major_formatter(ticker.FuncFormatter(format_time))
plt.setp(ax2.get_xticklabels(), rotation=45)

# Give extra space at top so the upper legend isn't clipped when displayed,
# and then tell savefig about the legend artists so bbox_inches='tight' includes them.
fig2.subplots_adjust(top=0.78)   # make room for the upper legend
plt.tight_layout()

output_path_tou = os.path.join(os.path.dirname(__file__), "time_of_use.pdf")
# pass the legend artists to bbox_extra_artists so tight bounding box includes them
fig2.savefig(output_path_tou, format='pdf', bbox_inches='tight',
             bbox_extra_artists=[legend_lines, legend_intervals], dpi=300)
print(f"Saved: {output_path_tou}")
plt.close()

print(f"Saved: {output_path_msc}")
print(f"Saved: {output_path_tou}")

# Debug: Check daytime charging for MSC
day_idx = np.where((hours >= 10) & (hours <= 14))[0]
print(f"\nMSC Daytime (10-14h) Debug:")
for idx in day_idx[::4]:  # Print every 4th point
    print(f"  Hour {hours[idx]:.1f}: SOC={msc_soc[idx]:.3f}, Battery={msc_battery[idx]:.2f} kW, PV={pv_power[idx]:.2f}, Load={load_power[idx]:.2f}")

# Debug: Check evening discharge for MSC
evening_idx = np.where((hours >= 18) & (hours <= 20))[0]
print(f"\nMSC Evening (18-20h) Debug:")
for idx in evening_idx[::4]:  # Print every 4th point
    print(f"  Hour {hours[idx]:.1f}: SOC={msc_soc[idx]:.3f}, Battery={msc_battery[idx]:.2f} kW, PV={pv_power[idx]:.2f}, Load={load_power[idx]:.2f}")
