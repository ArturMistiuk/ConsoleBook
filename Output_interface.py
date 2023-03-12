from main import get_contacts
from abc import ABC, abstractmethod


class OutputInterface(ABC):

    @abstractmethod
    def show_contacts(self, *args, **kwargs):
        pass


class ConsoleInterface(OutputInterface):

    def show_contacts(self, *args, **kwargs):
        return get_contacts()


output = ConsoleInterface()
print(output.show_contacts())
