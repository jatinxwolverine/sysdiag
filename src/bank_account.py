import csv
import json
from abc import ABC, abstractmethod


# 1. Custom Exceptions
class BankException(Exception):
    """Base exception for banking errors."""

    pass


class InsufficientFundsError(BankException):
    """Raised when an account does not have enough balance."""

    pass


class InvalidTransactionError(BankException):
    """Raised when an invalid amount or operation is attempted."""

    pass


class AccountNotFoundError(BankException):
    """Raised when an account is not found in the manager."""

    pass


# 2. Base Class & Subclasses
class Account(ABC):

    def __init__(self, account_number: str, account_holder: str, balance: float = 0.0):
        if balance < 0:
            raise InvalidTransactionError("Initial balance cannot be negative.")
        self.account_number = account_number
        self.account_holder = account_holder
        self._balance = float(balance)

    @property
    def balance(self) -> float:
        return self._balance

    def deposit(self, amount: float) -> float:
        if amount <= 0:
            raise InvalidTransactionError("Deposit amount must be greater than zero.")
        self._balance += amount
        return self._balance

    @abstractmethod
    def withdraw(self, amount: float) -> float:
        """Abstract method for withdrawal logic."""
        pass

    def to_dict(self) -> dict:
        return {
            "account_type": self.__class__.__name__,
            "account_number": self.account_number,
            "account_holder": self.account_holder,
            "balance": self._balance,
        }


class SavingsAccount(Account):

    def __init__(
        self,
        account_number: str,
        account_holder: str,
        balance: float = 0.0,
        minimum_balance: float = 500.0,
    ):
        super().__init__(account_number, account_holder, balance)
        self.minimum_balance = float(minimum_balance)

    def withdraw(self, amount: float) -> float:
        if amount <= 0:
            raise InvalidTransactionError(
                "Withdrawal amount must be greater than zero."
            )
        if self._balance - amount < self.minimum_balance:
            raise InsufficientFundsError(
                f"Cannot withdraw. Minimum balance of {self.minimum_balance} required."
            )
        self._balance -= amount
        return self._balance

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["minimum_balance"] = self.minimum_balance
        return data


class CheckingAccount(Account):

    def __init__(
        self,
        account_number: str,
        account_holder: str,
        balance: float = 0.0,
        overdraft_limit: float = 1000.0,
    ):
        super().__init__(account_number, account_holder, balance)
        self.overdraft_limit = float(overdraft_limit)

    def withdraw(self, amount: float) -> float:
        if amount <= 0:
            raise InvalidTransactionError(
                "Withdrawal amount must be greater than zero."
            )
        if self._balance + self.overdraft_limit < amount:
            raise InsufficientFundsError("Exceeded overdraft limit.")
        self._balance -= amount
        return self._balance

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["overdraft_limit"] = self.overdraft_limit
        return data


# 3. Manager with JSON/CSV Persistence
class BankManager:

    def __init__(self):
        self.accounts = {}

    def add_account(self, account: Account):
        self.accounts[account.account_number] = account

    def get_account(self, account_number: str) -> Account:
        if account_number not in self.accounts:
            raise AccountNotFoundError(f"Account {account_number} not found.")
        return self.accounts[account_number]

    def save_to_json(self, filepath: str):
        data = [acc.to_dict() for acc in self.accounts.values()]
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)

    def load_from_json(self, filepath: str):
        with open(filepath, "r") as f:
            data = json.load(f)
        self.accounts.clear()
        for item in data:
            acc_type = item.get("account_type")
            if acc_type == "SavingsAccount":
                acc = SavingsAccount(
                    item["account_number"],
                    item["account_holder"],
                    item["balance"],
                    item.get("minimum_balance", 500.0),
                )
            elif acc_type == "CheckingAccount":
                acc = CheckingAccount(
                    item["account_number"],
                    item["account_holder"],
                    item["balance"],
                    item.get("overdraft_limit", 1000.0),
                )
            else:
                continue
            self.add_account(acc)

    def save_to_csv(self, filepath: str):
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "account_type",
                    "account_number",
                    "account_holder",
                    "balance",
                    "extra_limit",
                ]
            )
            for acc in self.accounts.values():
                extra = getattr(
                    acc, "minimum_balance", getattr(acc, "overdraft_limit", 0.0)
                )
                writer.writerow(
                    [
                        acc.__class__.__name__,
                        acc.account_number,
                        acc.account_holder,
                        acc.balance,
                        extra,
                    ]
                )

    def load_from_csv(self, filepath: str):
        with open(filepath, "r") as f:
            reader = csv.DictReader(f)
            self.accounts.clear()
            for row in reader:
                acc_type = row["account_type"]
                balance = float(row["balance"])
                extra = float(row["extra_limit"])
                if acc_type == "SavingsAccount":
                    acc = SavingsAccount(
                        row["account_number"],
                        row["account_holder"],
                        balance,
                        minimum_balance=extra,
                    )
                elif acc_type == "CheckingAccount":
                    acc = CheckingAccount(
                        row["account_number"],
                        row["account_holder"],
                        balance,
                        overdraft_limit=extra,
                    )
                else:
                    continue
                self.add_account(acc)