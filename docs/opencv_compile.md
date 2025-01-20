cmake -D CMAKE_BUILD_TYPE=RELEASE \
	-D CMAKE_INSTALL_PREFIX=/usr/local \
	-D INSTALL_PYTHON_EXAMPLES=ON \
	-D INSTALL_C_EXAMPLES=OFF \
	-D OPENCV_ENABLE_NONFREE=ON \
	-D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
	-D PYTHON_EXECUTABLE=~/.virtualenvs/cv/bin/python \
	-D BUILD_EXAMPLES=ON ..

nvidia-smi --query-gpu=compute_cap --format=csv

cmake \
-D WITH_CUDA=ON \
-D WITH_CUDNN=ON \
-D OPENCV_DNN_CUDA=0N \
-D CUDA_ARCH_BIN=7.5 \
-D CUDA_GENERATION=Turing  \
-D CMAKE_C_COMPILER=gcc-11 \
-D CMAKE_CXX_COMPILER=g++-11 \
-D OPENCV_EXTRA_MODULES_PATH=/home/elvin/opencv_contrib/modules/ \
-D PYTHON3_EXECUTABLE=/usr/bin/python3 \
-D PYTHON_LIBRARIES=/home/elvin/.local/lib/python3.10/site-packages ..



To verify that your newly compiled OpenCV installation supports GPU acceleration, you can follow these steps:

---

### 1. **Check Build Information**
When you compile OpenCV, the build information is included in the installed library. You can print this information from Python to check for GPU support.

#### Run the Following Code:
```python
import cv2
print(cv2.getBuildInformation())
```

#### Look for the Following Sections:
- **CUDA:** This section should say `YES` if CUDA support is enabled. For example:
  ```
  CUDA: YES
  ```
- **cuDNN:** If cuDNN support is enabled, it will also be listed.
  ```
  cuDNN: YES
  ```
- **NVIDIA GPU Architecture:** This will show the GPU architectures (e.g., `sm_50`, `sm_60`, etc.) that were targeted during compilation.

---

### 2. **Test GPU Availability in OpenCV**
You can use OpenCV's GPU module (`cv2.cuda`) to check for available GPU devices.

#### Example Code:
```python
import cv2

# Check if the CUDA module is available
if cv2.cuda.getCudaEnabledDeviceCount() > 0:
    print(f"Number of CUDA-enabled devices: {cv2.cuda.getCudaEnabledDeviceCount()}")
    print(f"CUDA Device Name: {cv2.cuda.getDevice().name()}")
else:
    print("No CUDA-enabled devices found.")
```

---

### 3. **Verify GPU Performance with a CUDA Function**
You can test GPU functionality with a CUDA-enabled operation. For example, perform a Gaussian blur using the CUDA module:

#### Example Code:
```python
import cv2
import numpy as np

# Create a random image
image = np.random.randint(0, 256, (1024, 1024), dtype=np.uint8)

# Upload the image to the GPU
gpu_image = cv2.cuda_GpuMat()
gpu_image.upload(image)

# Apply a Gaussian blur on the GPU
gpu_result = cv2.cuda.createGaussianFilter(cv2.CV_8UC1, cv2.CV_8UC1, (15, 15), 0)
result = gpu_result.apply(gpu_image)

# Download the result back to the host
host_result = result.download()
print("GPU operation completed successfully!")
```

---

### 4. **Verify CUDA Libraries**
Ensure that the necessary CUDA libraries (e.g., `libcudart`, `libcublas`) are properly linked to your OpenCV installation. Use the `ldd` command on your OpenCV library to verify:

#### Example Command:
```bash
ldd /usr/local/lib/python3.11/site-packages/cv2.cpython-<...>.so | grep cuda
```

You should see links to CUDA-related libraries such as:
```
libcudart.so
libcublas.so
libcurand.so
```

---

### 5. **Verify NVIDIA Drivers**
Ensure your system has the correct NVIDIA drivers installed to support your GPU. Use the following command to check:
```bash
nvidia-smi
```

This should display details about your GPU, including driver version and CUDA version.

---

### 6. **Rebuild if Necessary**
If GPU support is not enabled, you might need to recompile OpenCV with the correct CUDA and GPU options. Ensure:
- CUDA Toolkit is installed.
- `WITH_CUDA=ON` is passed during the `cmake` configuration step.
- `CUDA_ARCH_BIN` matches your GPU architecture.

---

By performing these checks, you can confirm whether your compiled OpenCV is GPU-enabled and functioning properly.


