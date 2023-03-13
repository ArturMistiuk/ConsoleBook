"""
This is a console helper bot that recognizes commands entered
from the keyboard and responds to this command.
"""


import io
import itertools
import pickle
import re


from abc import ABC, abstractmethod
from collections import UserDict
from datetime import date, datetime


class AddressBook(UserDict):

    def __init__(self, filename):

        super().__init__()

        self.filename = filename
        try:
            with open(self.filename, 'rb') as file:
                self.data = pickle.load(file)
        except (FileNotFoundError, EOFError):   # File is empty or not founded
            self.data = {}

    def __del__(self):
        with io.open(self.filename, 'wb') as f:
            pickle.dump(self.data, f)

    def add_record(self, record):
        self.data[record.name] = record.phones, record.birthday.value

    def find_contact(self, request):
        for name, phones in self.data.items():
            if request.lower() in name.lower() or any(request in phone for phone in phones):
                return f'Contact was found: {name} {self.data[name]}'
        return f'Your request was not found!'

    def iterator(self, chunk_len):
        return chunks(self.data.items(), chunk_len)


class Record:

    def __init__(self, name, phones=None, birthday=None):
        self.name = name
        self.phones = phones
        self.birthday = birthday

    def add_number(self, number):
        self.phones.append(number)
        return f'Contact {self.name} has been changed. Phone numbers: {self.phones}'

    def _get_index(self):
        print(get_phone(self.name))
        index = int(input('Which number you want to change?(Write sequence number)\n')) - 1
        return index

    def change_number(self):
        index = self._get_index()
        new_num = input('Write new number:\n')
        try:
            self.phones[index] = new_num
        except IndexError:
            self.add_number(new_num)
        return f'Number has been changed. Numbers: {self.phones}'

    def del_number(self):
        index = self._get_index()
        self.phones.remove(self.phones[index])
        return f'Number has been deleted. Numbers : {self.phones}'

    def days_to_birthday(self):
        current_date = datetime.today().date()
        self.birthday._value = datetime.strptime(self.birthday.value, '%d-%m-%Y').date()
        this_birthday = date(current_date.year, self.birthday.value.month, self.birthday.value.day)
        next_birthday = date(current_date.year + 1, this_birthday.month, this_birthday.day)

        if this_birthday > current_date:
            days_left = (this_birthday - current_date).days
        else:
            days_left = (next_birthday - current_date).days

        return f'Until birthday {days_left} day(s) left'


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

    @property
    def value(self):
        return super().value

    @value.setter
    def value(self, birthday):
        self._value = birthday


class Name(Field):

    def __init__(self):
        super().__init__()

    @property
    def value(self):
        return super().value

    @value.setter
    def value(self, name):
        self._value = name


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

    @property
    def phones(self):
        return self._phones

    @phones.setter
    def phones(self, value):
        self._phones = value

    def append(self, phone):
        self.phones.append(phone)


# Block with output interface
# Abstract class for output
class OutputInterface(ABC):

    @abstractmethod
    def show_contacts(self, *args, **kwargs):
        pass


# output contacts
class ConsoleInterface(OutputInterface):

    def show_contacts(self, *args, **kwargs):
        return contact_book


# Block with custom Exceptions
class NumberException(Exception):
    pass


class InvalidBirthday(Exception):
    pass


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
            return 'Incorrect number or birthday! Write in the format: +380123456789 and dd-mm-yyyy. ' \
                   'Data was not accepted!'
        except InvalidBirthday:
            return 'Invalid birthdate! Write in the format: yyyy-mm-dd'
    return inner


# Currying
@input_error
def handler(command):
    if command in COMMANDS:
        return COMMANDS[command]
    else:
        return COMMANDS_WITHOUT_ARGS[command]


# Handling user commands
@input_error
def reply(user_command):
    if user_command.lower() not in COMMANDS_WITHOUT_ARGS:    # Checking if given command has arguments
        command, args = user_command.split(' ')[0].lower(), user_command.split(' ')[1:]    # Separate command, arguments
        instruction = handler(command)    # Instruction is a signature of given function by user
        return instruction(*args)    # Execute command with arguments given by user
    else:
        return handler(user_command.lower())()    # Execute command without any arguments


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
        contact_phone.phones.append(contact_phone.value)

    contact_record = Record(contact_name.value, contact_phone.phones, contact_birthday)
    contact_book.add_record(contact_record)    # Add new contact with name and phone number
    if contact_birthday.value:
        return f'New contact {contact_name.value} with numbers {contact_phone.phones} ' \
               f'and birthdate {contact_birthday.value} have been added.'
    else:
        return f'New contact {contact_name.value} with numbers {contact_phone.phones}'


def advice():
    instruction = "How can I help you?"
    return instruction


def calculate_days_to_birthday(name):
    record_name = Name()
    record_birthday = Birthday()
    record_name.value = name
    record_birthday.value = contact_book[record_name.value][-1]

    if record_name.value in contact_book:    # Checks that contact with given name is exist
        record = Record(record_name.value, contact_book[record_name.value], record_birthday)
        return record.days_to_birthday()


# +380934763834
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


def chunks(seq, chunk_len):

    iterable = iter(seq)

    while True:
        chunk = tuple(itertools.islice(iterable, int(chunk_len)))
        if len(chunk) == 0:
            break
        yield chunk


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


def search(request):
    return contact_book.find_contact(request)


# Shows all contacts
def get_contacts():
    output_book = ConsoleInterface()
    return output_book.show_contacts()


# Shows all phone numbers
@input_error
def get_phone(name):
    return f"{name}'s phone numbers are: {contact_book[name]}"


@input_error
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
    'add': add_contact,
    'calc_birthday': calculate_days_to_birthday,
    'change_number': change_number,
    'del_number': del_number,
    'find': search,
    'iter': iterating,
    'phone': get_phone,
    'new_number': new_number,
}
# Book of contacts
file_name = 'Contacts.txt'
contact_book = AddressBook(file_name)


def main():
    bot_loop = True
    while bot_loop:
        user_input = input('>> ')
        if handler(user_input.lower()) == close_bot:    # If the command entered is to exit the program
            bot_loop = False    # Stop loop
        print('<<', reply(user_input))


if __name__ == '__main__':
    main()
