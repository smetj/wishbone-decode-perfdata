#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_module_jq.py
#
#  Copyright 2016 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

from wishbone.event import Event, Metric
from wishbone_decode_perfdata import PerfData
from wishbone.actor import ActorConfig
from wishbone.utils.test import getter
import re
from gevent import sleep

host_perfdata = '''DATATYPE::HOSTPERFDATA   TIMET::1411637927   HOSTNAME::host1   HOSTPERFDATA::rta=0.751ms;3000.000;5000.000;0; pl=0%;80;100;;   HOSTCHECKCOMMAND::check_host!(null)   HOSTSTATE::0   HOSTSTATETYPE::1'''
serv_perfdata = '''DATATYPE::SERVICEPERFDATA   TIMET::1411637603   HOSTNAME::host2   SERVICEDESC::service1   SERVICEPERFDATA::time=0.02 'cat'=20;540;570;0;600 'armadillo'=0;540;570;0;600 'bear'=1;540;570;0;600 'dog'=128;540;570;0;600 'duck'=0;540;570;0;600 'monkey'=0;540;570;0;600 'lizard'=42;540;570;0;600    SERVICECHECKCOMMAND::check_animal SERVICESTATE::0 SERVICESTATETYPE'''


def test_module_decode_host_perfdata():

    data =  re.sub(' {2,4}', "\t", host_perfdata)
    actor_config = ActorConfig('pd', 100, 1, {}, "")
    pd = PerfData(actor_config)

    pd.pool.queue.inbox.disableFallThrough()
    pd.pool.queue.outbox.disableFallThrough()
    pd.start()

    e = Event(data)

    pd.pool.queue.inbox.put(e)
    sleep(1)
    assert pd.pool.queue.outbox.size() == 2

    one = getter(pd.pool.queue.outbox).get()
    assert isinstance(one, Metric)
    assert one.name == 'hostcheck.rta'
    assert one.value == '0.751'

    two = getter(pd.pool.queue.outbox).get()
    assert isinstance(two, Metric)
    assert two.name == 'hostcheck.pl'
    assert two.value == '0'


def test_module_decode_service_perfdata():

    data =  re.sub(' {2,4}', "\t", serv_perfdata)
    actor_config = ActorConfig('pd', 100, 1, {}, "")
    pd = PerfData(actor_config)

    pd.pool.queue.inbox.disableFallThrough()
    pd.pool.queue.outbox.disableFallThrough()
    pd.start()

    e = Event(data)

    pd.pool.queue.inbox.put(e)
    sleep(1)
    assert pd.pool.queue.outbox.size() == 8

    one = getter(pd.pool.queue.outbox).get()
    assert isinstance(one, Metric)
    assert one.name == 'service1.time'
    assert one.value == '0.02'

    two = getter(pd.pool.queue.outbox).get()
    assert isinstance(two, Metric)
    assert two.name == 'service1.cat'
    assert two.value == '20'
