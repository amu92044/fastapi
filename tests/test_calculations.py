
def test_add():
    from app.calculations import add, subtract, multiply, divide, bank_account
    sum=add(2, 3) 
    assert sum == 5

def test_subtract():
    from app.calculations import add, subtract, multiply, divide
    difference=subtract(5, 3) 
    assert difference == 2

def test_multiply():
    from app.calculations import add, subtract, multiply, divide
    product=multiply(2, 3) 
    assert product == 6
    
def test_divide():  
    from app.calculations import add, subtract, multiply, divide
    quotient=divide(6, 3) 
    assert quotient == 2.0  
    
def test_bank_account():
    from app.calculations import bank_account
    account = bank_account("John Doe", 100.0)
    assert account.get_balance() == 100.0

    account.deposit(50.0)
    assert account.get_balance() == 150.0

    account.withdraw(30.0)
    assert account.get_balance() == 120.0

    try:
        account.withdraw(200.0)
    except ValueError as e:
        assert str(e) == "Insufficient funds"