Title: RFS health in Debian
Date: 2014-09-18 10:50
Tags: debian, python
Category: Debian
Slug: rfs-health-in-debian

I am working on a small project to create WNPP like statistics for open RFS bugs. I think this could
improve a little bit effectiveness of sponsoring new packages by giving insight into bugs that are on
their way to being starved (i.e. not ever sponsored, or rotting in a queue). 

The script attached in this post is written in Python and uses [Debbugs SOAP
interface](https://wiki.debian.org/DebbugsSoapInterface) to get currently open RFS bugs and
calculates their dust and age. 

The dust factor is calculated as an absolute value of a difference between bugs's `age` and
`log_modified`. 

Later I would like to create fully blown stats for an RFS queue, taking into account 
the whole history (i.e. 2012-1-1 until now), and check its health, calculate `MTTGS` (mean time to get sponsored). 


The list looks more or less like this:

    Age  Dust Number  Title
    37   0    757966  RFS: lutris/0.3.5-1 [ITP]
    1    0    762015  RFS: s3fs-fuse/1.78-1 [ITP #601789] -- FUSE-based file system backed by Amazon S3
    81   0    753110  RFS: mrrescue/1.02c-1 [ITP]
    456  0    712787  RFS: distkeys/1.0-1 [ITP] -- distribute SSH keys
    120  1    748878  RFS: mwc/1.7.2-1 [ITP] -- Powerful website-tracking tool
    1    1    762012  RFS: fadecut/0.1.4-1
    3    1    761687  RFS: abraca/0.8.0+dfsg-1 -- Simple and powerful graphical client for XMMS2
    35   2    758163  RFS: kcm-ufw/0.4.3-1 ITP
    3    2    761636  RFS: raceintospace/1.1+dfsg1-1 [ITP]
    ....
    ....

The script `rfs_health.py` can be found below, it uses `SOAPpy` 
(only python <3 unfortunately).
 
    :::python
    #!/usr/bin/python

    import SOAPpy
    import time
    from datetime import date, timedelta, datetime

    url = 'http://bugs.debian.org/cgi-bin/soap.cgi'
    namespace = 'Debbugs/SOAP'
    server = SOAPpy.SOAPProxy(url, namespace)

    class RFS(object):

        def __init__(self, obj):
            self._obj = obj
            self._last_modified = date.fromtimestamp(obj.log_modified)
            self._date = date.fromtimestamp(obj.date)
            if self._obj.pending != 'done':
                self._pending = "pending"
                self._dust = abs(date.today() - self._last_modified).days
            else:
                self._pending = "done"
                self._dust = abs(self._date - self._last_modified).days
            today = date.today()
            self._age = abs(today - self._date).days

        @property
        def status(self):
            return self._pending

        @property
        def date(self):
            return self._date

        @property
        def last_modified(self):
            return self._last_modified

        @property
        def subject(self):
            return self._obj.subject

        @property
        def bug_number(self):
            return self._obj.bug_num
        @property
        def age(self):
            return self._age

        @property
        def dust(self):
            return self._dust

        def __str__(self):
            return "{} subject: {} age:{} dust:{}".format(self._obj.bug_num, self._obj.subject, self._age, self._dust)


    if __name__ == "__main__":

        bugi = server.get_bugs("package", "sponsorship-requests", "status", "open")
        buglist = [RFS(b.value) for b in server.get_status(bugi).item]
        buglist_sorted_by_dust = sorted(buglist, key=lambda x: x.dust, reverse=False)
        print("Age  Dust Number  Title")
        for i in buglist_sorted_by_dust:
            print("{:<4} {:<4} {:<7} {}".format(i.age, i.dust, i.bug_number, i.subject))

