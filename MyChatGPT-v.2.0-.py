"""
This is a console helper bot that recognizes commands entered
from the keyboard and responds to this command.
"""


import re
import itertools


from collections import UserDict
from datetime import datetime, date


class AddressBook(UserDict):

    address_book = {}

    def add_record(self, record):
        self.data[record.name] = record.phones

    def iterator(self, n):
        return chunks(self.data.items(), n)


class Record:

    def __init__(self, name, phones=None, birthday=None):
        self.name = name
        self.phones = phones
        self.birthday = birthday

    def add_number(self, number):
        self.phones.append(number)
        return f'Contact {self.name} has been changed. Phone numbers: {self.phones}'

    def change_number(self):
        print(get_phone(self.name))
        i = int(input('Which number you want to change?(Write sequence number)\n')) - 1
        new_num = input('Write new number:\n')
        self.phones[i] = new_num
        return f'Number has been changed. Numbers: {self.phones}'

    def del_number(self):
        print(get_phone(self.name))
        i = int(input('Which number you want to delete?(Write sequence number)\n')) - 1
        self.phones.remove(self.phones[i])
        return f'Number has been deleted. Numbers : {self.phones}'

    def days_to_birthday(self):
        this_birthday = date(self.birthday._current_date.year, self.birthday.value.month, self.birthday.value.day)
        next_birthday = date(self.birthday._current_date.year + 1, this_birthday.month, this_birthday.day)
        if this_birthday > self.birthday._current_date:
            return (this_birthday - self.birthday._current_date).days
        else:
            return (next_birthday - self.birthday._current_date).days


class Field:
    def __init__(self):
        self._value = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, data):
        self._value = data


class Birthday(Field):

    def __init__(self):
        super().__init__()
        self._current_date = datetime.today().date()

    @property
    def value(self):
        return super().value

    @value.setter
    def value(self, birthday):
        datetime.strptime(birthday, '%d-%m-%Y')
        self._value = datetime.strptime(birthday, '%d-%m-%Y').date()


class Name(Field):

    def __init__(self):
        super().__init__()

    @property
    def value(self):
        return super().value

    @value.setter
    def value(self, name):
        if name in contact_book.data.keys():  # Checking for an already existing name in memory
            raise ValueError(f'Contact with {name} already created. Try to change it.')
        else:
            self._value = name       # super(Name, Name)


class NumberException(Exception):
    pass


class InvalidBirthday(Exception):
    pass


class Phone(Field):

    def __init__(self):
        super().__init__()
        self._phones = []

    @property
    def value(self):
        return super().value

    @value.setter
    def value(self, phone):
        match = re.match(r'\+\d{12}', phone)  # Pattern for phone number
        if match:
            self._value = phone
        else:
            raise NumberException

    def append(self, phone):
        self._phones.append(phone)


# A decorator block to handle user input errors.
def input_error(func):
    def inner(arguments):
        try:
            result = func(arguments)
            return result
        except KeyError or IndexError:
            return 'Wrong arguments!'
        except TypeError:
            return 'Wrong command!'
        except NumberException:
            return 'Incorrect number! Write in the format: +380123456789. Numbers were not accepted!'
        except InvalidBirthday:
            return 'Invalid birthdate! Write in the format: yyyy-mm-dd'
    return inner


# In this block, the bot saves a new contact in memory.
def add_contact(*args):
    contact_name = Name()
    contact_phone = Phone()
    contact_birthday = Birthday()
    contact_name.value = args[0]
    try:
        contact_birthday.value = args[-1]
        args = args[1:-1]
    except ValueError:
        args = args[1:]
    for arg in args:
        contact_phone.value = arg
        contact_phone._phones.append(contact_phone.value)
    contact_record = Record(contact_name.value, contact_phone._phones, contact_birthday)
    contact_book.add_record(contact_record)    # Add new contact with name and phone number
    return f'New contact {contact_name.value} with numbers {contact_phone._phones} have been added'


def advice():
    instruction = "How can I help you?"
    return instruction


# +380934763845
# This function changes phone number in a existing contact
@input_error
def change_number(name):
    record_name = Name()
    record_name.value = name
    if record_name.value in contact_book:    # Checks that contact with given name is exist
        record = Record(record_name.value, contact_book[record_name.value])
        return record.change_number()
    else:    # If contact with name doesn't exist
        return f'{name} does not exist in contacts. Try to create new contact.'


def chunks(seq, n):
    it = iter(seq)
    while True:
        t = tuple(itertools.islice(it, int(n)))
        if len(t) == 0:
            break
        yield t


def close_bot():
    instruction = 'Good bye!'
    return instruction


@input_error
def del_number(name):
    record_name = Name()
    record_name.value = name
    if record_name.value in contact_book:    # Checks that contact with given name is exist
        record = Record(record_name.value, contact_book[record_name.value])
        return record.del_number()
    else:    # If contact with name doesn't exist
        return f'{name} does not exist in contacts. Try to create new contact.'


# Currying
@input_error
def handler(command):
    if command in COMMANDS:
        return COMMANDS[command]
    else:
        return COMMANDS_WITHOUT_ARGS[command]


# Shows all contacts
def get_contacts():
    return contact_book


# Shows all phone numbers
def get_phone(name):
    return f"{name}'s phone numbers are: {contact_book[name]}"


def iterating(n):
    for record in contact_book.iterator(n):
        print(record)


@input_error
def new_number(name):
    record_name = Name()
    record_name.value = name
    if record_name.value in contact_book:
        new_phone_number = input('Write a number: ')
        record = Record(record_name.value, contact_book[record_name.value])
        return record.add_number(new_phone_number)


# Handling user commands
@input_error
def reply(user_command):
    if user_command.lower() not in COMMANDS_WITHOUT_ARGS:    # Checking if given command has arguments
        command, args = user_command.split(' ')[0].lower(), user_command.split(' ')[1:]    # Separate command, arguments
        instruction = handler(command)    # Instruction is a signature of given function by user
        return instruction(*args)    # Execute command with arguments given by user
    else:
        return handler(user_command.lower())()    # Execute command without any arguments


# List of commands that don't take arguments and their command-words
COMMANDS_WITHOUT_ARGS = {
    'close': close_bot,
    'exit': close_bot,
    'good bye': close_bot,
    'hello': advice,
    'show all': get_contacts,
}
# # List of commands that take arguments and their command-words
COMMANDS = {
    'iter': iterating,
    'new_number': new_number,
    'add': add_contact,
    'change_number': change_number,
    'del_number': del_number,
    'phone': get_phone,
}
# Book of contacts
contact_book = AddressBook()


def main():
    bot_loop = True
    while bot_loop:
        user_input = input('>> ')
        if handler(user_input.lower()) == close_bot:    # If the command entered is to exit the program
            bot_loop = False    # Stop loop
        print('<<', reply(user_input))


if __name__ == '__main__':
    main()
