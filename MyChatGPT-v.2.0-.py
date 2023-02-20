"""
This is a console helper bot that recognizes commands entered
from the keyboard and responds to this command.
"""


import re


from collections import UserDict


class AddressBook(UserDict):

    address_book = {}

    def add_record(self, record):
        self.data[record.name.value] = record.phones


class Record:

    def __init__(self, name, phones=None):
        self.name = name
        self.phones = phones

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


class Field:
    pass


class Name:

    def __init__(self, name):
        self.value = name


class Phone:

    def __init__(self, phones):
        self.value = phones


# A decorator block to handle user input errors.
def input_error(func):
    def inner(arguments):
        try:
            result = func(arguments)
            return result
        except KeyError:
            return 'Wrong arguments!'
        except TypeError:
            return 'Wrong command!'
        except IndexError:
            return 'Wrong arguments'
    return inner


# In this block, the bot saves a new contact in memory.
def add_contact(*args):
    contact_name = Name(args[0])
    if contact_name.value in contact_book.data.keys():    # Checking for an already existing name in memory
        return f'Contact with {contact_name.value} already created. Try to change it.'
    contact_phones = []
    for phone_number in args[1:]:
        match = re.match(r'\+\d{12}', phone_number)    # Pattern for phone number
        if match:
            contact_phones.append(Phone(phone_number))
        else:
            print(f'Incorrect number! Write in the format: +380123456789. Number {phone_number} is not accepted!')
            break
    contact_record = Record(contact_name, [number.value for number in contact_phones])
    contact_book.add_record(contact_record)    # Add new contact with name and phone number
    return f'New contact {contact_name.value} with' \
           f' numbers {[phone_number.value for phone_number in contact_phones]} have been added'


def advice():
    instruction = "How can I help you?"
    return instruction


# +380934763845
# This function changes phone number in a existing contact
@input_error
def change_number(name):
    record_name = Name(name)
    if record_name.value in contact_book:    # Checks that contact with given name is exist
        record = Record(record_name.value, contact_book[record_name.value])
        return record.change_number()
    else:    # If contact with name doesn't exist
        return f'{name} does not exist in contacts. Try to create new contact.'


def close_bot():
    instruction = 'Good bye!'
    return instruction


@input_error
def del_number(name):
    record_name = Name(name)
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


@input_error
def new_number(record_name, new_number_for_contact):
    record_name = Name(record_name)
    if record_name.value in contact_book:
        record = Record(record_name.value, contact_book[record_name.value])
        return record.add_number(new_number_for_contact)


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
