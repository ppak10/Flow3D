![pytest](https://github.com/ppak10/Flow3D/workflows/pytest/badge.svg)

# Flow3D
Python wrapper for Flow3D

## `manage.py` Usage
1. Create `Job` folder:
```bash
python manage.py create_job name=SS316L_10_micron
```
2. Create `Simulations`:
```bash
python manage.py create_job_simulation_process_map job_name=SS316L_10_micron mesh_size=1E-5
```
3. Run `Simulations`:

