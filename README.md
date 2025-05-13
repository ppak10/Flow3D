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
### 3. Generate prepin file from `simulation.yml`
```bash
python manage.py simulation_generate_prepin example_simulation
```

<!-- #### Single Simulation
```bash
python manage.py prepin
``` -->

<!-- #### Process Map of Simulations
```bash
python manage.py prepin_process_map
``` -->

### 4. Run Simulation
<!-- #### Run all Simulations within Workspace
```bash
python manage.py simulate_all
``` -->
```bash
python manage.py simulation_run example_simulation
```

### 5. Postprocess Simulations
```bash
python manage.py simulation_postprocess example_simulation
```

### 6. Visualize Simulations
```bash
python manage.py simulation_visualize example_simulation num_proc=4
```

### 3. Post Process Simulations
#### Run `guipost` for all simulations within a Workspace
```bash
python manage.py post_all_run_guipost
```

#### Chunk `guipost` generated `flslnk.temp` files.
```bash
python manage.py post_all_flslnk_to_chunks
```

#### Convert chunks to npz
```bash
python manage.py post_all_flslnk_chunks_to_npz
```

### 4. Visualize Simulations
#### Prepare views for all simulations within workspace
```bash
python manage.py view_all_prepare_views num_proc=8
```

#### Generate views for all simulations within workspace
```bash
python manage.py view_all_generate_views num_proc=8
```

#### Prepare visualization views for all simulations within workspace
```bash
python manage.py visualize_all_prepare_view_visualizations
```

#### Generate visualization views for all simulations within workspace
```bash
python manage.py visualize_all_generate_views_visualizations
```

### 5. Upload Simulations to HuggingFace
#### Create HuggingFace dataset for `flslnk` dataset
```bash
python manage.py huggingface_all_create_flslnk_dataset
```

#### Upload created `flslnk` HuggingFace dataset
```bash
python manage.py huggingface_all_upload_flslnk_dataset dataset_id=<DATASET_ID>
```

#### Upload all Workspace files to HuggingFace
```bash
python manage.py huggingface_all_upload_folder dataset_id=<DATASET_ID>
```
