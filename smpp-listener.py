#!/usr/bin/python3.5

import logging
import sys

import smpplib.gsm
import smpplib.client
import smpplib.consts

'''
module haye log gereftan ezafe shode
module sys baraye dastrasi be driver haye sysmtem server ezafe shode
smpp library haye fork shode az google hastan
'''
#if you want to know what's happening
#logging.basicConfig(level='DEBUG')

# Two parts, UCS2, SMS with UDH
parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(u'Привет мир!\n'*10)

client = smpplib.client.Client('172.16.29.10', 2775)
'''
adress va porti ke mikhahim dar inja ezafe shod
'''

# Print when obtain message_id
client.set_message_sent_handler(
    lambda pdu: sys.stdout.write('sent {} {}\n'.format(pdu.sequence, pdu.message_id)))
client.set_message_received_handler(
    lambda pdu: sys.stdout.write('delivered {}\n'.format(pdu.receipted_message_id)))
client.connect()
client.bind_transceiver(system_id='asiatec', password='ea09217r')
'''
username va password SMPP thuraya inja ezafe shod
'''
client.listen()
