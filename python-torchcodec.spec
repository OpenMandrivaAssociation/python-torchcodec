%undefine _debugsource_packages

Name:		python-torchcodec
Version:	0.16.0
Release:	1
Summary:	Decode and encode video, audio and images for PyTorch
License:	BSD-3-Clause
Group:		Development/Python
URL:		https://github.com/pytorch/torchcodec
Source0:	https://github.com/pytorch/torchcodec/archive/refs/tags/v%{version}.tar.gz#/torchcodec-%{version}.tar.gz

BuildSystem:	python
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	pkgconfig(python)
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
