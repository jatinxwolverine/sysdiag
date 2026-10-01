import os
import pytest
from bank_account import (
    SavingsAccount,
    CheckingAccount,
    BankManager,
    InsufficientFundsError,
    InvalidTransactionError,
    AccountNotFoundError,
)


def test_savings_account_deposit_and_withdraw():
    acc = SavingsAccount("SA01", "Alice", balance=1000.0, minimum_balance=200.0)
    acc.deposit(500.0)
    assert acc.balance == 1500.0

    acc.withdraw(300.0)
    assert acc.balance == 1200.0

    with pytest.raises(InsufficientFundsError):
        acc.withdraw(1100.0)

    with pytest.raises(InvalidTransactionError):
        acc.deposit(-50)

    with pytest.raises(InvalidTransactionError):
        acc.withdraw(-50)


def test_checking_account_overdraft():
    acc = CheckingAccount("CA01", "Bob", balance=100.0, overdraft_limit=500.0)
    acc.withdraw(400.0)
    assert acc.balance == -300.0

    with pytest.raises(InsufficientFundsError):
        acc.withdraw(350.0)


def test_manager_json_persistence(tmp_path):
    manager = BankManager()
    sa = SavingsAccount("SA01", "Alice", 1000.0)
    ca = CheckingAccount("CA01", "Bob", 500.0)
    manager.add_account(sa)
    manager.add_account(ca)

    file_path = str(tmp_path / "accounts.json")
    manager.save_to_json(file_path)

    new_manager = BankManager()
    new_manager.load_from_json(file_path)

    assert len(new_manager.accounts) == 2
    assert new_manager.get_account("SA01").balance == 1000.0
    assert new_manager.get_account("CA01").balance == 500.0


def test_manager_csv_persistence(tmp_path):
    manager = BankManager()
    sa = SavingsAccount("SA01", "Alice", 1000.0)
    manager.add_account(sa)

    file_path = str(tmp_path / "accounts.csv")
    manager.save_to_csv(file_path)

    new_manager = BankManager()
    new_manager.load_from_csv(file_path)

    assert new_manager.get_account("SA01").balance == 1000.0


def test_account_not_found():
    manager = BankManager()
    with pytest.raises(AccountNotFoundError):
        manager.get_account("UNKNOWN")
        