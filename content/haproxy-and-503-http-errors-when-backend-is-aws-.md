Title: HAProxy and 503 HTTP errors with AWS ELB as a backend
Date: 2016-04-19 14:26
Tags: aws, linux, haproxy, http
Category: devops
Slug: haproxy-and-503-http-errors-with-aws-elb-as-a-backend


Although, AWS provides load balancer service in the form of Elastic Load Balancer (ELB), a common
trick is to use HAProxy in the middle to provide SSL offloading, complex routing and better logging.      
In this scenario, a public ELB is the frontier of all the traffic, HAProxy farm in the middle is
managed by an Auto Scaling Group, and one (or more) internal backend ELBs stay in front of Web farm. 

![haproxy](|filename|/images/haproxy.png)

I think that [HAProxy](http://www.haproxy.org/) does not need any introductions here. It is highly
scalable and reliable piece of software. There is however a small caveat when you use it with domain
names and not IP addresses. To speed up things, HAProxy resolves all the domain named during startup (during config file parsing in fact). Hence, when
the IP of a domain changes, you end up with a lot of 503s (Service Unavailable). 

Why is this important ? In AWS, ELB's IP can change over time, so it is recommended to use ELB's domain name.
Now, when you use this domain name in HAProxy's backend, you can end up with 503s. ELB IPs do not
change so often but still you would not want any downtimes. 

The solution is to configure runtime resolvers in HAProxy and use them in the backend
[(unforntunatelly this works only in HAProxy 1.6)](http://blog.haproxy.com/2015/10/14/whats-new-in-haproxy-1-6/):

     :::haproxy
     resolvers myresolver
          nameserver dns1 10.10.10.10:53
          resolve_retries       30
          timeout retry         1s
          hold valid           10s

      backend mybackend
          server myelb-internal.123456.eu-west-1.elb.amazonaws.com check resolvers myresolver

Now HAProxy will check the domain at runtime, no more 503s.
