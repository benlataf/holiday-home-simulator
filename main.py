import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from typing import Dict

# --------------------------------------------------------------------------- #
#  Fonctions utilitaires
# --------------------------------------------------------------------------- #
def monthly_payment(principal: float, annual_rate: float, years: int) -> float:
    """Mensualité constante d’un prêt amortissable."""
    r = annual_rate / 12
    n = years * 12
    return principal * r / (1 - (1 + r) ** -n)


# --------------------------------------------------------------------------- #
#  Structures de données
# --------------------------------------------------------------------------- #
@dataclass
class SimulationInput:
    # Investissement
    purchase_price: float = 120_000
    windows_cost: float = 0.0
    electricity_cost: float = 0.0
    sanitation_cost: float = 0.0
    plaster_paint_cost: float = 0.0
    insulation_cost: float = 0.0
    gas_tank_removal_cost: float = 0.0
    heating_cost: float = 0.0
    # Frais fixes annuels
    property_tax: float = 0.0          # taxe foncière
    electricity_annual: float = 0.0    # facture EDF (9 kVA)
    # Financement
    notary_rate: float = 0.075
    down_payment: float = 30_000
    loan_years: int = 20
    annual_rate: float = 0.0324
    # Location
    weekly_rent: float = 110
    weeks_rented: int = 6
    platform_fee_rate: float = 0.03
    # Fiscalité
    taxpayer_marginal_rate: float = 0.30
    social_contrib_rate: float = 0.172
    corporate_tax_rate: float = 0.15
    dividend_flat_tax_rate: float = 0.30


@dataclass
class SimulationResult:
    status: str
    gross_rent: float
    net_rent: float
    tax_due: float
    net_after_tax: float
    annual_debt_service: float
    net_cash_flow: float


# --------------------------------------------------------------------------- #
#  Calculs métier
# --------------------------------------------------------------------------- #
def simulate(inp: SimulationInput) -> Dict[str, SimulationResult]:
    """Calcule les résultats financiers pour chaque statut fiscal."""
    results: Dict[str, SimulationResult] = {}

    total_inv = (
        inp.purchase_price
        + inp.purchase_price * inp.notary_rate
        + inp.windows_cost
        + inp.electricity_cost
        + inp.sanitation_cost
        + inp.plaster_paint_cost
        + inp.insulation_cost
        + inp.gas_tank_removal_cost
        + inp.heating_cost
    )
    loan_principal = total_inv - inp.down_payment
    annual_debt = monthly_payment(loan_principal, inp.annual_rate, inp.loan_years) * 12

    gross_rent = inp.weekly_rent * inp.weeks_rented
    net_rent = gross_rent * (1 - inp.platform_fee_rate)

    annual_fixed = inp.property_tax + inp.electricity_annual

    # — LMNP Micro-BIC —
    taxable_micro = 0.5 * net_rent
    tax_micro = taxable_micro * (inp.taxpayer_marginal_rate + inp.social_contrib_rate)
    net_micro = net_rent - tax_micro
    results["LMNP_micro_BIC"] = SimulationResult(
        "LMNP Micro-BIC", gross_rent, net_rent, tax_micro, net_micro,
        annual_debt, net_micro - annual_debt - annual_fixed
    )

    # — LMNP Réel (impôt nul simplifié) —
    results["LMNP_reel"] = SimulationResult(
        "LMNP Réel", gross_rent, net_rent, 0.0, net_rent,
        annual_debt, net_rent - annual_debt - annual_fixed
    )

    # — SCI à l’IR —
    tax_ir = net_rent * (inp.taxpayer_marginal_rate + inp.social_contrib_rate)
    net_ir = net_rent - tax_ir
    results["SCI_IR"] = SimulationResult(
        "SCI à l'IR", gross_rent, net_rent, tax_ir, net_ir,
        annual_debt, net_ir - annual_debt - annual_fixed
    )

    # — SCI à l’IS —
    tax_is = net_rent * inp.corporate_tax_rate
    post_tax_is = net_rent - tax_is
    dividend_tax = post_tax_is * inp.dividend_flat_tax_rate
    net_is = post_tax_is - dividend_tax
    results["SCI_IS"] = SimulationResult(
        "SCI à l'IS", gross_rent, net_rent, tax_is + dividend_tax, net_is,
        annual_debt, net_is - annual_debt - annual_fixed
    )

    return results


# --------------------------------------------------------------------------- #
#  Interface graphique
# --------------------------------------------------------------------------- #
def run_gui() -> None:
    """GUI : deux colonnes Worst/Best, Base = moyenne."""
    root = tk.Tk()
    root.title("Simulation résidence secondaire")

    defaults = SimulationInput()

    # — Valeurs par défaut Worst / Best —
    recommended_worst = {
        "windows_cost": 5400,
        "electricity_cost": 5000,
        "sanitation_cost": 10000,
        "plaster_paint_cost": 21000,
        "insulation_cost": 4200,
        "gas_tank_removal_cost": 1500,
        "heating_cost": 12000,
        "property_tax": 600,
        "electricity_annual": 1200,
    }
    recommended_best = {
        "windows_cost": 3500,
        "electricity_cost": 3000,
        "sanitation_cost": 7000,
        "plaster_paint_cost": 14000,
        "insulation_cost": 2800,
        "gas_tank_removal_cost": 1000,
        "heating_cost": 8000,
        "property_tax": 400,
        "electricity_annual": 800,
    }

    # — Champs d’entrée —
    fields = [
        ("Prix d'achat net vendeur (€)", "purchase_price"),
        ("Huisseries / menuiseries (€)", "windows_cost"),
        ("Électricité mise aux normes (€)", "electricity_cost"),
        ("Assainissement individuel (€)", "sanitation_cost"),
        ("Plâtrerie / peintures (€)", "plaster_paint_cost"),
        ("Isolation (combles/murs) (€)", "insulation_cost"),
        ("Retrait cuve gaz (€)", "gas_tank_removal_cost"),
        ("Chauffage / PAC (€)", "heating_cost"),
        ("Taxe foncière annuelle (€)", "property_tax"),
        ("Électricité annuelle (€)", "electricity_annual"),
        ("Taux frais de notaire", "notary_rate"),
        ("Apport personnel (€)", "down_payment"),
        ("Durée du prêt (années)", "loan_years"),
        ("Taux nominal annuel", "annual_rate"),
        ("Loyer haute saison par semaine (€)", "weekly_rent"),
        ("Semaines louées par an", "weeks_rented"),
        ("Commission plateforme", "platform_fee_rate"),
        ("TMI", "taxpayer_marginal_rate"),
        ("Prélèvements sociaux", "social_contrib_rate"),
        ("Taux IS", "corporate_tax_rate"),
        ("Flat tax dividendes", "dividend_flat_tax_rate"),
    ]

    # En-têtes
    ttk.Label(root, text="Paramètre").grid(row=0, column=0, padx=5, pady=5)
    ttk.Label(root, text="Worst").grid(row=0, column=1, padx=5, pady=5)
    ttk.Label(root, text="Best").grid(row=0, column=2, padx=5, pady=5)

    vars_map: Dict[str, tk.StringVar] = {}
    int_attrs = ("loan_years", "weeks_rented")

    for i, (label, attr) in enumerate(fields, start=1):
        ttk.Label(root, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=2)
        def_val = getattr(defaults, attr)
        if attr in recommended_worst:
            var_worst = tk.StringVar(value=str(recommended_worst[attr]))
            var_best = tk.StringVar(value=str(recommended_best[attr]))
        else:
            var_worst = tk.StringVar(value=str(def_val))
            var_best = tk.StringVar(value=str(def_val))

        ttk.Entry(root, textvariable=var_worst, width=12).grid(row=i, column=1, padx=2, pady=2)
        ttk.Entry(root, textvariable=var_best, width=12).grid(row=i, column=2, padx=2, pady=2)

        vars_map[f"{attr}_worst"] = var_worst
        vars_map[f"{attr}_best"] = var_best

    # ------------------------------------------------------------ #
    def on_simulate() -> None:
        try:
            worst_kwargs, best_kwargs, base_kwargs = {}, {}, {}
            for _, attr in fields:
                w = vars_map[f"{attr}_worst"].get().replace(",", ".")
                b = vars_map[f"{attr}_best"].get().replace(",", ".")
                if attr in int_attrs:
                    vw, vb = int(float(w)), int(float(b))
                    vbase = int(round((vw + vb) / 2))
                else:
                    vw, vb = float(w), float(b)
                    vbase = (vw + vb) / 2
                worst_kwargs[attr] = vw
                best_kwargs[attr] = vb
                base_kwargs[attr] = vbase

            scenarios = {
                "Worst": SimulationInput(**worst_kwargs),
                "Base":  SimulationInput(**base_kwargs),
                "Best":  SimulationInput(**best_kwargs),
            }

            # Fenêtre résultat + rapport texte
            res_win = tk.Toplevel(root)
            res_win.title("Résultats de simulation")
            txt = tk.Text(res_win, width=115, height=42)
            report: list[str] = []

            header = f"{'Scenario':<8} | {'Statut':<15} | {'Net annuel (€)':>13} | {'Net mensuel (€)':>14} | {'Effort mensuel (€)':>17}\n"
            sep = "-" * len(header) + "\n"
            txt.insert(tk.END, header); report.append(header)
            txt.insert(tk.END, sep);    report.append(sep)

            for scen, inp in scenarios.items():
                res = simulate(inp)
                title = f"{scen} – paramètres saisis\n"
                txt.insert(tk.END, title); report.append(title)
                for lab, at in fields:
                    line = f"   {lab:<35}: {getattr(inp, at):,.0f}\n"
                    txt.insert(tk.END, line); report.append(line)
                txt.insert(tk.END, "\n");   report.append("\n")

                first = True
                for st, r in res.items():
                    eff = -r.net_cash_flow / 12 if r.net_cash_flow < 0 else 0.0
                    line = (
                        f"{scen if first else '':<8} | "
                        f"{st:<15} | {r.net_cash_flow:>13,.0f} | "
                        f"{r.net_cash_flow/12:>14,.0f} | {eff:>17,.0f}\n"
                    )
                    txt.insert(tk.END, line.replace(",", " "))
                    report.append(line.replace(",", " "))
                    first = False
                txt.insert(tk.END, "\n"); report.append("\n")

            from datetime import datetime
            fname = f"simulation_report_{datetime.now():%Y%m%d_%H%M%S}.txt"
            with open(fname, "w", encoding="utf-8") as f:
                f.writelines(report)

            from tkinter.messagebox import showinfo
            showinfo("Rapport enregistré", f"Rapport sauvegardé sous {fname}")
            txt.config(state="disabled")

        except Exception as exc:
            from tkinter.messagebox import showerror
            showerror("Erreur", str(exc))

    ttk.Button(root, text="Lancer simulation", command=on_simulate).grid(
        row=len(fields) + 1, column=0, columnspan=3, pady=10
    )

    root.mainloop()


# --------------------------------------------------------------------------- #
#  Lance l’application
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    run_gui()