
#!/bin/bash
# Unset any existing CUDA-related environment variables



# Set CUDA 11 environment
export CUDA_HOME=/usr/local/cuda-12.4
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
export PATH=$CUDA_HOME/bin:$PATH

# Verify the version

#$CUDA_HOME/extras/demo_suite/deviceQuery 
#$CUDA_HOME/extras/demo_suite/bandwidthTest         




nvcc --version
