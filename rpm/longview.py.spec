Name:	    longview.py	
Version:	0.0.1
Release:	7%{?dist}
Summary:	longview.py
Group:      Common
License:    BSD
BuildArch:  noarch
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

Requires:	python >= 2.4, MySQL-python

%description
longview.py


%install
cd $OLDPWD/..
rm -rf %{buildroot}
mkdir -p %{buildroot}/opt/longview_py
mkdir -p %{buildroot}/opt/longview_py/mod
mkdir -p %{buildroot}/etc/cron.d

install -p -D -m 0755 ./longview.py %{buildroot}/opt/longview_py/longview.py
install -p -D -m 0644 ./sysinfo.py %{buildroot}/opt/longview_py/sysinfo.py
install -p -D -m 0644 ./config_parser.py %{buildroot}/opt/longview_py/config_parser.py
install -p -D -m 0644 ./mod/*.py %{buildroot}/opt/longview_py/mod/
install -p -D -m 0644 ./rpm/longview_py.cron %{buildroot}/etc/cron.d/longview_py.cron
install -p -D -m 0644 ./rpm/longview_py.conf %{buildroot}/etc/longview_py.conf

%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
/opt/longview_py
/etc/cron.d/longview_py.cron
%config(noreplace) /etc/longview_py.conf

%changelog

