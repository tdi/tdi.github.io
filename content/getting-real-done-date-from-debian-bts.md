Title: getting real "done date" of a bug from Debian BTS
Date: 2014-09-19 09:17
Tags: debian, python
Category: Debian
Slug: getting-real-done-date-from-debian-bts

As I wrote in my last [post](|filename|debian-debbugs-processing-for-statistics.md) currently, SOAP
interface, nor Ultimate Debian Database do not provide a date when a given bug was closed (done
date). It is quite hard to calculate statistics on a bug tracker when you do not know when a bug was
closed (!!). 

Done date of bug can be found in its log. The log itself can be downloaded by SOAP method
`get_bug_log` but the processing of it is quite complicated. The same comes to web scrapping of a
BTS's web interface. Fortunatelly the web interface gives a possibility to download a log in an mbox
format. 

Below is a script that extracts the done date of a bug from its log in mbox format. It uses requests
to download the mbox and caches the result in `~/.cache/rfs_bugs`, which you need to create. It performs
different checks:

1. Check existence of a header e.g. `Received: (at 657783-done) by bugs.debian.org; 29 Jan 2012
  13:27:42 +0000`
2. Check  for header `CC: NUMBER-close|done`
3. Check for header `TO: NUMBER-close|done`
4. Check for `Close: NUMBER` in body.

The code is below:

    :::python
    import requests
    from datetime import datetime
    import mailbox
    import re
    import os
    import tempfile

    def get_done_date(bug_num):
     
        CACHE_DIR = os.path.expanduser("~") + "/.cache/rfs_bugs/"

        def get_from_cache():
            if os.path.exists("{}{}".format(CACHE_DIR, bug_num)):
                with open("{}{}".format(CACHE_DIR, bug_num)) as f:
                    return datetime.strptime(f.readlines()[0].rstrip(), "%Y-%m-%d").date()
            else:
                return None

        done_date = get_from_cache()

        if done_date is not None:
            return done_date
        else:
            r = requests.get("https://bugs.debian.org/cgi-bin/bugreport.cgi?mbox=yes;bug={};mboxstatus=yes".format(self._num))
            d = try_header(r.text)
            if d is None:
                d = try_cc(r.text)
            if d is None:
                d = try_body(r.text)
            if d is not None:
                with open("{}{}".format(CACHE_DIR, bug_num), "w") as f:
                    f.write("{}".format(d.date()))
            else:
                return None
            return d.date()

        def try_body(text):
            reg = "\(at\s.+\)\s+by\sbugs\.debian\.org;\s(\d{1,2}\s\w\w\w\s\d\d\d\d)"
            handle, name = tempfile.mkstemp()
            with open(name, "w") as f:
                f.write(text.encode('latin-1'))
            mbox = mailbox.mbox(name)
            for i in mbox.items():
                if i[1].is_multipart():
                    for m in i[1].get_payload():
                        if "close" in str(m) or "done" in str(m):
                            try:
                                result = re.search(reg, i[1]['Received'])
                                return datetime.strptime(result.group(1), "%d %b %Y")
                            except:
                                return None
                else:
                    if "close" in i[1].get_payload() or "done" in i[1].get_payload():
                        try:
                            result = re.search(reg, i[1]['Received'])
                            return datetime.strptime(result.group(1), "%d %b %Y")
                        except:
                            return None
            return None



        def try_header(text):
            reg = "Received:\s\(at\s\d\d\d\d\d\d-(close|done)\)\s+by.+"
            try:
                result = re.search(reg, r.text)
                line = result.group(0)
                reg2 = "\d{1,2}\s\w\w\w\s\d\d\d\d"
                result = re.search(reg2, line)
                d = datetime.strptime(result.group(0), "%d %b %Y")
                return d
            except:
                return None

        def try_cc(text):
            reg = "\(at\s.+\)\s+by\sbugs\.debian\.org;\s(\d{1,2}\s\w\w\w\s\d\d\d\d)"
            handle, name = tempfile.mkstemp()
            with open(name, "w") as f:
                f.write(text.encode('latin-1'))
            mbox = mailbox.mbox(name)
            for i in mbox.items():
                if ('CC' in i[1] and "done" in i[1]['CC']) or ('To' in i[1] and "done" in i[1]['To']):
                    try:
                        result = re.search(reg, i[1]['Received'])
                        return datetime.strptime(result.group(1), "%d %b %Y")
                    except:
                        return None

    if __name__ == "__main__":
        print get_done_date(752210)



PS: I hope that the script will be not needed in the near future, as Don Armstrong plans a new BTS
database, a [Debconf14 video is here](http://meetings-archive.debian.net/pub/debian-meetings/2014/debconf14/webm/bugsdebianorg_Database_Ho.webm).
