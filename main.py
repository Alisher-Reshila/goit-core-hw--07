from datetime import datetime, timedelta
from collections import UserDict



class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Имя не может быть пустым.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError("Формат даты: DD.MM.YYYY")

class Phone(Field):
    def __init__(self, value):
        if len(value) == 10 and value.isdigit():
            super().__init__(value)
        else:
            raise ValueError("Номер должен содержать 10 цифр.")
        
class Record:
    def __init__(self, name_value):
        self.name = Name(name_value)      
        self.phones = []  
        self.birthday = None
    
    def add_phone(self, number):
        self.phones.append(Phone(number))

    def remove_phone(self, number):
        phone_obj = self.find_phone(number)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError(f"Номер {number} не найден.")

    def edit_phone(self, old_number, new_number):
        self.find_phone(old_number) 
        new_p = Phone(new_number)
        self.remove_phone(old_number)
        self.phones.append(new_p)

    def find_phone(self, number):
        for p in self.phones:
            if p.value == number:
                return p
        return None
    
    def add_birthday(self, b_day_str):
        self.birthday = Birthday(b_day_str)

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        bd_str = f", день рождения: {self.birthday}" if self.birthday else ""
        return f"Контакт: {self.name.value}, телефоны: {phones_str}{bd_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
    
    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError(f"Контакт {name} не найден.")

    def upcoming_birthdays(self):
        ubd = []
        today = datetime.today().date()

        for rec in self.data.values():
            if rec.birthday is None:
                continue 
            
            b_date = datetime.strptime(rec.birthday.value, "%d.%m.%Y").date()
            bd_this_year = b_date.replace(year=today.year)

            if bd_this_year < today:
                bd_this_year = bd_this_year.replace(year=today.year + 1)
            
            if 0 <= (bd_this_year - today).days <= 7:
                congrat_date = bd_this_year
                if congrat_date.weekday() == 5:
                    congrat_date += timedelta(days=2)
                elif congrat_date.weekday() == 6:
                    congrat_date += timedelta(days=1)
                
                ubd.append({
                    "name": rec.name.value,
                    "congratulation_date": congrat_date.strftime("%d.%m.%Y")
                })
        return ubd



def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, KeyError, IndexError) as e:
            return str(e) if str(e) else "Ошибка ввода данных."
    return inner

@input_error
def add_contact(args, book):
    name, phone = args
    record = book.find(name)
    if record is None:
        record = Record(name)
        book.add_record(record)
        res = "Контакт добавлен."
    else:
        res = "Контакт обновлен."
    record.add_phone(phone)
    return res

@input_error
def add_birthday(args, book):
    name, bday = args
    record = book.find(name)
    if record:
        record.add_birthday(bday)
        return "Дата рождения добавлена."
    raise KeyError("Контакт не найден.")

def parse_input(user_input):
    parts = user_input.split()
    if not parts:
        return "", []
    cmd = parts[0].strip().lower()
    args = parts[1:]
    return cmd, args

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ").strip()
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "all":
            for record in book.data.values():
                print(record)
        elif command == "birthdays":
            upcoming = book.upcoming_birthdays()
            if not upcoming:
                print("На этой неделе дней рождения нет.")
            for entry in upcoming:
                print(f"{entry['name']}: поздравляем {entry['congratulation_date']}")
        elif command:
            print("Неизвестная команда.")

if __name__ == "__main__":
    main()
