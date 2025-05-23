![pytest](https://github.com/ppak10/Flow3D/workflows/pytest/badge.svg)

# Flow3D
Python wrapper for running and managing simulations in FLOW-3D

## Getting Started
1. Installation
```bash
pip install Flow3D
```

2. In the environment with `Flow3D` create a new `Workspace`:
```bash
flow3d-manage create_workspace test
```

3. Navigate to created workspace directory and use package with `manage.py` file.
```bash
cd out/test
```

## Workspace `manage.py` Usage
### 1. Initialize Simulation folders and `simulation.yml` file.
```bash
python manage.py simulation_init example_simulation
```

### 2. Edit generated `simulation.yml` file to your specific configurations
```yaml
# If using scientific notation, make sure to format like 1.0e+4 or 3.5e-3
# https://stackoverflow.com/a/77563328/10521456

# Global
simulation_finish_time: 0.001    # 0.001 Seconds
velocity: 0.0

# Units here are in (m)
mesh:
  size: 1.0e-5      # 10 µm resolution
  x_start: 0      # 0 µm
  x_end: 1.0e-3     # 1000 µm
  y_start: 0      # 0 µm
  y_end: 1.0e-3     # 1000 µm
  z_start: 0      # 0 µm
  z_end: 3.0e-3     # 3000 µm

fluid_region:
  x_start: 0      # 0 µm
  x_end: 1.0e-3     # 1000 µm
  y_start: 0      # 0 µm
  y_end: 1.0e-3     # 1000 µm
  z_start: 0      # 0 µm
  z_end: 2.8e-3     # 2800 µm

beam:
  diameter: 1.0e-4  # 100 µm (not explicity in prepin file)
  x: 5.0e-4         # Starting Location of Laser Beam 500 µm (0.05 cm)
  y: 5.0e-4         # Starting Location of Laser Beam 500 µm (0.05 cm)
  z: 0.01         # Starting Location of Laser Beam 10,000 µm (1.00 cm)

```

### 3. Generate prepin file from `simulation.yml`
```bash
python manage.py simulation_generate_prepin example_simulation
```

### 4. Run Simulation (and all other postprocessing and visualization steps)
```bash
python manage.py simulation_run_all example_simulation
```
  - This combines the following commands into one:

    #### 4.1. Run Simulation
    ```bash
    python manage.py simulation_run example_simulation
    ```

    #### 4.2. Postprocess Simulations
    ```bash
    python manage.py simulation_postprocess example_simulation
    ```

    #### 4.3. Visualize Simulations
    ```bash
    python manage.py simulation_visualize example_simulation num_proc=4
    ```

    #### 4.4. Generate Simulation Dataset
    ```bash
    python manage.py simulation_generate_dataset example_simulation
    ```
    #### 4.5. (upload=True) Upload Simulation and source files. (defaults to HuggingFace)
    ```bash
    python manage.py simulation_upload_dataset example_simulation
    ```

### 5. Create Workspace HuggingFace Dataset
#### Initialize a dataset for the workspace (defaults to HuggingFace)
```bash
python manage.py workspace_dataset_init
```
