Name:           fedrepos
Version:        0.1
Release:        1%{?dist}
Summary:        Update fedora yum repositories on a host to use a single source

License:        GPLv3
URL:            https://github.com/mdbooth/fedrepos
Source0:        fedrepos-%{version}.tar.xz

BuildRequires:  /usr/bin/a2x

Requires:       python-augeas


%description
Update all fedora yum repositories on a host to use a single source. The user
may specify baseurl, mirrorlist, metalink, or default, and all fedora repos will
be updated accordingly.


%prep
%setup


%build
a2x --doctype manpage --format manpage man/fedrepos.1.txt

# We don't need a debuginfo package
%define debug_package %{nil}


%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT/%{_bindir}
cp fedrepos.py $RPM_BUILD_ROOT/%{_bindir}/fedrepos

mkdir -p $RPM_BUILD_ROOT/%{_mandir}/man1
cp man/fedrepos.1 $RPM_BUILD_ROOT/%{_mandir}/man1/

 
%files
%doc COPYING
%{_bindir}/fedrepos
%{_mandir}/man1/fedrepos.1.gz


%changelog
* Fri Nov 22 2013 Matthew Booth <mbooth@redhat.com> = 0.1-1
- Initial build
