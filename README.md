Voici un README.md complet que tu peux placer à la racine du dépôt :

# Simulation Résidence Secondaire

> Outil interactif (Tkinter) pour modéliser l’achat, le financement et l’exploitation locative d’une maison de vacances.  
> Il calcule automatiquement les scénarios **Worst / Base / Best**, génère un rapport texte et tient compte des régimes fiscaux (LMNP micro-BIC / réel, SCI IR / IS).

---

## Fonctionnalités

- **Entrée graphique** : saisie des paramètres d’achat, de travaux et de charges dans deux colonnes (Worst, Best) – la moyenne sert de scénario Base.  
- **Calcul financier** :  
  - coût total d’investissement (prix + frais de notaire + postes de travaux),  
  - mensualité d’emprunt,  
  - cash-flow annuel & mensuel pour chaque statut fiscal,  
  - effort d’épargne mensuel si cash-flow négatif.  
- **Rapport** : affichage dans l’interface **et** enregistrement automatique (`simulation_report_YYYYMMDD_HHMMSS.txt`).  
- **Valeurs par défaut** : montants Worst / Best pré-remplis d’après des devis moyens sur la Manche (Surtainville).  
- **Build CI** : workflow GitHub Actions pour produire un exécutable Windows (`SimulationResidence-vX.Y.Z.exe`) à chaque tag `v*`.

---

## Installation locale

```bash
git clone https://github.com/<ton-pseudo>/holiday-home-simulator.git
cd holiday-home-simulator
python -m venv venv
source venv/bin/activate          # Windows : venv\Scripts\activate
pip install -r requirements.txt
python main.py                    # lance l’interface


⸻

Dépendances

Catégorie	Librairie	Version
Interface GUI	tkinter	builtin
Build exécutable	pyinstaller	6.6.0


⸻

Utilisation
	1.	Lancement : python main.py
	2.	Saisie : renseigner (ou laisser) les montants Worst & Best.
	3.	Simulation : cliquer « Lancer simulation » :
	•	Les paramètres des trois scénarios apparaissent,
	•	Les cash-flows sont détaillés,
	•	Un fichier texte est créé dans le dossier courant.

⸻

Compilation d’un exécutable Windows

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --onefile --windowed --name SimulationResidence main.py
# résultat : dist\SimulationResidence.exe


⸻

Intégration continue

Le workflow .github/workflows/build-win.yml :
	•	se lance sur chaque tag Git v* ;
	•	construit SimulationResidence-<version>.exe avec PyInstaller ;
	•	publie l’exécutable comme artefact et l’attache à une Release GitHub.

Créer un tag :

git tag v1.0.0
git push --tags


⸻

Licence

Ce projet est placé sous la licence MIT.
© 2025 Benjamin Ménard

