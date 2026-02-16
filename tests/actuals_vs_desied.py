import os
import numpy as np
import matplotlib.pyplot as plt

# Inverter parameters (in kilo units)
S_inv = 5.0  # kVA - inverter rated apparent power
P_lim = 4.5  # kW - active power limit

# Single timestamp scenario where thermal limit is violated MORE SIGNIFICANTLY
# Desired powers BEFORE scaling
p_ac_desired = 4.2  # kW
q_ac_desired = 3.5  # kVAr (from power factor or volt-var control)

# Calculate desired apparent power (violates thermal limit)
s_desired = np.sqrt(p_ac_desired ** 2 + q_ac_desired ** 2)

print(f"Before Scaling:")
print(f"  p^ac-desired = {p_ac_desired:.2f} kW")
print(f"  q^ac-desired = {q_ac_desired:.2f} kVAr")
print(f"  s^desired = {s_desired:.2f} kVA")
print(f"  Thermal Limit (S^inv) = {S_inv:.2f} kVA")
print(f"  Violation: {s_desired:.2f} > {S_inv:.2f} → EXCEEDS LIMIT!\n")

# Scale if exceeds inverter rating (Equations 4 & 5)
if s_desired > S_inv:
    scale_factor = S_inv / s_desired
    p_actual = p_ac_desired * scale_factor
    q_actual = q_ac_desired * scale_factor
    print(f"Scaling Applied:")
    print(f"  Scale Factor = S^inv / s^desired = {S_inv:.2f} / {s_desired:.2f} = {scale_factor:.4f}")
else:
    p_actual = p_ac_desired
    q_actual = q_ac_desired

# Calculate actual apparent power
s_actual = np.sqrt(p_actual ** 2 + q_actual ** 2)

print(f"\nAfter Scaling:")
print(f"  p^actual = {p_actual:.2f} kW")
print(f"  q^actual = {q_actual:.2f} kVAr")
print(f"  s^actual = {s_actual:.2f} kVA")
print(f"  s^actual = S^inv → AT THERMAL LIMIT ✓\n")

# Create visualization
fig, ax = plt.subplots(figsize=(12, 10))

# Draw inverter capability circle
theta = np.linspace(0, 2 * np.pi, 200)
p_circle = S_inv * np.cos(theta)
q_circle = S_inv * np.sin(theta)
ax.plot(p_circle, q_circle, 'purple', linestyle='-', linewidth=3.5,
        label=f'Inverter Thermal Limit')
ax.fill(p_circle, q_circle, color='purple', alpha=0.08)


# Plot desired point (BEFORE scaling - violates limit)
ax.scatter(p_ac_desired, q_ac_desired, s=500, c='red', marker='o',
           edgecolors='darkred', linewidth=3, zorder=5,
           label=f'Desired Output')

# Plot actual point (AFTER scaling - on the limit)
ax.scatter(p_actual, q_actual, s=500, c='green', marker='s',
           edgecolors='darkgreen', linewidth=3, zorder=5,
           label=f'Actual Output')

# Draw dashed lines from axes to desired point
ax.plot([0, p_ac_desired], [q_ac_desired, q_ac_desired], 'r--', linewidth=2, alpha=0.5)
ax.plot([p_ac_desired, p_ac_desired], [0, q_ac_desired], 'r--', linewidth=2, alpha=0.5)

# Draw dashed lines from axes to actual point
ax.plot([0, p_actual], [q_actual, q_actual], 'g--', linewidth=2, alpha=0.5)
ax.plot([p_actual, p_actual], [0, q_actual], 'g--', linewidth=2, alpha=0.5)

# Add labels for desired powers
ax.text(p_ac_desired / 2, q_ac_desired + 0.15, f'$q^{{ac-desired}}$',
        fontsize=20, color='darkred', ha='center', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='lightcoral', alpha=0.8))
ax.text(p_ac_desired + 0.15, q_ac_desired / 2, f'$p^{{ac-desired}}$',
        fontsize=20, color='darkred', ha='left', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='lightcoral', alpha=0.8))

# Add labels for actual powers
ax.text(p_actual / 2, q_actual - 0.35, f'$q^{{actual}}$',
        fontsize=20, color='darkgreen', ha='center', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='lightgreen', alpha=0.8))
ax.text(p_actual - 0.55, q_actual / 2, f'$p^{{actual}}$',
        fontsize=20, color='darkgreen', ha='right', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='lightgreen', alpha=0.8))

# Draw arrow showing the scaling adjustment
ax.annotate('', xy=(p_actual, q_actual), xytext=(p_ac_desired, q_ac_desired),
            arrowprops=dict(arrowstyle='->', lw=4, color='blue',
                            connectionstyle="arc3,rad=0.2"))

# Formatting
ax.axhline(y=0, color='k', linestyle='-', linewidth=0.8, alpha=0.5)
ax.axvline(x=0, color='k', linestyle='-', linewidth=0.8, alpha=0.5)
ax.set_xlabel('Active Power, $p$ (W)', fontsize=20)
ax.set_ylabel('Reactive Power, $q$ (VAr)', fontsize=20)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.10), ncol=3, fontsize=20,
          frameon=False)
ax.grid(True, alpha=0.3, linestyle='--')
ax.axis('equal')
ax.set_xlim(-0.5, 6)
ax.set_ylim(-0.5, 6)
ax.set_xticks([])
ax.set_yticks([])

ax.tick_params(axis='both', which='major', labelsize=20)
props = dict(boxstyle='round,pad=0.6', facecolor='wheat', alpha=0.9, edgecolor='black', linewidth=2)

plt.tight_layout()
plt.savefig(os.path.dirname(__file__) + '/s_actual_vs_desired.pdf', bbox_inches='tight')
plt.show()
