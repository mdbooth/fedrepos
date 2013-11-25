Name:           fedrepos
Version:        0.2
Release:        1%{?dist}
Summary:        Update fedora yum repositories on a host to use a single source

License:        GPLv3
URL:            https://github.com/mdbooth/fedrepos
Source0:        https://github.com/mdbooth/%{name}/releases/download/v%{version}/%{name}-%{version}.tar.gz

# Only if we patch the man page. Otherwise it's included in the dist
#BuildRequires:  /usr/bin/a2x

Requires:       python-augeas


%description
Update all fedora yum repositories on a host to use a single source. The user
may specify baseurl, mirrorlist, metalink, or default, and all fedora repos will
be updated accordingly.


%prep
%setup


%build
%configure
make

# We don't need a debuginfo package
%define debug_package %{nil}


%install
rm -rf $RPM_BUILD_ROOT
%makeinstall

 
%files
%doc COPYING
%{_bindir}/fedrepos
%{_mandir}/man1/fedrepos.1.gz


%changelog
* Mon Nov 25 2013 Matthew Booth <mbooth@redhat.com> - 0.2-1
- Updated build and installation process

* Fri Nov 22 2013 Matthew Booth <mbooth@redhat.com> - 0.1-1
- Initial build
