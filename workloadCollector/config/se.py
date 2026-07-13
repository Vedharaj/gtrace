import sys
import os

# Set up the paths to access gem5's configuration libraries
gem5_configs_path = "/run/media/vedha/E/gem5/configs"
sys.path.insert(0, gem5_configs_path)
sys.path.insert(0, os.path.join(gem5_configs_path, "deprecated/example"))

# Define __file__ so internal gem5 utility functions (like addToPath) resolve properly
deprecated_se_path = os.path.join(gem5_configs_path, "deprecated/example/se.py")
globals()['__file__'] = deprecated_se_path

# Read and execute the official gem5 se.py configuration
with open(deprecated_se_path, "r") as f:
    code = f.read()

exec(code, globals())
