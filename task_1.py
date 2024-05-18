import pickle
from datetime import datetime, timedelta
from collections import UserDict

class Field:
    def __init__(self, value) -> None:
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not isinstance(value, str) or not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be a string of 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.date_value = datetime.strptime(value, '%d.%m.%Y').date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

class Record:
    def __init__(self, name) -> None:
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_birthday(self, birthday):
        if not isinstance(birthday, Birthday):
            raise ValueError('Birthday must be an instance of Birthday class.')
        if self.birthday:
            raise ValueError('Only one birthday allowed per record.')
        self.birthday = birthday

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        print(f'Phone number {phone} not found')

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = Phone(new_phone).value
                break

    def find_phone(self, number):
        for p in self.phones:
            if p.value == number:
                return p
        return None

    def __str__(self):
        phones = "; ".join(str(p) for p in self.phones)
        birthday = str(self.birthday) if self.birthday else "Not set"
        return f'Contact name: {self.name}, phones: {phones}, birthday: {birthday}'

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday = record.birthday.date_value
                birthday_this_year = birthday.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                days_until_birthday = (birthday_this_year - today).days
                if 0 <= days_until_birthday <= 7:
                    if birthday_this_year.weekday() in (5, 6):
                        if birthday_this_year.weekday() == 5:
                            birthday_this_year += timedelta(days=2)
                        else:
                            birthday_this_year += timedelta(days=1)
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": birthday_this_year.strftime("%Y.%m.%d")
                    })
        return upcoming_birthdays

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, IndexError) as e:
            return str(e)
    return inner

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_phone(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found."
    record.edit_phone(old_phone, new_phone)
    return f"Phone number for {name} changed from {old_phone} to {new_phone}."

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found."
    phones = ", ".join(phone.value for phone in record.phones)
    return f"{name}'s phone numbers: {phones}"

@input_error
def show_all_contacts(args, book: AddressBook):
    if not book.data:
        return "No contacts found."
    result = "All contacts:\n"
    for record in book.data.values():
        result += str(record) + "\n"
    return result

@input_error
def add_birthday(args, book):
    name, birthday_str = args
    record = book.find(name)
    if not record:
        return f"Contact {name} not found."
    try:
        birthday = Birthday(birthday_str)
        record.add_birthday(birthday)
        return f"Birthday for {name} added as {birthday_str}."
    except ValueError as e:
        return str(e)

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        return f"Contact {name} not found."
    if record.birthday:
        return f"Birthday for {name} is {record.birthday.value}."
    else:
        return f"Birthday for {name} is not set."

@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No birthdays in the next week."
    result = "Upcoming birthdays:\n"
    for bd in upcoming_birthdays:
        result += f"{bd['name']}: {bd['congratulation_date']}\n"
    return result

def parse_input(user_input):
    parts = user_input.strip().split()
    command = parts[0]
    args = parts[1:]
    return command, args

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено


def main():
    book = load_data()

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all_contacts(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == '__main__':
    main()
