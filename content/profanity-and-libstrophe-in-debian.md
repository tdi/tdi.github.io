Title: profanity and libstrophe status in Debian
Date: 2014-09-12 09:10
Tags: debian, packaging
Category: debian

[profanity](http://www.profanity.im) is a great console based XMPP client written in ncurses and C
by James Booth. The code has a great quality, upstream is super collaborative, and willing, so packaging should be pretty straightforward. This
post will show that this was not the case here. 

![profanity](http://www.profanity.im/images/prof-1.png)


First obstacle was that profanity depended on [libstrophe](http://strophe.im), an XMPP library, which
was not in Debian. As it occurred libstrophe's upstream was not responsive, so any changes that were
needed to prepare libstrophe for high quality packaging could not be met. 

1. First of all libstrophe's build system (automake and friends) built only a static library. 
2. The second problem was that libstrophe did not tag releases on github, this was needed to make Debian watch file work. 
3. A third, smaller problem was the presence of `debian/` directory in upstream's source. It can be neglected
most of the time, since you can tell `git-import-orig` to delete it. 

To solve those 3 problems I created a pull request fixing the
build system to build also a shared library, deleting `debian/` directory and politely asking for
tagging releases. You can see my pull request [here](https://github.com/strophe/libstrophe/pull/20) dated on April 26th. 
There was no answer for the libstrophe's upstream but I has some support from profanity's developers
and other users wanting to make those changes. Finally metajack (libstrophe upstream) gave us right
to the repo and we could merge the pull request on August 6th. The lesson learned - be patient and
know autotools (a great tutorial [is here](https://www.lrde.epita.fr/~adl/autotools.html)). 

With profanity there were less changes to do. The most important one was that it linked to OpenSSL
and due to the license incompatibility with GPL it could not go into Debian. Fortunately upstream
added the OpenSSL exception, and profanity could be finally packaged. 

Now both profanity and libstrophe are in [NEW queue](https://ftp-master.debian.org/new.html) and hopefully they will be accepted by ftp
masters. When they are, there is plenty to do with them in the future,  upstream closed some bugs,
new upstream versions are tagged. 
