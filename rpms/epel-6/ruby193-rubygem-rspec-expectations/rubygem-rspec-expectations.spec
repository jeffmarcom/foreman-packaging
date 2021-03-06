%{!?scl:%global pkg_name %{name}}
%{?scl:%scl_package rubygem-%{gem_name}}

%global	gem_name	rspec-expectations

%global	rubyabi	1.9.1

# %%check section needs rspec, however rspec depends on rspec-expectations
%global	need_bootstrap	1

Summary:	Rspec-2 expectations (should and matchers) 
Name:		%{?scl_prefix}rubygem-%{gem_name}
Version:	2.11.1
Release:	4

Group:		Development/Languages
License:	MIT
URL:		http://github.com/rspec/rspec-expectations
Source0:	http://rubygems.org/gems/%{gem_name}-%{version}.gem

BuildRequires:	%{?scl_prefix}ruby(abi) = %{rubyabi}
BuildRequires:	%{?scl_prefix}rubygems-devel
%if 0%{?need_bootstrap} < 1
BuildRequires:	%{?scl_prefix}rubygem(rspec)
BuildRequires:	%{?scl_prefix}rubygem(minitest)
%endif
Requires:	%{?scl_prefix}ruby(abi) = %{rubyabi}
Requires:	%{?scl_prefix}rubygem(diff-lcs) >= 1.1.3
Requires:	%{?scl_prefix}rubygem(diff-lcs) < 1.2
Provides:	%{?scl_prefix}rubygem(%{gem_name}) = %{version}-%{release}
BuildArch:	noarch

%description
rspec-expectations adds `should` and `should_not` to every object and includes
RSpec::Matchers, a library of standard matchers.

%package	doc
Summary:	Documentation for %{pkg_name}
Group:		Documentation
Requires:	%{?scl_prefix}%{pkg_name} = %{version}-%{release}

%description	doc
This package contains documentation for %{pkg_name}.


%prep
%setup -q -c -T

mkdir -p .%{gem_dir}
%{?scl:scl enable %scl "}
gem install \
	-V \
	--local \
	--install-dir .%{gem_dir} \
	--force \
	--rdoc \
	%{SOURCE0}
%{?scl:"}

%build

%install
mkdir -p %{buildroot}%{gem_dir}
cp -a .%{gem_dir}/* %{buildroot}%{gem_dir}/

%if 0%{?need_bootstrap} < 1
%check
pushd .%{gem_instdir}
%{?scl:scl enable %scl "}
rspec -Ilib spec/
%{?scl:"}
popd
%endif

%files
%dir %{gem_instdir}
%doc %{gem_instdir}/License.txt
%{gem_libdir}
%exclude %{gem_instdir}/.*
%exclude %{gem_cache}
%{gem_spec}

%files	doc
%doc %{gem_instdir}/*.md
%doc %{gem_docdir}
%{gem_instdir}/features/
%{gem_instdir}/spec/

%changelog
* Fri Feb 22 2013 Miroslav Suchý <msuchy@redhat.com> 2.11.1-4
- bootstrap ruby193-rubygem-rspec-expectations (msuchy@redhat.com)

* Fri Feb 22 2013 Miroslav Suchý <msuchy@redhat.com> 2.11.1-3
- new package built with tito

* Tue Jul 24 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 2.11.1-2
- Enable tests again.

* Tue Jul 24 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 2.11.1-1
- Update to Rspec-Expectations 2.11.1.
- Specfile cleanup

* Fri Mar 30 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 2.8.0-4
- Allow tests.

* Fri Mar 30 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 2.8.0-3
- Rebuilt for scl.

* Sun Jan 21 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 2.8.0-2
- Require (diff-lcs) again

* Sun Jan 21 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 2.8.0-1
- 2.8.0

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.6.0-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon May 16 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 2.6.0-1
- 2.6.0

* Tue May 10 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 2.6.0-0.3.rc6
- 2.6.0 rc6

* Tue May  3 2011 Mamoru Tasaka <mtasaka@fedoraproject.org>
- And enable check on rawhide

* Tue May  3 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 2.6.0-0.1.rc4
- 2.6.0 rc4

* Sat Feb 26 2011 Mamoru Tasaka <mtasaka@fedoraproject.org>
- And enable check on rawhide

* Sat Feb 26 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 2.5.0-2
- Cleanups

* Thu Feb 17 2011 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 2.5.0-1
- 2.5.0

* Fri Nov 05 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 2.0.1-1
- Initial package
