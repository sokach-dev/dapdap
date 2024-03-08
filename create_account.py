from eth_account import Account
import sqlite3


def generate_eth_wallet(mnemonic):
    Account.enable_unaudited_hdwallet_features()
    if mnemonic:
        account = Account.from_mnemonic(mnemonic)
    else:
        account, mnemonic = Account.create_with_mnemonic()
    address = account.address
    private_key = account.key.hex()

    return mnemonic, private_key, address

if __name__ == "__main__":
    # mnemonic, private_key, address = generate_eth_wallet(None)
    # print(mnemonic)
    # print(private_key)
    # print(address)

    connection = sqlite3.connect('dapdap_1.db')
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wallet (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mnemonic TEXT,
        private_key TEXT,
        address TEXT,
        used INTEGER DEFAULT 0
    );
    ''')
    for i in range(20000):
        mnemonic, private_key, address = generate_eth_wallet(None)
        cursor.execute('''
        INSERT INTO wallet (mnemonic, private_key, address) VALUES (?, ?, ?)
        ''', (mnemonic, private_key, address))
        connection.commit()

    cursor.close()
    connection.close()

    connection = sqlite3.connect('dapdap_visit.db')
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS visit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        visit_code TEXT,
        used INTEGER DEFAULT 0
    );
    ''')
    connection.commit()
    cursor.close()
    connection.close()

