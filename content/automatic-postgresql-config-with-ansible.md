Title: Automatic PostgreSQL config with Ansible
Date: 2016-08-13 18:18
Tags: postgresql, linux, ansible
Category: devops
Slug: automatic-postgresql-config-with-ansible


If for some reasons you can’t use dedicated DBaaS for your PostgreSQL (like AWS RDS) then you need
to run your database server on a cloud instance. In these kind of setup, when you scale up or down
your instance size, you need to adjust PostgreSQL parameters according to the changing RAM size.
There are several parameters in PostgreSQL that highly depend on RAM size. An example is
`shared_buffers` for which a rule of thumb says that is should be set to 0.25*RAM.

In DBaaS, when you scale the DB instance up or down, parameters are adjusted for you by the cloud
provider, e.g. AWS RDS uses parameter groups for that reason, where particular parameters are
defined depending on the size of the RAM of the RDS instance.

So what can you when you do not have RDS or any other DBaaS? You can always keep several
configuration files on your instance, each for a different memory size, you can rewrite you config
every time you change the size of the instance… or you can use Ansible role for that.

Our Ansible role will be very simple, we will have two tasks. One will change the PostgreSQL config,
the second one will just restart the database server:

    :::yaml
    ---
    - name: Update PostgreSQL config
      template: src=postgresql.conf.j2 dest=/etc/postgresql/9.5/main/postgresql.conf
      register: pgconf
      
    - name: Restart postgresql
      service: name=postgresql state=restarted
      when: pgconf.changed


Now we need the template, where are the calculations take place. RAM size will be taken from the
Ansible’s fact called `ansible_memtotal_mb`. Since it returns RAM size in MBs, we will stick to MBs.
We will define the following parameters, you can adjust them to your needs:

- `shared_buffers`, as 0.25*RAM size,
- `work_mem`, as `shared_buffers/max_connections`,
- `maintenance_work_mem`, as RAM GBs times 64MB,
- `effective_cache_size`, as 0.75*RAM size.

For max_connections we will define a default role variable of 100 but we will allow to specify it at
a runtime. The relevant parts of the `postgresql.conf.j2` are below:

     max_connections = {{ max_connections }}      
     shared_buffers = {{ (((ansible_memtotal_mb/1024.0)|round|int)*0.25)|int*1024 }}MB
     work_mem = {{ ((((ansible_memtotal_mb/1024.0)|round|int)*0.25)/max_connections*1024)|round|int }}MB
     maintenance_work_mem = {{ ((ansible_memtotal_mb/1024.0)|round|int)*64 }}MB
     effective_cache_size = {{ (((ansible_memtotal_mb/1024.0)|round|int)*0.75)|int*1024 }}MB

You can now run the role every time you change the instance size, and the config will be changed
accordingly to the RAM size. You can extend the role and maybe add other constraints and change
`max_connections` to you specific needs. An example playbook could look like:

    :::ansible
    ---
    hosts: my_postgres
    roles:
      - postgres-config 
    vars:
      - max_connection: 300

And run it:

    :::bash
    $ ansible-playbook playbook.yml

The complete role can be found in my [github repo](https://github.com/tdi/postgres-config).

