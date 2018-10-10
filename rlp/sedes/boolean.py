from rlp.exceptions import (
    DeserializationError,
    SerializationError,
)


class Boolean:
    """A sedes for booleans
    """
    def serialize(self, obj):
        if not isinstance(obj, bool):
            raise SerializationError('Can only serialize integers', obj)

        if obj is False:
            return b''
        elif obj is True:
            return b'\x01'
        else:
            raise Exception("Invariant: no other options for boolean values")

    def deserialize(self, serial, to_list = False):
        if serial == b'':
            return False
        elif serial == b'\x01':
            return True
        else:
            raise DeserializationError(
                'Invalid serialized boolean.  Must be either 0x01 or 0x00',
                serial
            )

    def get_sede_identifier(self):
        return 0

boolean = Boolean()
