from __future__ import print_function  # for Python 2 compatibility
import sys
from datetime import datetime

def print_section(title):
    print("\n" + "=" * 20 + " " + title + " " + "=" * 20)

def main():
    start_time = datetime.now()

    print_section("Python Environment")
    print("Python Version: {}".format(sys.version.split()[0]))
    print("Python Path: {}".format(sys.executable))

    print_section("Deep Learning Frameworks")
    # TensorFlow
    try:
        import tensorflow as tf
        print("TensorFlow:")
        print("  Version: {}".format(tf.__version__))
        print("  GPU: {}".format("Available" if tf.config.list_physical_devices('GPU') else "Not Available"))
    except ImportError:
        print("TensorFlow: Not Installed")

    # PyTorch
    try:
        import torch
        print("\nPyTorch:")
        print("  Version: {}".format(torch.__version__))
        print("  GPU: {}".format("Available" if torch.cuda.is_available() else "Not Available"))
        print("  CUDA: {}".format(torch.version.cuda if torch.version.cuda else "Not Installed"))
        print("  Installation Path: {}".format(torch.__file__))
        print("  Build Info:")
        print("    Debug: {}".format(torch.version.debug))
        print("    Python ABI: {}".format(torch._C._PYBIND11_BUILD_ABI))
        #print("    CPU Backend: {}".format(torch.backends.cpu.get_cpu_capability()))

        if hasattr(torch.backends, 'cudnn'):
            print("  cuDNN: {}".format(
                torch.backends.cudnn.version() if torch.backends.cudnn.is_available() else "Not Installed"
            ))
    except ImportError:
        print("PyTorch: Not Installed")

    print_section("Scientific Computing Libraries")
    # NumPy
    try:
        import numpy as np
        print("NumPy Version: {}".format(np.__version__))
    except ImportError:
        print("NumPy: Not Installed")

    # Pandas
    try:
        import pandas as pd
        print("Pandas Version: {}".format(pd.__version__))
    except ImportError:
        print("Pandas: Not Installed")

    # Scikit-learn
    try:
        import sklearn
        print("Scikit-learn Version: {}".format(sklearn.__version__))
    except ImportError:
        print("Scikit-learn: Not Installed")

    print_section("System Information")
    import platform
    print("OS: {} {}".format(platform.system(), platform.release()))
    print("Architecture: {}".format(platform.machine()))

    try:
        import psutil
        mem = psutil.virtual_memory()
        print("Total Memory: {:.1f} GB".format(mem.total / (1024.0**3)))
        print("Available Memory: {:.1f} GB".format(mem.available / (1024.0**3)))
        print("CPU Cores: {}".format(psutil.cpu_count()))
    except ImportError:
        print("psutil: Not Installed")

    end_time = datetime.now()
    print("\nExecution Time: {:.2f} seconds".format((end_time - start_time).total_seconds()))

if __name__ == "__main__":
    main()