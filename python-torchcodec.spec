%undefine _debugsource_packages

Name:		python-torchcodec
Version:	0.16.0
Release:	2
Summary:	Decode and encode video, audio and images for PyTorch
License:	BSD-3-Clause
Group:		Development/Python
URL:		https://github.com/pytorch/torchcodec
Source0:	https://github.com/pytorch/torchcodec/archive/refs/tags/v%{version}.tar.gz#/torchcodec-%{version}.tar.gz

BuildSystem:	python
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	pkgconfig(python3)
BuildRequires:	pkgconfig(libavcodec)
BuildRequires:	pkgconfig(libavformat)
BuildRequires:	pkgconfig(libavutil)
BuildRequires:	pkgconfig(libavfilter)
BuildRequires:	pkgconfig(libswscale)
BuildRequires:	pkgconfig(libswresample)
BuildRequires:	pkgconfig(libjpeg)
BuildRequires:	pkgconfig(libpng)
BuildRequires:	pkgconfig(libwebp)
BuildRequires:	cmake(libavif)
BuildRequires:	pkgconfig(libavif)
BuildRequires:	pkgconfig(libheif)
BuildRequires:	python
BuildRequires:	python%{pyver}dist(pip)
BuildRequires:	python%{pyver}dist(scikit-build-core)
BuildRequires:	python%{pyver}dist(pybind11)
BuildRequires:	python%{pyver}dist(torch)
# The ROCm torch CMake package links these imported targets. They are
# not defined until the packages are found, and torchcodec's CMake
# finds Torch before anything else.
BuildRequires:	cmake(hip)
BuildRequires:	cmake(hiprtc)
BuildRequires:	cmake(rocblas)
BuildRequires:	cmake(hipblas)
BuildRequires:	cmake(hipfft)
BuildRequires:	cmake(hiprand)
BuildRequires:	cmake(hipsparse)
BuildRequires:	cmake(rocsolver)
BuildRequires:	cmake(hipsolver)
BuildRequires:	cmake(hipblaslt)
BuildRequires:	cmake(miopen)
Requires:	python%{pyver}dist(torch)

%description
PyTorch-native media codec. Video and audio go through the system
FFmpeg (libav*); images use system libjpeg / libpng / libwebp /
libavif / libheif. Built without CUDA/nvJPEG so the same RPM works
on CPU and on the ROCm torch build.

%prep -a
# Upstream FetchContent-downloads a prebuilt libavif from S3 (no
# network on ABF, and we do not ship binaries we did not build).
# Use the system cmake(libavif) package instead.
sed -i 's|include(${CMAKE_CURRENT_SOURCE_DIR}/fetch_avif_from_s3.cmake)|find_package(libavif CONFIG REQUIRED)|' \
	src/torchcodec/_core/CMakeLists.txt
sed -i 's/libavif from S3/system libavif/' src/torchcodec/_core/CMakeLists.txt
# c10_hip / torch_hip reference hip::host and the roc* targets. Finding
# Torch first fails configure on the ROCm build.
python - <<'PY'
from pathlib import Path
p = Path("src/torchcodec/_core/CMakeLists.txt")
text = p.read_text()
old = "find_package(Torch REQUIRED)\n"
new = """# OM python-torch is the ROCm build. Import its HIP dependencies first.
find_package(hip CONFIG REQUIRED)
find_package(hiprtc CONFIG REQUIRED)
find_package(rocblas CONFIG REQUIRED)
find_package(hipblas CONFIG REQUIRED)
find_package(hipfft CONFIG REQUIRED)
find_package(hiprand CONFIG REQUIRED)
find_package(hipsparse CONFIG REQUIRED)
find_package(rocsolver CONFIG REQUIRED)
find_package(hipsolver CONFIG REQUIRED)
find_package(hipblaslt CONFIG REQUIRED)
find_package(miopen CONFIG REQUIRED)
find_package(Torch REQUIRED)
"""
if text.count(old) != 1:
    raise SystemExit(f"expected one Torch find_package, found {text.count(old)}")
p.write_text(text.replace(old, new, 1))
PY

%build -p
export BUILD_VERSION=%{version}
export ENABLE_CUDA=0
export TORCHCODEC_BUILD_NVJPEG=OFF
export TORCHCODEC_DISABLE_COMPILE_WARNING_AS_ERROR=ON
# Distro RPM: dynamically link system FFmpeg (ELF deps), do not
# download the upstream non-GPL S3 build (needs the network).
export I_CONFIRM_THIS_IS_NOT_A_LICENSE_VIOLATION=1

%files
%doc README.md
%license LICENSE
%{python_sitearch}/torchcodec
%{python_sitearch}/torchcodec-*.*-info
