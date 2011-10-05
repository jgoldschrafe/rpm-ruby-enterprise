%define __arch_install_post %{nil}
%define _prefix /opt/ruby-enterprise

# Package Maintainer: Increment phusion_release to match latest release available
%define phusion_release	2011.03

Summary: Ruby Enterprise Edition (Release %{phusion_release})
Name: ruby-enterprise
Vendor: Phusion.nl <info@phusion.nl>
Packager: Adam Vollrath <hosting@endpoint.com>
Version: 1.8.7
Release: 8%{dist}
License: Ruby or GPL v2
Group: Development/Languages 
URL: http://www.rubyenterpriseedition.com/
Source0: ruby-enterprise-%{version}-%{phusion_release}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{phusion_release}-root-%(%{__id_u} -n)
BuildRequires: chrpath
BuildRequires: make patch gcc-c++ glibc-devel
BuildRequires: openssl-devel readline-devel
BuildRequires: zlib-devel

%description 
Ruby Enterprise Edition is a server-oriented friendly branch of Ruby which includes various enhancements:
* A copy-on-write friendly garbage collector. Phusion Passenger uses this, in combination with a technique called preforking, to reduce Ruby on Rails applications' memory usage by 33% on average.
* An improved memory allocator called tcmalloc, which improves performance quite a bit.
* The ability to tweak garbage collector settings for maximum server performance, and the ability to inspect the garbage collector's state. (RailsBench GC patch)
* The ability to dump stack traces for all running threads (caller_for_all_threads), making it easier for one to debug multithreaded Ruby web applications.

%prep 
%setup -q -n %{name}-%{version}-%{phusion_release}

%package rubygems
Summary: The Ruby standard for packaging ruby libraries
Version: 1.5.2
License: Ruby or GPL v2
Vendor: Jim Weirich, Chad Fowler, and Eric Hodel <rubygems-developers@rubyforge.org>
Group: Development/Libraries
Requires: ruby-enterprise >= 1.8
Provides: ruby-enterprise(rubygems) = %{version}

%description rubygems
RubyGems is the Ruby standard for publishing and managing third party
libraries.  This rubygems package is for ruby-enterprise in /opt.

%build 
# Strip forced rpath from installer script
#patch --strip=1 << EOF
#--- trunk/installer.rb
#+++ trunk/installer.rb
#@@ -257,12 +257,7 @@
# 			end
# 			
# 			preincflags = "-I/opt/local/include"
#-			prelibs = "-L/opt/local/lib -Wl,"
#-			if PlatformInfo.solaris_ld?
#-				prelibs << "-R#{@prefix}/lib"
#-			else
#-				prelibs << "-rpath,#{@prefix}/lib"
#-			end
#+			prelibs = "-L/opt/local/lib"
# 			prelibs << " -L#{@destdir}#{@prefix}/lib"
# 			if tcmalloc_supported?
# 				prelibs << " -ltcmalloc_minimal "
#EOF

# Security patch for CVE-2011-0188
patch --strip=1 --directory=./source << EOF
--- trunk/ext/bigdecimal/bigdecimal.c
+++ trunk/ext/bigdecimal/bigdecimal.c
@@ -2032,11 +2032,11 @@
 VP_EXPORT void *
 VpMemAlloc(U_LONG mb)
 {
-    void *p = xmalloc((unsigned int)mb);
-    if(!p) {
-        VpException(VP_EXCEPTION_MEMORY,"failed to allocate memory",1);
+    void *p = xmalloc(mb);
+    if (!p) {
+        VpException(VP_EXCEPTION_MEMORY, "failed to allocate memory", 1);
     }
-    memset(p,0,mb);
+    memset(p, 0, mb);
 #ifdef _DEBUG
     gnAlloc++; /* Count allocation call */
 #endif /* _DEBUG */
EOF

%install
rm -rf $RPM_BUILD_ROOT

# work around bug in "installer"
mkdir -p $RPM_BUILD_ROOT%{_prefix}/lib/ruby/gems/1.8/gems

./installer --auto %{_prefix} \
  --configure-arg --disable-rpath \
  --dont-install-useful-gems \
  --no-dev-docs \
  --destdir $RPM_BUILD_ROOT

# Installer adds incorrect rpath for buildroot; delete it
#chrpath --delete $RPM_BUILD_ROOT%{_prefix}/lib/ruby/site_ruby/1.8/x86_64-linux/iconv.so

%check
# Help the dynamic linker find the libtcmalloc files:
export LD_LIBRARY_PATH="${RPM_BUILD_ROOT}%{_prefix}/lib/"
# and the Ruby library files:
export RUBYLIB="${RPM_BUILD_ROOT}%{_prefix}/lib/ruby/1.8"
export RUBYLIB="${RUBYLIB}:${RPM_BUILD_ROOT}%{_prefix}/lib/ruby/1.8/%{_arch}-linux"
# Run Ruby's unit tests:
#${RPM_BUILD_ROOT}%{_bindir}/ruby ./source/test/runner.rb | tee ./source/RPM_build_unit_tests || :

%clean
rm -rf $RPM_BUILD_ROOT

%files 
%defattr(-,root,root)
%{_bindir}/*
%{_prefix}/lib/*
%{_prefix}/share/man/man1/ruby.1
%doc source/ChangeLog
%doc source/COPYING
%doc source/LEGAL
%doc source/LGPL
%doc source/NEWS
%doc source/README
%doc source/README.EXT
%doc source/ToDo
#%doc source/RPM_build_unit_tests

# rubygems
%exclude %{_prefix}/bin/gem
%exclude %{_prefix}/lib/ruby/gems
%exclude %{_prefix}/lib/ruby/site_ruby/1.8/rubygems*
%exclude %{_prefix}/lib/ruby/site_ruby/1.8/ubygems.rb
%exclude %{_prefix}/lib/ruby/site_ruby/1.8/rbconfig

%files rubygems
%{_bindir}/gem
%{_prefix}/lib/ruby/gems
%{_prefix}/lib/ruby/site_ruby/1.8/rubygems*
%{_prefix}/lib/ruby/site_ruby/1.8/ubygems.rb
%{_prefix}/lib/ruby/site_ruby/1.8/rbconfig
%doc rubygems/LICENSE.txt
%doc rubygems/README.rdoc
%doc rubygems/UPGRADING.rdoc
%doc rubygems/GPL.txt
%doc rubygems/Manifest.txt
%doc rubygems/History.txt
%doc rubygems/ChangeLog

%pre
# Do not install if %{_prefix}/bin/ruby exists and is not provided by an RPM
if ([ -e %{_bindir}/ruby ] && !(rpm -q --whatprovides %{_bindir}/ruby >/dev/null)); then
    exit 1
else
    exit 0
fi

%pre rubygems
# Do not install if %{_prefix}/bin/gem exists and is not provided by an RPM
if ([ -e %{_bindir}/gem ] && !(rpm -q --whatprovides %{_bindir}/gem >/dev/null)); then
    exit 1
else
    exit 0
fi

%changelog 
* Mon Oct  3 2011 Jeff Goldschrafe <jeff@holyhandgrenade.org> - 1.8.7-8.hhg
- Bugfixes for CentOS 6

* Thu Aug 11 2011 Adam Vollrath <hosting@endpoint.com>
- Added upstream security patch for CVE-2011-0188

* Wed Apr 20 2011 Adam Vollrath <hosting@endpoint.com>
- Corrected Licenses

* Tue Apr 19 2011 Adam Vollrath <hosting@endpoint.com>
- Updated for 2011.03 and rubygems 1.5.2

* Tue Aug 24 2010 Adam Vollrath <hosting@endpoint.com>
- Updated package metadata
- Updated BuildRequires dependency lists after testing
- Run Ruby's unit tests during package building

* Wed Jun 30 2010 Adam Vollrath <hosting@endpoint.com>
- Updated for release 2010.02
- Updated rubygems version to 1.3.7
- Generalized all paths

* Mon Apr 19 2010 End Point Corporation <hosting@endpoint.com>
- Updated for release 2010.01
- Updated rubygems to 1.3.6

* Wed Dec 02 2009 Adam Vollrath <adam@endpoint.com>
- Updated for release 2009.10

* Wed Oct 07 2009 Adam Vollrath and Richard Templet <hosting@endpoint.com>
- Updated for release 20090928

* Wed Jun 10 2009 Adam Vollrath <adam@endpoint.com>
- Updated for release 20090610

* Tue Jun 02 2009 Adam Vollrath <adam@endpoint.com>
- Added check for existing /usr/local/bin/gem
- Added LICENSE and other important document files

* Mon Jun 01 2009 Adam Vollrath <adam@endpoint.com>
- Refactored to use Phusion's installer instead of building from source
- Changed prefix to just /usr/local
- Added check for existing /usr/local/bin/ruby
- Split rubygems into a subpackage

* Sat May 30 2009 Adam Vollrath <adam@endpoint.com>
- Changed Release number convention
- Added tcmalloc support and `make test`

* Tue May 26 2009 Adam Vollrath <adam@endpoint.com>
- Updated for 1.8.6-20090520
- Several small improvements to spec file

* Fri Dec 13 2008 Tim C. Harper <tim.harper@leadmediapartners.com>
- first build of REE package

--- installer.rb	2011-02-24 09:11:03.000000000 -0500
+++ /home/mockbuild/installer.rb	2011-10-02 22:17:41.840454206 -0400

