%define major 1
%define libname %mklibname openshadinglanguage
%define devname %mklibname openshadinglanguage -d
%global oiio_major_minor_ver %(rpm -q --queryformat='%%{version}' %{_lib}OpenImageIO-devel | cut -d . -f 1-2)
%bcond qt6 1
%bcond python 1

Name:		openshadinglanguage
Version:	1.15.5.0
Release:	3
Summary:	Advanced shading language for production GI renderers
License:	BSD-3-Clause
Group:		System/Libraries
URL:		https://open-shading-language.readthedocs.io
Source0:	https://github.com/AcademySoftwareFoundation/OpenShadingLanguage/archive/v%{version}/%{name}-%{version}.tar.gz
Source100:	%{name}.rpmlintrc
# repo - https://github.com/AcademySoftwareFoundation/OpenShadingLanguage
Patch0:	OpenShadingLanguage-1.15.4.0-fix-install-paths.patch
Patch1:	openshadinglanguage-1.15.5.0-llvm-23.patch

BuildSystem:	cmake
BuildOption(prep):	-p1
BuildOption:	-DCMAKE_PREFIX_PATH:PATH="%{_prefix}"
BuildOption:	-DCMAKE_INSTALL_DOCDIR:PATH="%{_docdir}/%{name}"
BuildOption:	-DCMAKE_SKIP_RPATH:BOOL=TRUE
BuildOption:	-DOSL_SHADER_INSTALL_DIR:PATH="%{_datadir}/%{name}/shaders"
BuildOption:	-Dpartio_DIR:PATH="%{_prefix}"
BuildOption:	-DPARTIO_INCLUDE_DIR=%{_includedir}
BuildOption:	-DPARTIO_LIBRARIES=%{_libdir}/libpartio.so
BuildOption:	-DPYTHON_VERSION=%{pyver}
BuildOption:	-DINSTALL_DOCS:BOOL=OFF
%if %{with qt6}
BuildOption:	-DUSE_QT:BOOL=TRUE
%endif
BuildOption:	-GNinja

BuildRequires:	bison
BuildRequires:	boost-devel
BuildRequires:	cmake
BuildRequires:	cmake(clang)
BuildRequires:	cmake(Imath)
BuildRequires:	cmake(OpenImageIO)
BuildRequires:	cmake(tsl-robin-map)
BuildRequires:	flex
BuildRequires:	help2man
BuildRequires:	partio-devel
BuildRequires:	pkgconfig(pugixml)
BuildRequires:	pkgconfig(zlib)
%if %{with qt6}
BuildRequires:	cmake(Qt6)
BuildRequires:	cmake(Qt6Core)
BuildRequires:	cmake(Qt6Gui)
BuildRequires:	cmake(Qt6OpenGLWidgets)
BuildRequires:	cmake(Qt6Widgets)
%endif
%if %{with python}
BuildRequires:	cmake(pybind11)
BuildRequires:	pkgconfig(python)
BuildRequires:	python%{pyver}dist(numpy)
%endif

%global common_desc %{expand:
Open Shading Language (OSL) is a small but rich language for programmable
shading in advanced renderers and other applications, ideal for describing
materials, lights, displacement, and pattern generation.}

%description %{common_desc}

%package -n %{libname}
Summary:	OSL Libraries
Group:		System/Libraries

%description -n %{libname} %{common_desc}

%package -n %{devname}
Summary:	Development files for %{name}
Group:		Development/C++
Requires:	%{libname} = %{EVRD}

%description -n %{devname}
Development files (Headers etc.) for %{name}.

%package example-shaders-source
Summary:	OSL Shader Examples
Group:	Development/Other
BuildArch:	noarch
Requires:	%{name} = %{EVRD}
Requires:	%{name}-common-headers = %{EVRD}

%description example-shaders-source %{common_desc}
This package contains OSL example shaders.

%package common-headers
Summary:	OSL standard library and auxillary headers
Group:		Development/C++
BuildArch:	noarch
Requires:	%{name} = %{EVRD}

%description common-headers %{common_desc}
This package contains the OSL standard library headers and additional headers
useful for writing shaders.

%package -n OpenImageIO-plugin-osl
Summary:	OpenImageIO OSL input plugin
Group:	System/Libraries
Requires:	%{libname} = %{EVRD}

%description -n OpenImageIO-plugin-osl %{common_desc}
A plugin to access OSL from OpenImageIO

%if %{with python}
%package -n python-%{name}
Summary:	Pyhton bindings for OSL
Group:		Development/Python
Requires:	%{libname} = %{EVRD}

%description -n python-%{name} %{common_desc}
This package contains the python bindings for %{libname}
%endif


%install -a
# Generate and install man pages
install -d '%{buildroot}%{_mandir}/man1'
for cmd in %{buildroot}%{_bindir}/*
do
  PYTHONPATH='%{buildroot}%{python_sitearch}' \
  LD_LIBRARY_PATH='%{buildroot}%{_libdir}' \
      help2man \
      --no-info --no-discard-stderr --version-string='%{version}' \
      --output="%{buildroot}%{_mandir}/man1/$(basename "${cmd}").1" \
      "${cmd}"
done

# Remove unneeded files
rm -rf %{buildroot}%{_prefix}/build-scripts
rm -rf %{buildroot}%{_prefix}/cmake/llvm_macros.cmake

# Make the default search path for the OpenImageIO plugin if it doesnt exist.
mkdir -p %{buildroot}%{_libdir}/OpenImageIO-%{oiio_major_minor_ver}
# Move the OpenImageIO plugin into its default search path and symlink
# for compatibility
mv %{buildroot}%{_libdir}/osl.imageio.so %{buildroot}%{_libdir}/OpenImageIO-%{oiio_major_minor_ver}/
ln -s %{_libdir}/OpenImageIO-%{oiio_major_minor_ver}/osl.imageio.so \
    %{buildroot}%{_libdir}/osl.imageio.so

# Remove unneeded files
rm -rf %{buildroot}%{_datadir}/build-scripts
rm -f %{buildroot}%{_libdir}/cmake/OSL/llvm_macros.cmake

%files
%doc README.md CHANGES.md
%{_bindir}/osl{c,info}
%{_bindir}/test{render,shade,shade_dso}
%if %{with qt6}
%{_bindir}/osltoy
%endif
%{_mandir}/man1/osl{c,info}.1*
%{_mandir}/man1/test{render,shade,shade_dso}.1*
%if %{with qt6}
%{_mandir}/man1/osltoy.1*
%endif

%files example-shaders-source
%{_datadir}/%{name}/shaders/*.osl
%{_datadir}/%{name}/shaders/*.oso

%files common-headers
%dir %{_datadir}/%{name}/shaders
%{_datadir}/%{name}/shaders/*.h

%files -n OpenImageIO-plugin-osl
%license LICENSE.md
%dir %{_libdir}/OpenImageIO-%{oiio_major_minor_ver}
%{_libdir}/OpenImageIO-%{oiio_major_minor_ver}/osl.imageio.so
%{_libdir}/osl.imageio.so

%files -n %{libname}
%doc README.md CHANGES.md
%license LICENSE.md THIRD-PARTY.md
%{_libdir}/libosl*.so.%{major}*
%{_libdir}/libtestshade.so.%{major}*

%files -n %{devname}
%{_includedir}/OSL
%{_libdir}/libosl*.so
%{_libdir}/libtestshade.so
%{_libdir}/pkgconfig/osl*.pc
%{_libdir}/cmake/OSL

%if %{with python}
%files -n python-%{name}
%{python_sitearch}/oslquery
%endif
