# Low-Voltage Distribution Network Benchmark Model

This repository provides a **benchmark model for low-voltage (LV) distribution networks** with high consumer energy resource (CER) penetration under diverse operating scenarios.  

This work is described in the following paper:

**A. Makhalfih, C. Macana, R. P. Aguilera, E. Langham, and I. Anwar Ibrahim**  
*"A Comprehensive Benchmark Model for Low-Voltage Distribution Networks With High CER Penetration Under Diverse Operating Scenarios,"*  
**IEEE Access, vol. 13, pp. 211845–211882, 2025**  
[doi:10.1109/ACCESS.2025.3644142](https://doi.org/10.1109/ACCESS.2025.3644142)

> **Note:** This work is mainly inspired by the concept of EPRI’s OpenDER project.  
> OpenDER: [https://github.com/epri-dev/OpenDER](https://github.com/epri-dev/OpenDER)  
> Only the concept was referenced; the code here is independently developed.

## Requirements

- Python 3.10 or higher
- Packages listed in `myvenv/requirements.txt`
- OpenDSS stand alone program.

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/AsaadMakhalfih/benchmark-cer-opendss-model.git
    cd <repository_folder>
    ```
2. Create a virtual environment:
    ```bash
    python -m venv myvenv
    ```
3. Activate the environment:
    ```bash
    myvenv\Scripts\activate
    ```
4. Install required packages:
    ```bash
    pip install -r myvenv/requirements.txt
    ```

## Usage

- Example scripts are provided in the `examples/` folder.
- All **time steps are in minutes**.
- All **active and reactive power values are in watts (W) and vars (VAr)**.
- Ensure your environment is activated before running any scripts.

## Notes

- The model requires the OpenDSS be installed on your computer.
- opendssdirect.py package can be an alternative to using the stand alone OpenDSS,
  however, you will need to change the COM code to opendssdirect.py format which is not difficult but might need time.
- The model is flexible and supports multiple operating scenarios.
- Carefully check **time step and power units** when integrating with other systems.
- Some simulations may take longer depending on scenario complexity.

## Citation

If you use this benchmark model in your research, please cite:
**A. Makhalfih, C. Macana, R. P. Aguilera, E. Langham, and I. Anwar Ibrahim**  
*"A Comprehensive Benchmark Model for Low-Voltage Distribution Networks With High CER Penetration Under Diverse Operating Scenarios,"*  
**IEEE Access, vol. 13, pp. 211845–211882, 2025**  
[doi:10.1109/ACCESS.2025.3644142](https://doi.org/10.1109/ACCESS.2025.3644142)
