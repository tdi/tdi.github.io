Title: statistics of RFS bugs and sponsoring process
Date: 2014-09-21 16:21
Tags: debian, sponsoring
Category: Debian
Slug: statistics-of-rfs-bugs-and-sponsoring-process

For some days I have been working on statistics of the sponsoring process in Debian. I find
this to be one of the most important things that Debian has to attract and enable new contributions.
It is important to know how this process works, whether we need more sponsors, how effective is the
sponsoring and what are the timings connected to it. 

# How I did this ?

I have used Debbugs SOAP interface to get all bugs that are filed against `sponsorship-requests`
pseudo package. SOAP gives a little bit of overhead because it needs to download a complete list of
bugs for the `sponsorship-requests` package, and then process them according to given date ranges. 
The same information can be easily extracted from the UDD database in the future, it will be faster
because SQL is better when working with date ranges than python obviously. 

The most problematic part was getting the "real done date" of a particular bug, and frankly most of
my time I have spent on writing a rather dirty and complicated script. The script gets a log for a
particular bug number and returns a "real done date". I have published a proof of concept in a
[previous post.](|filename|getting-real-done-date-from-debian-bts.md).

# What I measured ?

RFSs is a queue, and in every queue one is interested in a mean time to get processed. In this case I
called the metric global MTTGS (mean time to get sponsored). This is a metric that gives the overall
performance insight in RFS queue. Time to get sponsored (TTGS) for a bug is a number of days that
passed between filing an RFS bug and closing it (bug was sponsored). Mean time to get sponsored is calculated as
a sum of TTGSs of all bugs divided by number of bugs (in a given period of time). Global MTTGS is
MTTGS calculated for a period of time 2012-1-1 until `today()`. 

Besides MTTGS I have also measured typical bug related metrics:

 - number of bugs closed in a given day,
 - number of bugs opened in a given day,
 - number of bugs with status open in a given day,
 - number of bugs with status closed in a given day.

# Plots and graphs

Below is a plot of global MTTGS vs. time (click for a larger image).

[![mttgs plot](|filename|/images/mttgs_small.png)](|filename|/images/mttgs.png)

As you can see, the trend is roughly exponential and MTTGS tends to settle around 60 days at the end of the
year 2013. This does not mean that your package will wait 60 days on average nowadays to get
sponsored. I remind that this is a global MTTGS, so even if the MTTGS of last month was very low, the global MTTGS would decrease
just slightly. It gives, however, a good glance in performance of the process. Even that more
packages are filed for sponsoring (see next graphs) now, than in the beginning of the epoch, the
sponsoring rate is high enough to flatten the global MTTGS, and with time maybe decrease it. 

The image below (click for a larger one) shows how many bugs reside in a queue with status open or
closed (calculated for each day). For closed we have an almost linear function, so each day more or less the same amount of
bugs are closed and they increase the pool of bugs with status closed. For bugs with status open the
interesting part begins around May 2012 after the system is saturated or gets popular. It can be interpreted
as a plot of how many bugs reside in the queue, the important part is that it is stable and does not
show clear increasing trend. 

[![open done plot](|filename|/images/open_done_small.png)](|filename|/images/open_done.png)

The last plot shows arrival and departure rate of bugs from RFS queue, i.e. how many bugs are opened
and closed each day. The interesting part here are the maxima. Let's look at them.

[![opened closed plot](|filename|/images/opened_closed_small.png)](|filename|/images/opened_closed.png)

Maximal number of opened bugs (21) was on 2012-05-06. As it appears it was a bunch upload of RFSs
for `tryton-modules-*.`.

      706953  RFS: tryton-modules-account-stock-anglo-saxon/2.8.0-1 
      706954  RFS: tryton-modules-purchase-shipment-cost/2.8.0-1 
      706948  RFS: tryton-modules-production/2.8.0-1 
      706969  RFS: tryton-modules-account-fr/2.8.0-1 
      706946  RFS: tryton-modules-project-invoice/2.8.0-1 
      706950  RFS: tryton-modules-stock-supply-production/2.8.0-1 
      706942  RFS: tryton-modules-product-attribute/2.8.0-1 
      706957  RFS: tryton-modules-stock-lot/2.8.0-1 
      706958  RFS: tryton-modules-carrier-weight/2.8.0-1 
      706941  RFS: tryton-modules-stock-supply-forecast/2.8.0-1 
      706955  RFS: tryton-modules-product-measurements/2.8.0-1 
      706952  RFS: tryton-modules-carrier-percentage/2.8.0-1 
      706949  RFS: tryton-modules-account-asset/2.8.0-1 
      706904  RFS: chinese-checkers/0.4-1 
      706944  RFS: tryton-modules-stock-split/2.8.0-1 
      706981  RFS: distcc/3.1-6 
      706945  RFS: tryton-modules-sale-supply/2.8.0-1 
      706959  RFS: tryton-modules-carrier/2.8.0-1 
      706951  RFS: tryton-modules-sale-shipment-cost/2.8.0-1 
      706943  RFS: tryton-modules-account-stock-continental/2.8.0-1 
      706956  RFS: tryton-modules-sale-supply-drop-shipment/2.8.0-1 

Maximum number of closed bugs (18) was on 2013-09-24, and as you probably guessed right also tryton modules had impact on that. 


      706953  RFS: tryton-modules-account-stock-anglo-saxon/2.8.0-1 
      706954  RFS: tryton-modules-purchase-shipment-cost/2.8.0-1 
      706948  RFS: tryton-modules-production/2.8.0-1 
      706969  RFS: tryton-modules-account-fr/2.8.0-1 
      706946  RFS: tryton-modules-project-invoice/2.8.0-1 
      706950  RFS: tryton-modules-stock-supply-production/2.8.0-1 
      706942  RFS: tryton-modules-product-attribute/2.8.0-1 
      706958  RFS: tryton-modules-carrier-weight/2.8.0-1 
      706941  RFS: tryton-modules-stock-supply-forecast/2.8.0-1 
      706955  RFS: tryton-modules-product-measurements/2.8.0-1 
      706952  RFS: tryton-modules-carrier-percentage/2.8.0-1 
      706949  RFS: tryton-modules-account-asset/2.8.0-1 
      706944  RFS: tryton-modules-stock-split/2.8.0-1 
      706959  RFS: tryton-modules-carrier/2.8.0-1 
      723991  RFS: mapserver/6.4.0-2 
      706951  RFS: tryton-modules-sale-shipment-cost/2.8.0-1 
      706943  RFS: tryton-modules-account-stock-continental/2.8.0-1 
      706956  RFS: tryton-modules-sale-supply-drop-shipment/2.8.0-1 

# The software 

Most of the software was written in Python. Graphs were generated in R. After a code cleanup I will
publish a complete solution on my github account, free to use by everybody. If you would like to see
another statistics, please let me know, I can create them if the data provides sufficient
information. 



