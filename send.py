import os
import json
import time
import requests
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Carica le variabili d'ambiente
load_dotenv()

# Configurazione
WEB3_PROVIDER_URL = os.getenv('WEB3_PROVIDER_URL')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
TOKEN_ADDRESS = os.getenv('TOKEN_ADDRESS')
POLYGONSCAN_API_KEY = os.getenv('POLYGONSCAN_API_KEY')
POLYGONSCAN_API_URL = 'https://api.polygonscan.com/api'

# Modalità di test
TEST_MODE = False  # Imposta su False per la modalità di produzione

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

def get_nonce():
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

def load_nft_data(filename='nft_transactions.json'):
    """Carica i dati NFT dal file JSON."""
    with open(filename, 'r') as f:
        return json.load(f)

def process_compound_transactions(nft_data):
    """Elabora le transazioni di compound."""
    today = datetime.now().date()
    
    for collection_address, nfts in nft_data.items():
        for nft in nfts:
            transaction_sent = False  # Flag per tracciare se una transazione è stata inviata per questo NFT

            for i in range(1, 13):  # Controlla tutte le 12 possibili date di compound
                compound_date_key = f'compound_date_{i}'
                is_sent_key = f'isSent_compound_{i}'
                
                if compound_date_key not in nft or nft[compound_date_key] == "N/A":
                    continue  # Salta se la data non esiste o è N/A
                
                compound_date = datetime.strptime(nft[compound_date_key], '%d/%m/%Y').date()
                
                # In modalità test, processa solo la prima data disponibile.
                # In modalità produzione, solo le date di oggi non ancora inviate.
                if (TEST_MODE and not transaction_sent and not nft[is_sent_key]) or \
                   (not TEST_MODE and today == compound_date and not nft[is_sent_key]):
                    
                    interest_earned = nft['interest_earned']
                    to_address = nft['from']  # Usa l'indirizzo 'from' come destinatario
                    
                    print(f"Elaborazione compound per NFT {nft['tokenId']} della collezione {nft['collection_name']}")
                    print(f"Interesse guadagnato: {interest_earned} MATIC")
                    print(f"Data di compound: {compound_date}, Data odierna: {today}")
                    print(f"Indirizzo destinatario (owner): {to_address}")
                    
                    try:
                        if TEST_MODE:
                            print(f"MODALITÀ TEST: Invio transazione per la data {compound_date_key}")
                        
                        receipt = send_token(to_address, interest_earned)
                        
                        if receipt['status'] == 1:
                            print(f"Transazione di compound confermata. Blocco numero: {receipt['blockNumber']}")
                            nft[is_sent_key] = True  # Aggiorna lo stato a inviato
                            print(f"Stato di invio aggiornato per {compound_date_key}")
                            transaction_sent = True  # Imposta il flag a True dopo l'invio
                        else:
                            print("La transazione di compound è fallita.")
                    except Exception as e:
                        print(f"Errore durante l'invio della transazione di compound: {str(e)}")
                    
                    if TEST_MODE:
                        break  # Esci dal ciclo dopo aver inviato una transazione in modalità test
                    
                    time.sleep(5)  # Ritardo tra le transazioni

    # Salva i dati aggiornati nel file JSON
    with open('nft_transactions.json', 'w') as f:
        json.dump(nft_data, f, indent=2)

    print("\nProcesso completato e dati salvati.")
    
    
def main():
    nft_data = load_nft_data('nft_transactions.json')  # Carica i dati dal file fornito
    
    if TEST_MODE:
        print("ATTENZIONE: Modalità di test attiva. Le transazioni verranno inviate per tutte le date di compound disponibili.")
    else:
        print("ATTENZIONE: Modalità di produzione attiva. Le transazioni verranno inviate solo per le date di compound di oggi.")
    
    confirm = input("Sei sicuro di voler procedere? (y/n): ")
    if confirm.lower() != 'y':
        print("Operazione annullata.")
        return
    
    process_compound_transactions(nft_data)
    print("\nProcesso completato.")

if __name__ == "__main__":
    main()