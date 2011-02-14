buildy - automatic nightly builder
==================================

Author: Evgeni Golov
License: BSD

0. About
--------
buildy is an automatic nightly builder. Given a VCS repository and a
packaging template it can create distribution packages of your software.

1. VCS
------
Currently buildy supports SVN and Git as VCS.

You just have to specify the repository and vcs-type in the config:

SVN:
    vcs = svn
    vcs-url = https://geany.svn.sourceforge.net/svnroot/geany/trunk

Git:
    vcs = git
    vcs-url = git://github.com/evgeni/bley.git

Git with a specified branch (not master):
    vcs = git
    vcs-url = git://hades.mount.at/siyb/tbar
    vcs-git-branch = 1.3

2. Distributions
----------------
Currently buildy supports only Debian (and Ubuntu and other dpkg/deb-using
ones) as target distribution. Support for other (RPM-based) distributions
will come later.

3. Usage
--------
Ask Zhenech in #geany on irc.freenode.net - too lazy now ;)
