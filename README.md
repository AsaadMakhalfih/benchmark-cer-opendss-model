Low-Voltage Distribution Network Benchmark Model

High CER Penetration Under Diverse Operating Scenarios

This repository provides a comprehensive benchmark model for low-voltage distribution networks (LVDNs) with high penetration of Consumer Energy Resources (CERs), including photovoltaic (PV) systems, battery energy storage systems (BESS), and electric vehicles (EVs). The benchmark is intended to support reproducible research, algorithm development, and comparative studies in optimisation, control, and hosting capacity analysis of LVDNs.

Reference

If you use this benchmark model in your work, please cite:

A. Makhalfih, C. Macana, R. P. Aguilera, E. Langham, and I. Anwar Ibrahim,
“A Comprehensive Benchmark Model for Low-Voltage Distribution Networks With High CER Penetration Under Diverse Operating Scenarios,”
IEEE Access, vol. 13, pp. 211845–211882, 2025.
DOI: 10.1109/ACCESS.2025.3644142

Inspiration and Acknowledgement

This work is conceptually inspired by the OpenDER project developed by the Electric Power Research Institute (EPRI):

https://github.com/epri-dev/OpenDER

The overall benchmarking philosophy and scenario-based evaluation approach are inspired by OpenDER. However, no OpenDER source code is copied directly into this repository, except where explicitly stated and where similarities arise naturally from standard modelling practices. All implementations in this repository are original and independently developed.

Repository Structure

networks/ – Low-voltage distribution network models

cer_models/ – PV, battery, and EV models

scenarios/ – Operating scenarios and uncertainty realisations

examples/ – Minimal working examples demonstrating model usage

results/ – Example outputs and visualisations

Requirements

Python 3.9+

OpenDSS (installed and accessible from the system path)

Recommended operating system: Linux or macOS (Windows supported)

Installation

It is strongly recommended to use a virtual environment.

python -m venv myvenv
source myvenv/bin/activate   # Linux/macOS
myvenv\Scripts\activate      # Windows


Install the required dependencies:

pip install -r requirements.txt

Usage

Users are encouraged to start with the examples provided in the examples/ directory. These scripts demonstrate how to:

Load the benchmark network

Instantiate CER models

Generate operating scenarios

Run power-flow and optimisation studies

Important Modelling Notes

Time step size is expressed in minutes throughout the repository.

All power values are expressed in watts (W) and volt-amperes reactive (var).

Voltage quantities follow per-phase complex representations unless otherwise stated.

Scenario generation is based on Monte Carlo sampling where applicable.

Users should ensure unit consistency when integrating custom models or datasets.

Disclaimer

This benchmark model is provided for research and educational purposes only. While care has been taken to ensure correctness, the authors make no guarantees regarding accuracy or fitness for any particular application.

License

This repository is distributed under an open-source license. See the LICENSE file for details.

