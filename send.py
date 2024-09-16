import os
import json
import time
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
from web3.datastructures import AttributeDict

# Carica le variabili d'ambiente
load_dotenv()

# Configurazione
WEB3_PROVIDER_URL = os.getenv('WEB3_PROVIDER_URL')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
TOKEN_ADDRESS = os.getenv('TOKEN_ADDRESS')

# Modalità di test
TEST_MODE = False

# Inizializza Firebase
cred = credentials.Certificate('/Users/davidezangrando/NFT/FIVERR/ordini/riccardo/FINANCE/sito-finale/prova-produzione/powerPlace-Finance/server-requests/powermining-retrieve-firebase-adminsdk-rt0x4-664e7464fc.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://powermining-retrieve-default-rtdb.firebaseio.com/'
})

# Inizializza Web3
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))

# Verifica la connessione
if not w3.is_connected():
    raise Exception("Impossibile connettersi alla rete. Verifica la tua connessione e l'URL del provider.")

# Crea l'account
account = Account.from_key(PRIVATE_KEY)

print(f"Indirizzo del mittente: {account.address}")

# ABI del contratto ERC20 (versione semplificata)
ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    }
]

# Inizializza il contratto
contract = w3.eth.contract(address=TOKEN_ADDRESS, abi=ERC20_ABI)

# Variabile globale per tenere traccia del nonce
current_nonce = None

def convert_to_serializable(obj):
    """Converte oggetti complessi in tipi serializzabili JSON."""
    if isinstance(obj, AttributeDict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (bytes, bytearray)):
        return obj.hex()
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        return {k: convert_to_serializable(v) for k, v in obj.__dict__.items()}
    else:
        return obj

def get_nonce():
    """Ottiene il nonce corrente per le transazioni."""
    global current_nonce
    if current_nonce is None:
        current_nonce = w3.eth.get_transaction_count(account.address, 'pending')
    else:
        current_nonce += 1
    return current_nonce

def send_token(to_address, amount):
    """Invia token ERC20 all'indirizzo specificato."""
    global current_nonce
    to_address = Web3.to_checksum_address(to_address)
    amount_wei = int(amount * 10**18)
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            nonce = get_nonce()
            tx = contract.functions.transfer(to_address, amount_wei).build_transaction({
                'chainId': w3.eth.chain_id,
                'gas': 200000,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce,
            })
            
            signed_tx = account.sign_transaction(tx)
            
            if hasattr(signed_tx, 'rawTransaction'):
                raw_tx = signed_tx.rawTransaction
            elif hasattr(signed_tx, 'raw_transaction'):
                raw_tx = signed_tx.raw_transaction
            else:
                raise AttributeError("Impossibile trovare 'rawTransaction' o 'raw_transaction' nell'oggetto SignedTransaction")
            
            tx_hash = w3.eth.send_raw_transaction(raw_tx)
            
            print(f"Transazione inviata. Hash: {tx_hash.hex()}")
            print(f"Puoi verificare la transazione su PolygonScan: https://polygonscan.com/tx/{tx_hash.hex()}")
            
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            return tx_receipt
        except Exception as e:
            if "nonce too low" in str(e):
                print(f"Errore nonce too low. Tentativo {attempt + 1} di {max_retries}.")
                current_nonce = None  # Resetta il nonce
                time.sleep(2)  # Attendi prima di riprovare
            else:
                raise e
    
    raise Exception(f"Impossibile inviare la transazione dopo {max_retries} tentativi.")


def save_nft_data(nft_data):
    """Salva i dati NFT su Firebase."""
    ref = db.reference('nft_transactions/data')
    
    # Converti i dati in un formato serializzabile
    serializable_data = convert_to_serializable(nft_data)
    
    # Salva i dati convertiti su Firebase
    ref.set(serializable_data)
    
    # Aggiorna il timestamp
    timestamp_ref = db.reference('nft_transactions/timestamp')
    timestamp_ref.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    print("Dati salvati su Firebase con successo.")

def process_compound_transactions(nft_data):
    """Elabora le transazioni di compound, invia i token e stampa un riepilogo."""
    today = datetime.now().date()
    all_transactions = []
    
    for collection_address, collection_nfts in nft_data.items():
        for nft in collection_nfts:
            transaction_sent = False

            for i in range(1, 13):
                compound_date_key = f'compound_date_{i}'
                is_sent_key = f'isSent_compound_{i}'
                
                if compound_date_key not in nft or nft[compound_date_key] == "N/A":
                    continue
                
                compound_date = datetime.strptime(nft[compound_date_key], '%d/%m/%Y').date()
                
                transaction_info = {
                    "collection_name": nft['collection_name'],
                    "tokenId": nft['tokenId'],
                    "compound_date": nft[compound_date_key],
                    "interest_earned": nft['interest_earned'],
                    "to_address": nft['from'],
                    "is_sent": nft.get(is_sent_key, False),
                    "processed_today": False,
                    "tx_hash": None
                }
                
                if (TEST_MODE and not nft.get(is_sent_key, False)) or \
                   (not TEST_MODE and today == compound_date and not nft.get(is_sent_key, False)):
                    
                    print(f"\nElaborazione compound per NFT {nft['tokenId']} della collezione {nft['collection_name']}")
                    print(f"Interesse guadagnato: {nft['interest_earned']} MATIC")
                    print(f"Data di compound: {compound_date}, Data odierna: {today}")
                    print(f"Indirizzo destinatario (owner): {nft['from']}")
                    
                    try:
                        # Invia effettivamente la transazione
                        tx_receipt = send_token(nft['from'], nft['interest_earned'])
                        
                        tx_hash = tx_receipt['transactionHash'].hex()
                        print(f"Transazione inviata. Hash: {tx_hash}")
                        
                        # Aggiorna lo stato nel database
                        nft[is_sent_key] = True
                        nft[f'tx_hash_{i}'] = tx_hash  # Salva l'hash della transazione nel database
                        
                        transaction_info["is_sent"] = True
                        transaction_info["processed_today"] = True
                        transaction_info["tx_hash"] = tx_hash
                        
                        print(f"Stato di invio aggiornato per {compound_date_key}")
                        transaction_sent = True
                        
                    except Exception as e:
                        print(f"Errore durante l'invio della transazione di compound: {str(e)}")
                    
                    if TEST_MODE:
                        break  # In modalità test, invia solo una transazione per NFT
                
                all_transactions.append(transaction_info)

    # Salva i dati aggiornati su Firebase
    save_nft_data(nft_data)

    print("\nRiepilogo delle transazioni:")
    print("-" * 50)
    for tx in all_transactions:
        status = "Inviata oggi" if tx["processed_today"] else ("Già inviata" if tx["is_sent"] else "Non inviata")
        print(f"Collezione: {tx['collection_name']}")
        print(f"Token ID: {tx['tokenId']}")
        print(f"Data compound: {tx['compound_date']}")
        print(f"Interesse: {tx['interest_earned']} MATIC")
        print(f"Destinatario: {tx['to_address']}")
        print(f"Stato: {status}")
        if tx["tx_hash"]:
            print(f"Hash transazione: {tx['tx_hash']}")
        print("-" * 50)

    print("\nProcesso completato e dati salvati su Firebase.")

def load_nft_data():
    """Carica i dati NFT da Firebase."""
    ref = db.reference('nft_transactions/data')
    return ref.get()

def main():
    nft_data = load_nft_data()  # Carica i dati da Firebase
    
    if TEST_MODE:
        print("ATTENZIONE: Modalità di test attiva. Le transazioni verranno inviate per tutte le date di compound disponibili.")
    else:
        print("ATTENZIONE: Modalità di produzione attiva. Le transazioni verranno inviate solo per le date di compound di oggi.")
    
    confirm = input("Sei sicuro di voler procedere? (y/n): ")
    if confirm.lower() != 'y':
        print("Operazione annullata.")
        return
    
    process_compound_transactions(nft_data)

if __name__ == "__main__":
    main()