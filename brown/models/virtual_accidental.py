from brown.utils.exceptions import InvalidAccidentalError


class VirtualAccidental:

    def __init__(self, value):
        """
        Args:
            value (str or int or None): A description of the accidental.
                'f' or -1: Flat
                'n' or  0: Natural (Explicit)
                's' or  1: Sharp
                None     : No accidental, value depends on context.
        """
        self.value = value

    ######## SPECIAL METHODS ########

    def __repr__(self):
        """Represent the accidental as the code needed to instantiate it"""
        return '{}("{}")'.format(type(self).__name__,
                                 self.value_as_str)

    def __eq__(self, other):
        """Two accidentals are equal if their values are equal"""
        return isinstance(other, type(self)) and self.value == other.value

    def __hash__(self):
        """Hash based on the __repr__() of the accidental.

        VirtualAccidentals with different values will have different hashes"""
        return hash(self.__repr__())

    def __lt__(self, other):
        """An accidental is less than another if its numeric value is"""
        return isinstance(other, type(self)) and self.value < other.value

    ######## PUBLIC PROPERTIES ########

    @property
    def value(self):
        """int or None: The value of the accidental.

        String values passed to this will be automatically converted
        to their integer representations. None values will remain None.

        'f' or -1: Flat
        'n' or  0: Natural (Explicit)
        's' or  1: Sharp
        None     : No accidental, value depends on context.
        """
        return self._value

    @value.setter
    def value(self, new_value):
        if isinstance(new_value, str):
            if new_value == 'f' or new_value == 'F':
                self._value = -1
            elif new_value == 'n' or new_value == 'N':
                self._value = 0
            elif new_value == 's' or new_value == 'S':
                self._value = 1
            else:
                raise InvalidAccidentalError
        elif isinstance(new_value, (int, float)):
            if -1 <= new_value <= 1:
                self._value = int(new_value)
            else:
                raise InvalidAccidentalError
        elif isinstance(new_value, type(self)):
            self._value = new_value.value
        elif new_value is None:
            self._value = None
        else:
            raise InvalidAccidentalError

    @property
    def value_as_str(self):
        """str or None: The str (or None) version of the accidental value.

        Read-only.
        """
        if self._value == -1:
            return 'f'
        elif self._value == 0:
            return 'n'
        elif self._value == 1:
            return 's'
        else:
            return None
