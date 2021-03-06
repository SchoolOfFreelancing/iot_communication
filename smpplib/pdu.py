"""PDU module"""

import struct

from . import command_codes
from . import consts

SMPP_ESME_ROK = 0x00000000


def extract_command(pdu):
    """Extract command from a PDU"""

    code = struct.unpack('>L', pdu[4:8])[0]

    return command_codes.get_command_name(code)


class default_client(object):
    """Dummy client"""
    sequence = 0


class PDU(object):
    """PDU class"""

    length = 0
    command = None
    status = None
    _sequence = None

    def __init__(self, client=default_client(), **kwargs):
        """Singleton dummy client will be used if omitted"""
        if client is None:
            self._client = default_client()
        else:
            self._client = client

    def _get_sequence(self):
        """Return global sequence number"""
        return self._sequence if self._sequence is not None else \
            self._client.sequence

    def _set_sequence(self, sequence):
        """Setter for sequence"""
        self._sequence = sequence

    sequence = property(_get_sequence, _set_sequence)

    def _next_seq(self):
        """Return next sequence number"""
        return self._client.next_sequence()

    def is_vendor(self):
        """Return True if this is a vendor PDU, False otherwise"""
        return hasattr(self, 'vendor')

    def is_request(self):
        """Return True if this is a request PDU, False otherwise"""
        return not self.is_response()

    def is_response(self):
        """Return True if this is a response PDU, False otherwise"""
        if command_codes.get_command_code(self.command) & 0x80000000:
            return True
        return False

    def is_error(self):
        """Return True if this is an error response, False otherwise"""
        if self.status != SMPP_ESME_ROK:
            return True
        return False

    def get_status_desc(self, status=None):
        """Return status description"""

        if status is None:
            status = self.status

        try:
            desc = consts.DESCRIPTIONS[status]
        except KeyError:
            return "Description for status 0x%x not found!" % status

        return desc

    def parse(self, data):
        """Parse raw PDU"""

        #
        # PDU format:
        #
        # Header (16 bytes)
        #   command_length: 4 bytes
        #   command_id: 4 bytes
        #   command_status: 4 bytes
        #   sequence_number: 4 bytes
        # Body (variable length)
        #   parameter
        #   parameter
        #   ...

        header = data[0:16]
        chunks = struct.unpack('>LLLL', header)
        self.length = chunks[0]
        self.command = extract_command(data)
        self.status = chunks[2]
        self.sequence = chunks[3]

        if len(data) > 16:
            self.parse_params(data[16:])

    def generate(self):
        """Generate raw PDU"""

        body = self.generate_params()

        self._length = len(body) + 16

        command_code = command_codes.get_command_code(self.command)

        header = struct.pack(">LLLL", self._length, command_code,
                             self.status, self.sequence)

        return header + body
