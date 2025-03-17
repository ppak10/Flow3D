![pytest](https://github.com/ppak10/Flow3D/workflows/pytest/badge.svg)

# Flow3D
Python wrapper for FLOW-3D

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
### 1. Initialize Simulation folders with prepin file(s)
#### Single Simulation
```bash
python manage.py prepin
```

#### Process Map of Simulations
```bash
python manage.py prepin_process_map
```

### 2. Run Simulations
#### Run all Simulations within Workspace
```bash
python manage.py simulate_all
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
#### Prepare visualization views for all simulations within workspace
```bash
python manage.py visualize_all_prepare_views
```

#### Generate visualization views for all simulations within workspace
```bash
python manage.py visualize_all_generate_views
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
