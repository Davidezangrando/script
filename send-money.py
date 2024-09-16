import calendar
import requests
from datetime import datetime, timedelta
import time
import json
import os
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
import random
# Carica le variabili d'ambiente
load_dotenv()

# Configurazione
API_KEY = os.getenv('POLYGONSCAN_API_KEY')
API_URL = 'https://api.polygonscan.com/api'
WEB3_PROVIDER_URL = os.getenv('WEB3_PROVIDER_URL')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
TOKEN_ADDRESS = os.getenv('TOKEN_ADDRESS')
TEST_MODE = os.getenv('TEST_MODE', 'False').lower() == 'true'

# Inizializza Web3
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))

# Aggiungi il middleware per la firma e l'invio di transazioni raw
account = Account.from_key(PRIVATE_KEY)
# Imposta l'account di default
w3.eth.default_account = account.address

ERC20_ABI = json.loads('''
[
  {
    "inputs": [],
    "stateMutability": "nonpayable",
    "type": "constructor"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "owner",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "spender",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "value",
        "type": "uint256"
      }
    ],
    "name": "Approval",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "delegator",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "fromDelegate",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "toDelegate",
        "type": "address"
      }
    ],
    "name": "DelegateChanged",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "delegate",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "previousBalance",
        "type": "uint256"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "newBalance",
        "type": "uint256"
      }
    ],
    "name": "DelegateVotesChanged",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [],
    "name": "EIP712DomainChanged",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "address",
        "name": "platformFeeRecipient",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "flatFee",
        "type": "uint256"
      }
    ],
    "name": "FlatPlatformFeeUpdated",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "uint8",
        "name": "version",
        "type": "uint8"
      }
    ],
    "name": "Initialized",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "platformFeeRecipient",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "platformFeeBps",
        "type": "uint256"
      }
    ],
    "name": "PlatformFeeInfoUpdated",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": false,
        "internalType": "enum IPlatformFee.PlatformFeeType",
        "name": "feeType",
        "type": "uint8"
      }
    ],
    "name": "PlatformFeeTypeUpdated",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "recipient",
        "type": "address"
      }
    ],
    "name": "PrimarySaleRecipientUpdated",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "bytes32",
        "name": "role",
        "type": "bytes32"
      },
      {
        "indexed": true,
        "internalType": "bytes32",
        "name": "previousAdminRole",
        "type": "bytes32"
      },
      {
        "indexed": true,
        "internalType": "bytes32",
        "name": "newAdminRole",
        "type": "bytes32"
      }
    ],
    "name": "RoleAdminChanged",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "bytes32",
        "name": "role",
        "type": "bytes32"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "account",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "sender",
        "type": "address"
      }
    ],
    "name": "RoleGranted",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "bytes32",
        "name": "role",
        "type": "bytes32"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "account",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "sender",
        "type": "address"
      }
    ],
    "name": "RoleRevoked",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "mintedTo",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "quantityMinted",
        "type": "uint256"
      }
    ],
    "name": "TokensMinted",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "signer",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "mintedTo",
        "type": "address"
      },
      {
        "components": [
          {
            "internalType": "address",
            "name": "to",
            "type": "address"
          },
          {
            "internalType": "address",
            "name": "primarySaleRecipient",
            "type": "address"
          },
          {
            "internalType": "uint256",
            "name": "quantity",
            "type": "uint256"
          },
          {
            "internalType": "uint256",
            "name": "price",
            "type": "uint256"
          },
          {
            "internalType": "address",
            "name": "currency",
            "type": "address"
          },
          {
            "internalType": "uint128",
            "name": "validityStartTimestamp",
            "type": "uint128"
          },
          {
            "internalType": "uint128",
            "name": "validityEndTimestamp",
            "type": "uint128"
          },
          {
            "internalType": "bytes32",
            "name": "uid",
            "type": "bytes32"
          }
        ],
        "indexed": false,
        "internalType": "struct ITokenERC20.MintRequest",
        "name": "mintRequest",
        "type": "tuple"
      }
    ],
    "name": "TokensMintedWithSignature",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "address",
        "name": "from",
        "type": "address"
      },
      {
        "indexed": true,
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "indexed": false,
        "internalType": "uint256",
        "name": "value",
        "type": "uint256"
      }
    ],
    "name": "Transfer",
    "type": "event"
  },
  {
    "inputs": [],
    "name": "CLOCK_MODE",
    "outputs": [
      {
        "internalType": "string",
        "name": "",
        "type": "string"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "DEFAULT_ADMIN_ROLE",
    "outputs": [
      {
        "internalType": "bytes32",
        "name": "",
        "type": "bytes32"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "DOMAIN_SEPARATOR",
    "outputs": [
      {
        "internalType": "bytes32",
        "name": "",
        "type": "bytes32"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "owner",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "spender",
        "type": "address"
      }
    ],
    "name": "allowance",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "spender",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "approve",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "balanceOf",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "burn",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "burnFrom",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      },
      {
        "internalType": "uint32",
        "name": "pos",
        "type": "uint32"
      }
    ],
    "name": "checkpoints",
    "outputs": [
      {
        "components": [
          {
            "internalType": "uint32",
            "name": "fromBlock",
            "type": "uint32"
          },
          {
            "internalType": "uint224",
            "name": "votes",
            "type": "uint224"
          }
        ],
        "internalType": "struct ERC20VotesUpgradeable.Checkpoint",
        "name": "",
        "type": "tuple"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "clock",
    "outputs": [
      {
        "internalType": "uint48",
        "name": "",
        "type": "uint48"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "contractType",
    "outputs": [
      {
        "internalType": "bytes32",
        "name": "",
        "type": "bytes32"
      }
    ],
    "stateMutability": "pure",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "contractURI",
    "outputs": [
      {
        "internalType": "string",
        "name": "",
        "type": "string"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "contractVersion",
    "outputs": [
      {
        "internalType": "uint8",
        "name": "",
        "type": "uint8"
      }
    ],
    "stateMutability": "pure",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "decimals",
    "outputs": [
      {
        "internalType": "uint8",
        "name": "",
        "type": "uint8"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "spender",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "subtractedValue",
        "type": "uint256"
      }
    ],
    "name": "decreaseAllowance",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "delegatee",
        "type": "address"
      }
    ],
    "name": "delegate",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "delegatee",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "nonce",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "expiry",
        "type": "uint256"
      },
      {
        "internalType": "uint8",
        "name": "v",
        "type": "uint8"
      },
      {
        "internalType": "bytes32",
        "name": "r",
        "type": "bytes32"
      },
      {
        "internalType": "bytes32",
        "name": "s",
        "type": "bytes32"
      }
    ],
    "name": "delegateBySig",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "delegates",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "eip712Domain",
    "outputs": [
      {
        "internalType": "bytes1",
        "name": "fields",
        "type": "bytes1"
      },
      {
        "internalType": "string",
        "name": "name",
        "type": "string"
      },
      {
        "internalType": "string",
        "name": "version",
        "type": "string"
      },
      {
        "internalType": "uint256",
        "name": "chainId",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "verifyingContract",
        "type": "address"
      },
      {
        "internalType": "bytes32",
        "name": "salt",
        "type": "bytes32"
      },
      {
        "internalType": "uint256[]",
        "name": "extensions",
        "type": "uint256[]"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "timepoint",
        "type": "uint256"
      }
    ],
    "name": "getPastTotalSupply",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "timepoint",
        "type": "uint256"
      }
    ],
    "name": "getPastVotes",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "getPlatformFeeInfo",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      },
      {
        "internalType": "uint16",
        "name": "",
        "type": "uint16"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bytes32",
        "name": "role",
        "type": "bytes32"
      }
    ],
    "name": "getRoleAdmin",
    "outputs": [
      {
        "internalType": "bytes32",
        "name": "",
        "type": "bytes32"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bytes32",
        "name": "role",
        "type": "bytes32"
      },
      {
        "internalType": "uint256",
        "name": "index",
        "type": "uint256"
      }
    ],
    "name": "getRoleMember",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bytes32",
        "name": "role",
        "type": "bytes32"
      }
    ],
    "name": "getRoleMemberCount",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "getVotes",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bytes32",
        "name": "role",
        "type": "bytes32"
      },
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "grantRole",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bytes32",
        "name": "role",
        "type": "bytes32"
      },
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "hasRole",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "spender",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "addedValue",
        "type": "uint256"
      }
    ],
    "name": "increaseAllowance",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_defaultAdmin",
        "type": "address"
      },
      {
        "internalType": "string",
        "name": "_name",
        "type": "string"
      },
      {
        "internalType": "string",
        "name": "_symbol",
        "type": "string"
      },
      {
        "internalType": "string",
        "name": "_contractURI",
        "type": "string"
      },
      {
        "internalType": "address[]",
        "name": "_trustedForwarders",
        "type": "address[]"
      },
      {
        "internalType": "address",
        "name": "_primarySaleRecipient",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "_platformFeeRecipient",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "_platformFeeBps",
        "type": "uint256"
      }
    ],
    "name": "initialize",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "forwarder",
        "type": "address"
      }
    ],
    "name": "isTrustedForwarder",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "mintTo",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "components": [
          {
            "internalType": "address",
            "name": "to",
            "type": "address"
          },
          {
            "internalType": "address",
            "name": "primarySaleRecipient",
            "type": "address"
          },
          {
            "internalType": "uint256",
            "name": "quantity",
            "type": "uint256"
          },
          {
            "internalType": "uint256",
            "name": "price",
            "type": "uint256"
          },
          {
            "internalType": "address",
            "name": "currency",
            "type": "address"
          },
          {
            "internalType": "uint128",
            "name": "validityStartTimestamp",
            "type": "uint128"
          },
          {
            "internalType": "uint128",
            "name": "validityEndTimestamp",
            "type": "uint128"
          },
          {
            "internalType": "bytes32",
            "name": "uid",
            "type": "bytes32"
          }
        ],
        "internalType": "struct ITokenERC20.MintRequest",
        "name": "_req",
        "type": "tuple"
      },
      {
        "internalType": "bytes",
        "name": "_signature",
        "type": "bytes"
      }
    ],
    "name": "mintWithSignature",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bytes[]",
        "name": "data",
        "type": "bytes[]"
      }
    ],
    "name": "multicall",
    "outputs": [
      {
        "internalType": "bytes[]",
        "name": "results",
        "type": "bytes[]"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "name",
    "outputs": [
      {
        "internalType": "string",
        "name": "",
        "type": "string"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "owner",
        "type": "address"
      }
    ],
    "name": "nonces",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "numCheckpoints",
    "outputs": [
      {
        "internalType": "uint32",
        "name": "",
        "type": "uint32"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "owner",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "spender",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "value",
        "type": "uint256"
      },
      {
        "internalType": "uint256",
        "name": "deadline",
        "type": "uint256"
      },
      {
        "internalType": "uint8",
        "name": "v",
        "type": "uint8"
      },
      {
        "internalType": "bytes32",
        "name": "r",
        "type": "bytes32"
      },
      {
        "internalType": "bytes32",
        "name": "s",
        "type": "bytes32"
      }
    ],
    "name": "permit",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "primarySaleRecipient",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bytes32",
        "name": "role",
        "type": "bytes32"
      },
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "renounceRole",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bytes32",
        "name": "role",
        "type": "bytes32"
      },
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "revokeRole",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "string",
        "name": "_uri",
        "type": "string"
      }
    ],
    "name": "setContractURI",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_platformFeeRecipient",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "_platformFeeBps",
        "type": "uint256"
      }
    ],
    "name": "setPlatformFeeInfo",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "_saleRecipient",
        "type": "address"
      }
    ],
    "name": "setPrimarySaleRecipient",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bytes4",
        "name": "interfaceId",
        "type": "bytes4"
      }
    ],
    "name": "supportsInterface",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "symbol",
    "outputs": [
      {
        "internalType": "string",
        "name": "",
        "type": "string"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "totalSupply",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "transfer",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "from",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "transferFrom",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "components": [
          {
            "internalType": "address",
            "name": "to",
            "type": "address"
          },
          {
            "internalType": "address",
            "name": "primarySaleRecipient",
            "type": "address"
          },
          {
            "internalType": "uint256",
            "name": "quantity",
            "type": "uint256"
          },
          {
            "internalType": "uint256",
            "name": "price",
            "type": "uint256"
          },
          {
            "internalType": "address",
            "name": "currency",
            "type": "address"
          },
          {
            "internalType": "uint128",
            "name": "validityStartTimestamp",
            "type": "uint128"
          },
          {
            "internalType": "uint128",
            "name": "validityEndTimestamp",
            "type": "uint128"
          },
          {
            "internalType": "bytes32",
            "name": "uid",
            "type": "bytes32"
          }
        ],
        "internalType": "struct ITokenERC20.MintRequest",
        "name": "_req",
        "type": "tuple"
      },
      {
        "internalType": "bytes",
        "name": "_signature",
        "type": "bytes"
      }
    ],
    "name": "verify",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      },
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  }
]
''')

collections_info = {
    "0x3Ab1A1eB2ccd98fB0aa62721525BD3F21A37d298": {
        "name": "Finance 100", "value": 100, "compound_rate": 0.015, "compound_period": 6,
        "min_contract": 24, "max_contract": 36
    },
    "0x5F959e844D38DBF8A696110C40e622040d6BA009": {
        "name": "Finance 300", "value": 300, "compound_rate": 0.015, "compound_period": 6,
        "min_contract": 24, "max_contract": 36
    },
    "0x950838cC769DE033d8cc2b6B3bD2F2E7bCc45Fd4": {
        "name": "Finance 500", "value": 500, "compound_rate": 0.015, "compound_period": 6,
        "min_contract": 24, "max_contract": 36
    },
    "0xC09a41E1432A7b898315114a802C42bB58792bb8": {
        "name": "Finance 1000", "value": 1000, "compound_rate": 0.015, "compound_period": 6,
        "min_contract": 24, "max_contract": 36
    },
    "0x3857C26c33f35084c7DA8774d1E176A93bEE2DFB": {
        "name": "Finance 3000", "value": 3000, "compound_rate": 0.02, "compound_period": 6,
        "min_contract": 18, "max_contract": 24
    },
    "0x3795073983495AB2848a0C501D11A85BE3b16981": {
        "name": "Finance 5000", "value": 5000, "compound_rate": 0.02, "compound_period": 6,
        "min_contract": 18, "max_contract": 24
    },
    "0x3af00d4b4490dB4b90f9d54B62C97d26d5838cBA": {
        "name": "Finance 10000", "value": 10000, "compound_rate": 0.025, "compound_period": 3,
        "min_contract": 18, "max_contract": 24
    },
    "0xd233Ae7d4D5DbdA8F8Cae299467921Cee93e01F4": {
        "name": "Finance 30000", "value": 30000, "compound_rate": 0.025, "compound_period": 1,
        "min_contract": 6, "max_contract": 12
    },
    "0x98D7A49Dc0d09B489d17d45c54C85b75c23a1548": {
        "name": "Finance 50000", "value": 50000, "compound_rate": 0.03, "compound_period": 1,
        "min_contract": 6, "max_contract": 12
    }
}

def get_nft_transactions(contract_address):
  
    params = {
        'module': 'account',
        'action': 'txlist',
        'address': contract_address,
        'startblock': 0,
        'endblock': 99999999,
        'sort': 'asc',
        'apikey': API_KEY
    }

    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()  # Solleva un'eccezione per codici di stato HTTP non 2xx
        data = response.json()
        
        if data['status'] == '1':
            return data['result']
        else:
            print(f"Errore API per {contract_address}: {data['message']}")
            if 'result' in data:
                print(f"Dettagli risultato: {data['result']}")
            return []
    except requests.RequestException as e:
        print(f"Errore di rete per {contract_address}: {str(e)}")
        return []

def calculate_all_compound_dates(start_date, collection_info):
    compound_period = collection_info['compound_period']
    max_contract_months = collection_info['max_contract']
    
    try:
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
    except ValueError:
        try:
            current_date = datetime.strptime(start_date, '%d/%m/%Y')
        except ValueError:
            raise ValueError(f"Formato data non valido: {start_date}. Usare 'YYYY-MM-DD' o 'DD/MM/YYYY'.")

    compound_dates = []
    contract_end_date = current_date + timedelta(days=max_contract_months * 30)  # Approssimazione

    while current_date < contract_end_date:
        next_date = calculate_next_compound_date(current_date.strftime('%d/%m/%Y'), compound_period)
        compound_dates.append(next_date)
        current_date = datetime.strptime(next_date, '%d/%m/%Y')

    compound_info = {}
    ordinals = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth']
    
    for i, date in enumerate(compound_dates[:6]):  # Limitiamo a 6 date
        ordinal = ordinals[i]
        compound_info[f"{ordinal}_compoundDate"] = date
        compound_info[f"isSent_{ordinal}_compoundDate"] = False
        
def calculate_next_compound_date(current_date, compound_period):
    try:
        current_date = datetime.strptime(current_date, '%Y-%m-%d')
    except ValueError:
        try:
            current_date = datetime.strptime(current_date, '%d/%m/%Y')
        except ValueError:
            raise ValueError(f"Formato data non valido: {current_date}. Usare 'YYYY-MM-DD' o 'DD/MM/YYYY'.")

    years_to_add = compound_period // 12
    months_to_add = compound_period % 12
    
    next_year = current_date.year + years_to_add
    next_month = current_date.month + months_to_add
    
    if next_month > 12:
        next_year += 1
        next_month -= 12
    
    # Assicuriamoci che il giorno sia valido per il nuovo mese/anno
    last_day_of_month = calendar.monthrange(next_year, next_month)[1]
    next_day = min(current_date.day, last_day_of_month)
    
    next_date = current_date.replace(year=next_year, month=next_month, day=next_day)
    
    # Aggiustiamo al 15 del mese come richiesto
    if next_date.day < 15:
        next_date = next_date.replace(day=15)
    elif next_date.day > 15:
        if next_date.month == 12:
            next_date = next_date.replace(year=next_date.year + 1, month=1, day=15)
        else:
            next_date = next_date.replace(month=next_date.month + 1, day=15)
    
    return next_date.strftime('%d/%m/%Y')

def calculate_compound(initial_value, monthly_rate, months):
    value = initial_value
    for _ in range(months):
        value += value * monthly_rate
    return value

def to_checksum_address(address):
    return Web3.to_checksum_address(address)
  
def get_raw_transaction(signed_tx):
    if hasattr(signed_tx, 'rawTransaction'):
        return signed_tx.rawTransaction
    elif hasattr(signed_tx, 'raw_transaction'):
        return signed_tx.raw_transaction
    elif callable(getattr(signed_tx, 'rawTransaction', None)):
        return signed_tx.rawTransaction()
    else:
        raise AttributeError("Impossibile ottenere la transazione raw dalla transazione firmata")
      
def check_balance_before_send(from_address, to_address, amount):
    contract = w3.eth.contract(address=TOKEN_ADDRESS, abi=ERC20_ABI)
    balance = contract.functions.balanceOf(from_address).call()
    if balance < amount:
        raise ValueError(f"Saldo insufficiente. Necessario: {amount}, Disponibile: {balance}")
    print(f"Saldo sufficiente. Necessario: {amount}, Disponibile: {balance}")

def get_next_nonce(w3, address):
    # Ottieni il nonce on-chain
    on_chain_nonce = w3.eth.get_transaction_count(address)
    
    # Ottieni il nonce delle transazioni in sospeso
    pending_nonce = w3.eth.get_transaction_count(address, 'pending')
    
    # Usa il massimo tra i due
    return max(on_chain_nonce, pending_nonce)

def send_test_transaction(to_address, amount):
    to_address = Web3.to_checksum_address(to_address)
    if not w3.is_address(to_address):
        raise ValueError("Indirizzo non valido")

    test_amount = max(amount // 100, 1)  # Usiamo almeno 1 wei

    print(f"\nTEST: Tentativo di invio di {test_amount} wei ({test_amount / 10**18:.9f} tokens) a {to_address}")
    print(f"(1% dell'importo originale di {amount} wei ({amount / 10**18:.6f} tokens))")

    try:
        tx_hash = send_transaction_with_retry(w3, contract, to_address, test_amount)
        print(f"TEST: Transazione inviata con successo. Hash: {tx_hash}")
        return tx_hash
    except Exception as e:
        print(f"TEST: Errore nell'invio della transazione: {str(e)}")
        raise

def send_transaction_with_retry(w3, contract, to_address, amount, max_retries=3):
    for attempt in range(max_retries):
        try:
            # Verifica il saldo
            balance = contract.functions.balanceOf(w3.eth.default_account).call()
            print(f"Saldo attuale: {balance / 10**18:.6f} tokens")
            if balance < amount:
                raise ValueError(f"Saldo insufficiente. Richiesto: {amount / 10**18:.6f}, Disponibile: {balance / 10**18:.6f}")

            # Verifica l'approvazione
            allowance = contract.functions.allowance(w3.eth.default_account, contract.address).call()
            print(f"Approvazione attuale: {allowance / 10**18:.6f} tokens")
            if allowance < amount:
                approval_amount = max(amount, 10**25)  # Approva 10 milioni di token o l'importo richiesto, il maggiore dei due
                print(f"Approvazione insufficiente. Approvazione in corso per {approval_amount / 10**18:.6f} tokens...")
                approve_tx = contract.functions.approve(contract.address, approval_amount).transact()
                w3.eth.wait_for_transaction_receipt(approve_tx)
                print("Approvazione completata.")
            else:
                print("Approvazione sufficiente. Procedendo con la transazione.")

            # Invia la transazione
            tx_hash = contract.functions.transfer(to_address, amount).transact()
            print(f"Transazione inviata. Hash: {tx_hash.hex()}")

            # Attendi la conferma
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            if tx_receipt['status'] == 1:
                print(f"Transazione confermata con successo: {tx_hash.hex()}")
                return tx_hash.hex()
            else:
                raise Exception("La transazione è fallita")
        except ValueError as e:
            print(f"Errore di valore: {str(e)}")
            if "nonce too low" in str(e).lower():
                print(f"Nonce troppo basso. Tentativo {attempt + 1} di {max_retries}. Ritentando...")
                time.sleep(2)
            else:
                raise
        except Exception as e:
            print(f"Errore imprevisto: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Tentativo {attempt + 1} di {max_retries}. Ritentando...")
                time.sleep(5)
            else:
                raise

    raise Exception(f"Impossibile inviare la transazione dopo {max_retries} tentativi")
  
def send_erc20_transaction(to_address, amount, max_retries=3):
    to_address = to_checksum_address(to_address)
    if not w3.is_address(to_address):
        raise ValueError("Indirizzo non valido")

    account = Account.from_key(PRIVATE_KEY)
    contract = w3.eth.contract(address=to_checksum_address(TOKEN_ADDRESS), abi=ERC20_ABI)

    print(f"\nDettagli della transazione:")
    print(f"Da: {account.address}")
    print(f"A: {to_address}")
    print(f"Importo: {amount} wei ({amount / 10**18:.9f} tokens)")
    print(f"Token Address: {TOKEN_ADDRESS}")

    for attempt in range(max_retries):
        try:
            nonce = get_next_nonce(w3, account.address)
            print(f"Nonce: {nonce}")

            tx = contract.functions.transfer(to_address, amount).build_transaction({
                'chainId': w3.eth.chain_id,
                'gas': 200000,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce,
            })

            print(f"Gas Price: {tx['gasPrice']} wei")
            print(f"Gas Limit: {tx['gas']}")

            signed_tx = account.sign_transaction(tx)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(f"Transazione inviata. Hash: {tx_hash.hex()}")

            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            if tx_receipt['status'] == 1:
                print(f"Transazione confermata con successo: {tx_hash.hex()}")
                print(f"Blocco: {tx_receipt['blockNumber']}")
                print(f"Gas Usato: {tx_receipt['gasUsed']}")
                return tx_hash.hex()
            else:
                raise Exception("La transazione è fallita")
        except ValueError as e:
            print(f"Errore: {str(e)}")
            if "nonce too low" in str(e):
                print(f"Nonce troppo basso. Tentativo {attempt + 1} di {max_retries}. Ritentando...")
                time.sleep(2)
            else:
                raise
        except TransactionNotFound:
            print(f"Transazione non trovata. Tentativo {attempt + 1} di {max_retries}. Ritentando...")
            time.sleep(5)
        except Exception as e:
            print(f"Errore imprevisto: {str(e)}")
            raise

    raise Exception(f"Impossibile inviare la transazione dopo {max_retries} tentativi")
      
def process_compound_transactions(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    today = datetime.now().strftime('%Y-%m-%d')  # Usiamo il formato 'YYYY-MM-DD'
    updates_made = False

    for collection_address, transactions in data.items():
        for tx in transactions:
            if TEST_MODE or (tx['next_compound_date'] == today and not tx['is_closed']):
                compound_amount = int(tx['compound_value'] * 10**18)  # Converti in wei
                
                print(f"\nProcessing compound for token ID {tx['tokenId']}:")
                print(f"Initial value: {tx['starting_balance']:.6f} tokens")
                print(f"Compound value: {tx['compound_value']:.6f} tokens")
                print(f"Interest earned: {tx['compound_value'] - tx['starting_balance']:.6f} tokens")
                print(f"Full amount to send: {compound_amount} wei ({tx['compound_value']:.6f} tokens)")

                try:
                    to_address = to_checksum_address(tx['from'])
                    if TEST_MODE:
                        print(f"TEST MODE: Invio transazione di test (1% dell'importo reale)")
                        tx_hash = send_test_transaction(to_address, compound_amount)
                    else:
                        print(f"Invio di {tx['compound_value']:.6f} token ({compound_amount} wei) all'indirizzo {to_address}")
                        tx_hash = send_erc20_transaction(to_address, compound_amount)
                    
                    tx['is_closed'] = True
                    tx['compound_tx_hash'] = tx_hash
                    tx['compound_date'] = today
                    tx['current_balance'] = tx['compound_value']
                    
                    # Calcoliamo la prossima data di compound
                    tx['next_compound_date'] = calculate_next_compound_date(today, tx['compound_period'])
                    
                    updates_made = True
                    print(f"Transazione compound completata per token ID {tx['tokenId']}")
                    print(f"Hash transazione: {tx_hash}")
                except Exception as e:
                    print(f"Errore nell'invio della transazione per token ID {tx['tokenId']}:")
                    print(f"Tipo di errore: {type(e).__name__}")
                    print(f"Messaggio di errore: {str(e)}")
                    print(f"Dettagli transazione: To: {tx['from']}, Amount: {compound_amount} wei")

    if updates_made:
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
        print("\nFile JSON aggiornato con le nuove transazioni di compound")
    else:
        print("\nNessuna transazione di compound da processare")
        
def process_transactions(transactions, collection_address, existing_data):
    collection_info = collections_info[collection_address]
    existing_transactions = existing_data.get(collection_address, [])
    existing_hashes = {tx['hash'] for tx in existing_transactions}
    
    def calculate_all_compound_dates(start_date, compound_period, max_periods):
        all_dates = []
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        for _ in range(max_periods):
            next_date = calculate_next_compound_date(current_date.strftime('%Y-%m-%d'), compound_period)
            all_dates.append(next_date)
            current_date = datetime.strptime(next_date, '%d/%m/%Y')
        return all_dates

    for tx in transactions:
        value_in_matic = float(tx['value']) / 1e18
        if value_in_matic > 0.99 and tx['hash'] not in existing_hashes:
            tx_date = datetime.fromtimestamp(int(tx['timeStamp']))
            
            compound_period = collection_info['compound_period']
            max_contract_months = collection_info['max_contract']
            max_periods = min(12, max_contract_months // compound_period)
            
            all_compound_dates = calculate_all_compound_dates(tx_date.strftime("%Y-%m-%d"), compound_period, max_periods)
            
            initial_value = value_in_matic * collection_info['value']
            final_value = calculate_compound(
                initial_value,
                collection_info['compound_rate'],
                compound_period
            )
            
            interest_earned = final_value - initial_value
            
            compound_dates_dict = {}
            for i in range(12):
                if i < len(all_compound_dates):
                    compound_dates_dict[f'compound_date_{i+1}'] = all_compound_dates[i]
                    compound_dates_dict[f'isSent_compound_{i+1}'] = False
                else:
                    compound_dates_dict[f'compound_date_{i+1}'] = "N/A"
                    compound_dates_dict[f'isSent_compound_{i+1}'] = None

            new_tx = {
                'tokenId': str(len(existing_transactions) + 1),
                'hash': tx['hash'],
                'from': tx['from'],
                'to': tx['to'],
                'value': value_in_matic,
                'date': tx_date.strftime('%Y-%m-%d %H:%M:%S'),
                'is_closed': False,
                'starting_balance': initial_value,
                'current_balance': initial_value,
                'collection_address': collection_address,
                'collection_name': collection_info['name'],
                'collection_value': collection_info['value'],
                'compound_rate': collection_info['compound_rate'],
                'compound_period': compound_period,
                'min_contract': collection_info['min_contract'],
                'max_contract': collection_info['max_contract'],
                'compound_value': final_value,
                'interest_earned': interest_earned,
                **compound_dates_dict
            }
            
            existing_transactions.append(new_tx)
            existing_hashes.add(tx['hash'])

    existing_data[collection_address] = existing_transactions
    return existing_data
  
def send_erc20_transaction(to_address, amount):
    if not w3.is_address(to_address):
        raise ValueError("Indirizzo non valido")

    account = Account.from_key(PRIVATE_KEY)
    contract = w3.eth.contract(address=TOKEN_ADDRESS, abi=ERC20_ABI)

    nonce = w3.eth.get_transaction_count(account.address)
    tx = contract.functions.transfer(to_address, amount).build_transaction({
        'chainId': w3.eth.chain_id,
        'gas': 200000,
        'gasPrice': w3.eth.gas_price,
        'nonce': nonce,
    })

    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if tx_receipt['status'] == 1:
        print(f"Transazione inviata con successo: {tx_hash.hex()}")
        return tx_hash.hex()
    else:
        raise Exception("La transazione è fallita")

def process_compound_transactions(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    today = datetime.now().strftime('%d/%m/%Y')
    updates_made = False

    for collection_address, transactions in data.items():
        for tx in transactions:
            if TEST_MODE or (tx['next_compound_date'] == today and not tx['is_closed']):
                compound_amount = int((tx['compound_value'] - tx['starting_balance']) * 10**18)  # Converti in wei
                
                try:
                    to_address = to_checksum_address(tx['from'])
                    if TEST_MODE:
                        print(f"TEST MODE: Simulazione invio transazione per token ID {tx['tokenId']}")
                        tx_hash = send_test_transaction(to_address, compound_amount)
                    else:
                        tx_hash = send_erc20_transaction(to_address, compound_amount)
                    
                    tx['is_closed'] = True
                    tx['compound_tx_hash'] = tx_hash
                    tx['compound_date'] = today
                    tx['current_balance'] = tx['compound_value']
                    
                    # Utilizziamo la funzione calculate_next_compound_date per calcolare la prossima data di compound
                    tx['next_compound_date'] = calculate_next_compound_date(today, tx['compound_period'])
                    
                    updates_made = True
                    print(f"Processata transazione compound per token ID {tx['tokenId']}")
                except Exception as e:
                    print(f"Errore nell'invio della transazione per token ID {tx['tokenId']}:")
                    print(f"Tipo di errore: {type(e).__name__}")
                    print(f"Messaggio di errore: {str(e)}")
                    print(f"Dettagli transazione: To: {tx['from']}, Amount: {compound_amount}")

    if updates_made:
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
        print("File JSON aggiornato con le nuove transazioni di compound")
    else:
        print("Nessuna transazione di compound da processare")
        
def check_token_balance(address):
    contract = w3.eth.contract(address=TOKEN_ADDRESS, abi=ERC20_ABI)
    balance = contract.functions.balanceOf(address).call()
    return balance

def save_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)


def main():
    # Carica i dati esistenti dal file JSON, se esiste
    filename = 'nft_transactions.json'
    try:
        with open(filename, 'r') as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = {}

    for collection_address in collections_info.keys():
        print(f"\nElaborazione della collezione: {collections_info[collection_address]['name']}")
        transactions = get_nft_transactions(collection_address)
        transactions_over_1_matic = sum(1 for tx in transactions if float(tx['value']) / 1e18 > 0.99)
        
        # Passa i dati esistenti alla funzione process_transactions
        updated_data = process_transactions(transactions, collection_address, existing_data)
        
        existing_transactions = updated_data.get(collection_address, [])
        print(f"Numero totale di transazioni: {len(transactions)}")
        print(f"Transazioni con valore > 1 MATIC trovate: {transactions_over_1_matic}")
        print(f"Transazioni con valore > 1 MATIC nel file: {len(existing_transactions)}")

        time.sleep(5)  # Aggiungi un ritardo di 5 secondi tra le richieste

    # Salva i dati aggiornati nel file JSON
    save_to_file(updated_data, filename)
    print(f"\nTutti i dati sono stati salvati in {os.path.abspath(filename)}")

if __name__ == "__main__":
    main()
    