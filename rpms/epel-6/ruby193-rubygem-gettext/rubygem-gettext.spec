%{?scl:%scl_package rubygem-%{gem_name}}
%{!?scl:%global pkg_name %{name}}

%global		rubyabi		1.9.1
%global		ruby19          1

%global		gem_name	gettext

%global		locale_ver		2.0.5
%global		repoid			67096

Name:		%{?scl_prefix}rubygem-%{gem_name}
Version:	2.3.7
Release:	4%{?dist}
Summary:	RubyGem of Localization Library and Tools for Ruby
Group:		Development/Languages

License:	Ruby
URL:		http://www.yotabanana.com/hiki/ruby-gettext.html?ruby-gettext
Source0:	http://gems.rubyforge.org/gems/%{gem_name}-%{version}.gem
#Source0:	http://rubyforge.org/frs/download.php/%{repoid}/%{gem_name}-%{version}.gem
# For test-unit 2.4.5 (latest test-unit is 2.5.3:
# please remove Patch0 after updating test-unit)
Patch0:	rubygem-gettext-2.3.6-old-test-unit.patch

BuildRequires:	%{?scl_prefix}ruby(abi) = %{rubyabi}
BuildRequires:	%{?scl_prefix}rubygems-devel
BuildRequires:	%{?scl_prefix}rubygem(locale) >= %{locale_ver}
# Disable tests
## For %%check
#BuildRequires:	%{?scl_prefix}rubygem(test-unit)
#BuildRequires:	%{?scl_prefix}rubygem(test-unit-notify)
#BuildRequires:	%{?scl_prefix}rubygem(test-unit-rr)
#BuildRequires:	%{?scl_prefix}rubygem(levenshtein)
BuildRequires:	gettext

Requires:	%{?scl_prefix}ruby(abi) = %{rubyabi}
Requires:	%{?scl_prefix}ruby(rubygems)
Requires:	%{?scl_prefix}rubygem(locale) >= %{locale_ver}
Requires:	%{?scl_prefix}rubygem(levenshtein)
Requires:	%{?scl_prefix}irb
Provides:	%{?scl_prefix}rubygem(%{gem_name}) = %{version}-%{release}

Obsoletes:	%{?scl_prefix}ruby-gettext-package <= %{version}-%{release}
Provides:	%{?scl_prefix}ruby-gettext-package = %{version}-%{release}

BuildArch:	noarch

%description
Ruby-GetText-Package is a GNU GetText-like program for Ruby. 
The catalog file(po-file) is same format with GNU GetText. 
So you can use GNU GetText tools for maintaining.

This package provides gem for Ruby-Gettext-Package.

%package	doc
Summary:	Documentation for %{pkg_name}
Group:		Documentation
Requires:	%{?scl_prefix}%{pkg_name} = %{version}-%{release}

%description	doc
This package contains documentation for %{pkg_name}.


%prep
%setup -n %{pkg_name}-%{version} -q -c -T

TOPDIR=$(pwd)
mkdir tmpunpackdir
pushd tmpunpackdir

%{?scl:scl enable %{scl} "}
gem unpack %{SOURCE0}
%{?scl:"}
cd %{gem_name}-%{version}

#Patches, etc
%patch0 -p0

%{?scl:scl enable %{scl} "}
gem specification -l --ruby %{SOURCE0}
%{?scl:"} > %{gem_name}.gemspec

%{?scl:scl enable %{scl} "}
gem build %{gem_name}.gemspec
%{?scl:"}
mv %{gem_name}-%{version}.gem $TOPDIR

popd
rm -rf tmpunpackdir

%build
mkdir -p .%{gem_dir}
%{?scl:scl enable %{scl} "}
gem install \
	--local \
	--install-dir .%{gem_dir} \
	--force \
	--rdoc \
	-V \
	%{gem_name}-%{version}.gem
%{?scl:"}

#%%{__rm} -f .%{gem_instdir}/Rakefile
%{__rm} -f .%{gem_instdir}/%{gem_name}.gemspec
%{__rm} -f .%{gem_instdir}/replace.rb
%{__rm} -rf .%{gem_instdir}/po/
%{__rm} -rf .%{gem_dir}/bin/
%{__chmod} 0755 .%{gem_instdir}/bin/*
%{__chmod} 0644 .%{gem_dir}/cache/*.gem
find .%{gem_instdir}/ -name \*.po | xargs %{__chmod} 0644

# Cleanups for rpmlint
find .%{gem_instdir}/lib/ -name \*.rb | while read f
do
	%{__sed} -i -e '/^#!/d' $f
done

# fix timestamps
find . -type f -print0 | xargs -0 touch -r %{SOURCE0}

%install
%{__mkdir_p} %{buildroot}%{gem_dir}

%{__cp} -a .%{gem_dir}/* %{buildroot}%{gem_dir}/
find %{buildroot}%{gem_dir} -name \*.rb.patch\* -delete

# Create symlinks
##
## Note that before switching to gem %%{ruby_sitelib}/%%{gem_name}
## already existed as a directory, so this cannot be replaced
## by symlink (cpio fails)
## Similarly, all directories under %%{ruby_sitelib} cannot be
## replaced by symlink
#

create_symlink_rec(){

ORIGBASEDIR=$1
TARGETBASEDIR=$2

## First calculate relative path of ORIGBASEDIR 
## from TARGETBASEDIR
TMPDIR=$TARGETBASEDIR
BACKDIR=
DOWNDIR=
num=0
nnum=0
while true
do
	num=$((num+1))
	TMPDIR=$(echo $TMPDIR | %{__sed} -e 's|/[^/][^/]*$||')
	DOWNDIR=$(echo $ORIGBASEDIR | %{__sed} -e "s|^$TMPDIR||")
	if [ x$DOWNDIR != x$ORIGBASEDIR ]
	then
		nnum=0
		while [ $nnum -lt $num ]
		do
			BACKDIR="../$BACKDIR"
			nnum=$((nnum+1))
		done
		break
	fi
done

RELBASEDIR=$( echo $BACKDIR/$DOWNDIR | %{__sed} -e 's|//*|/|g' )

## Next actually create symlink
pushd %{buildroot}/$ORIGBASEDIR
find . -type f | while read f
do
	DIRNAME=$(dirname $f)
	BACK2DIR=$(echo $DIRNAME | %{__sed} -e 's|/[^/][^/]*|/..|g')
	%{__mkdir_p} %{buildroot}${TARGETBASEDIR}/$DIRNAME
	LNNAME=$(echo $BACK2DIR/$RELBASEDIR/$f | \
		%{__sed} -e 's|^\./||' | %{__sed} -e 's|//|/|g' | \
		%{__sed} -e 's|/\./|/|' )
	%{__ln_s} -f $LNNAME %{buildroot}${TARGETBASEDIR}/$f
done
popd

}

create_symlink_rec %{gem_instdir}/bin %{_bindir}

#%if 0%{?ruby19} < 1
#create_symlink_rec %{gem_instdir}/data/locale %{_datadir}/locale
#%endif

# For --short-circult
%{__rm} -f *.lang

# modify find-lang.sh to deal with gettext .mo files under
# %%{gem_instdir}/locale (required on EL6)
sed -e 's|/share/locale/|/locale/|' \
	/usr/lib/rpm/find-lang.sh \
	> find-lang-modified.sh

sh find-lang-modified.sh %{buildroot} gettext gettext-gem.lang
#%find_lang gettext
#mv gettext.lang gettext-gem.lang

%{__cat} *-gem.lang >> %{pkg_name}-gem.lang

# list directories under %%{gem_instdir}/locale/
find %{buildroot}%{gem_instdir}/locale -type d | while read dir
do
	echo "%%dir ${dir#%{buildroot}}" >> %{pkg_name}-gem.lang
done

# clean up
rm -f %{buildroot}%{gem_instdir}/.yardopts

# Disable tests as it adds test-unit requirement into builds, and currently
# this isn't actively used.
#%check
#pushd .%{gem_instdir}
#export LANG=ja_JP.UTF-8
#%{?scl:scl enable %{scl} "}
#ruby -Ilib:test test/run-test.rb
#%{?scl:"}
#popd


%files	-f %{pkg_name}-gem.lang
%defattr(-,root,root,-)
%{_bindir}/rxgettext
%{_bindir}/rmsginit
%{_bindir}/rmsgfmt
%{_bindir}/rmsgmerge

%dir %{gem_instdir}/
%doc %{gem_instdir}/[A-Z]*
%doc %{gem_instdir}/doc/
%exclude %{gem_instdir}/Rakefile
%{gem_instdir}/bin/
%{gem_instdir}/lib/

%exclude	%{gem_cache}
%{gem_spec}

%files		doc
%defattr(-,root,root,-)
%{gem_docdir}/
%{gem_instdir}/samples/
%exclude	%{gem_instdir}/test/
%exclude	%{gem_instdir}/src/

%changelog
* Sun May 19 2013 Dominic Cleal <dcleal@redhat.com> 2.3.7-4
- Disable tests, fix find-lang.sh and _bindir on EL6, fix SCL redirection
  (dcleal@redhat.com)

* Tue Mar 12 2013 Lukas Zapletal <lzap+git@redhat.com> 2.3.7-3
- new package built with tito

* Sun Feb 10 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2/3/7-2
- Require levenshtein for fuzzy merging

* Thu Jan 24 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2.3.7-1
- 2.3.7

* Wed Jan  2 2013 Mamoru TASAKA <mtasaka@fedoraproject.org>  - 2.3.6-1
- 2.3.6

* Wed Jan  2 2013 Mamoru TASAKA <mtasaka@fedoraproject.org>  - 2.2.1-3
- Clean up old stuff

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed May 30 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 2.2.1-1
- 2.2.1

* Mon Apr  7 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 2.2.0-2
- Fix test case

* Mon Apr  7 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 2.2.0-1
- 2.2.0

* Tue Apr 03 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 2.1.0-7
- Fix conditionals for F17 to work for RHEL 7 as well.

* Sun Jan 29 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 2.1.0-6
- F-17: rebuild against ruby 1.9

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sat Jun 25 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 2.1.0-4
- Rescue Gem.all_load_paths when it is removed from rubygems

* Mon Feb 14 2011 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 2.1.0-3
- F-15 mass rebuild

* Tue Jan 12 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp>
- gems.rubyforge.org gem file seems old, changing Source0 URL for now

* Wed Nov 18 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 2.1.0-1
- 2.1.0

* Sat Jul 25 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 2.0.4-2
- F-12: Mass rebuild

* Wed May 28 2009 Mamoru Tasaka <mtasaka@ios.s.u-tokyo.ac.jp> - 2.0.4-1
- 2.0.4

* Mon May 11 2009 Mamoru Tasaka <mtasaka@ios.s.u-tokyo.ac.jp> - 2.0.3-2
- 2.0.3
- Add "BR: gettext" (not to Requires) for rake test

* Fri May  1 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 2.0.1-3
- Mark LICENSE etc as %%doc

* Wed Apr 22 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 2.0.1-2
- Bump ruby-locale Requires version

* Tue Apr 21 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 2.0.1-1
- 2.0.1, drop patches already in upstream (all)

* Sat Mar 29 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 2.0.0-1
- Update to 2.0.0
- Now require rubygem(locale)
- Rescue NoMethodError on gem call on gettext.rb
- Reintroduce 4 args bindtextdomain() compatibility

* Tue Feb 24 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.93.0-8
- %%global-ize "nested" macro 

* Thu Oct 23 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.93.0-7
- Handle gettext .mo files under %%{gem_instdir}/data/locale by
  modifying find-lang.sh

* Tue Oct  7 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.93.0-6
- Move sed edit section for lib/ files from %%install to %%build
  stage for cached gem file

* Tue Oct  7 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.93.0-5
- Recreate gettext .mo files (by using this itself)

* Mon Oct  6 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.93.0-3
- Some modification for spec file by Scott

* Tue Sep 23 2008 Scott Seago <sseago@redhat.com> - 1.93.0-2
- Initial package (of rubygem-gettext)
  Set at release 2 to supercede ruby-gettext-package-1.93.0-1

* Thu Sep 18 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.93.0-1
- 1.93.0

* Sat Aug  9 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.92.0-1
- 1.92.0

* Thu May 22 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.91.0-1
- 1.91.0

* Sun Feb  3 2008 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.90.0-1
- 1.90.0
- Arch changed to noarch

* Wed Aug 29 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.10.0-1
- 1.10.0

* Wed Aug 22 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.9.0-2.dist.2
- Mass rebuild (buildID or binutils issue)

* Fri Aug  3 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.9.0-2.dist.1
- License update

* Mon May  7 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.9.0-2
- Create -doc subpackage

* Sat Apr 21 2007 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.9.0-1
- Initial packaging
