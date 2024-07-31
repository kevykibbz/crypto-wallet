import json

def normalize_key(key):
    """Normalize keys by stripping extra spaces and converting to uppercase."""
    return key.strip().upper()

def find_common_keys(json1, json2):
    """Find common keys in two JSON dictionaries."""
    normalized_keys1 = {normalize_key(key) for key in json1.keys()}
    normalized_keys2 = {normalize_key(key) for key in json2.keys()}
    common_normalized_keys = normalized_keys1 & normalized_keys2

    # Retrieve original keys from the normalized keys
    common_keys = {key for key in json1.keys() if normalize_key(key) in common_normalized_keys}
    return common_keys

def print_common_keys(json1, json2):
    """Print common keys found in two JSON dictionaries."""
    # Find common keys
    common_keys = find_common_keys(json1, json2)
    
    # Print common keys
    if common_keys:
        print("Common keys found in both JSON objects:")
        for key in common_keys:
            print(key)
    else:
        print("No common keys found.")

if __name__ == "__main__":
    # Define two JSON objects as dictionaries
    json1 = {
    "DATE :": "17/07/2024",
    "PERMIT ARRIVAL NUMBER :": "7485965874514256",
    "PERMIT CODE :": "541578956254758",
    "TRANSFER DATA ENCRYPTION CODE :": "941578596-GFAG",
    "TRANSACTION CODE :": "5359478695VFT641758695",
    "LOGIN DOMAIN :": "GFAG",
    "REFERENCE NUMBER :": "947145869587458",
    "TRANSFER CODE :": "574895142569:65897458KHR68475957",
    "FARM NAME :": "FARM 42",
    "AMOUNT :": "EUR 100.000.000.000.00",
    "FINAL BLOCKING CODE :": "UBSW365748957459",
    "UNIQUE TRANSACTION CODE :": "UBSWCHZHB0A5415786954715869547145259",
    "LOGIN SERVER :": "GFAG47589MW",
    "CLEARING CODE :": "UBSWCHZH8OA",
    "SERVER GLOBAL IP (ORIGIN) :": "AS212238",
    "WTS (WINDOW TERMINAL SERVER) :": "1001958",
    "CURRENCY :": "EURO (EUR)",
    "UPLOAD CODE :": "8415748596524157",
    "CLEARING HOUSE NUMBER :": "369574785968UBSWCHZH80A758968574514",
    "FILE FORMAT :": "FIN",
    "SERVER GLOBAL IP :": "169.150.197.205",
    "TIME :": "18:51:52",
    "USER NAME :": "GFAG6257",
    "INTERBANKING BLOCING CODE :": "72H: M: K: BR458965745865248",
    "FINAL RELEASE CODE :": "UBSWCH68541586",
    "IDENTITY CODE :": "21K M6 P4 NW 57VFQ 47L",
    "IMAD NUMBER :": "00000000BGQ-BY-05",
    "ENCODING :": "UTF I 9",
    "UPLOAD FORMAT": "DROPBOX UPLOAD FORMAT",
    "FILE EXTENSION :": "AES",
    "FUNDS TYPE": "MO FUNDS",
    "LANG2XGEPAY01 (License)": "Active port-basic slot (slot-id) port <port-limit> activated",
    "Upload in Process: 40%": "SRV2",
    "Upload in Process: 80%": "SRV3",
    "AMOUNT:": "100,000,000,000.00",
    "Upload in Process: 100%": "SRV4",
    "IPSVR:": "DROPBOX UPLOAD ACCESS",
    "CUR:": "EURO",
    "EPLD Version:": "V120",
    "EPGA1 Version:": "V130",
    "BEGIN CERTIFICATE": "",
    "IPIP VER:": "IPV4/IPV6",
    "Upload in Process: 10%": "SRV1",
    "EPLD Version: V120": "",
    "Upload in Process 10% SRV1": "",
    "LANG4XGEPAY01": "(License)",
    "INFG": "GT5NFT73 REV Y",
    "END CERTIFICATE": "",
    "FUNDS UPLOAD": "SUDESSFUL",
    "ALL": "ACCESS",
    "HAS BEEN": "GRANTED",
    "PCB Version: CTGICXPI REV A PCB Version CTGICXPI REV A": "",
    "> SENDER/ORDERING CUSTOMER": "",
    "DATE:": "17/07/2024",
    "TRANSMISSION:": "OK",
    "TIME:": "18:51:52",
    "END OF MESSAGE: OK": ""
}

    json2 = {
    "PROTOCOL:": "SFTP",
    "Network Delivery Status:": "NetworkAck",
    "32A:": "VALUE DATE",
    "Priority/Delivery:": "Urgent",
    "SENDER:": "BANK OF CANADA (CAYMAN) LTD",
    "BIC:": "ROYCKYKTXXX",
    "USER ID:": "",
    "Message Input Reference:": "9:11:2370924ROYCKYKTXXX314634c2024",
    "AMOUNT:": "",
    "23B:": "Bank Operation Code",
    "50K:": "CLIENT GULEN RESOURCES INTERNATIONAL",
    "CLEARING HOUSE ACC.:": "529864",
    "SENDING DATE:": "",
    "NAME:": "ROYAL BANK OF CANADA (CAYMAN) LTD",
    "CLIENT NAME:": "RBC1.COM",
    "SERVER IP:": ": 193.150.166.0/24/193.150.166.0/243",
    "COMMON SERVER": "IP: 193.150.166.0/243",
    "SORT CODE:": "A23F17.0131.47.RBC5",
    "21: Sender's Reference": "ROYCKYKTXXX - 7277103S2S",
    "FARM NAME:": "RBC1.RFGD.COM",
    "ADDRESS:": "24 SHEDDEN ROAD, GEORGE TOWN, CAYMAN ISLANDS",
    "SERVER ID:": "AS45277",
    "TRANSACTION CODE:": "GUL/RBC/SFTPNETS2S-02-024",
    "IMAD NO.:": "487NA",
    "Message Output Reference:": "9:33:1670924SCENAIDJAKU314655f2024",
    "IDENTITY CODE:": "RB771590",
    "DATE:": "JULY, 2024",
    "REFERENCE": "NO.: RBC-561117-9",
    "ACCOUNT NUMBER:": "2011759",
    "21C: TRN:": "5897017305319779",
    "Message Header": "",
    "MARCO_ZWICK": "",
    "33B: CURRENCY/INSTRUCTED AMOUNT": "CURRENCY: EURO \u20ac10,000,000,972.00 (TEN BILLION, NINE HUNDRED AND SEVENTY TWO EUROS ONLY)",
    "ROYAL": "",
    "SFTP": "JULY 9, 2024 LOCALSWIFTACKS-IPS2S8011-000103",
    "CLIENT: GULEN RESOURCES INTERNATIONAL LTD": "",
    "Input Time: 9:11:23": "06521437+4'165107 RBCCAY S2S",
    "ADDRESS: 24 SHEDDEN ROAD, GEORGE": "",
    "Notification (Transmission) of Original sent to": "SERVER(ACK)",
    "Interventions": "",
    "REMIT TANCE INFORMATION": "/ROC/",
    "VALUED DATE:": "7.09.24",
    "EURO CASH": "(\u20ac10,000,000,972.00)",
    "PROTOCOL: SFTP": "DATE: JULY 9, 2024",
    "Message Trailer": "",
    "CONFIRMATION FINTRAC ANSWER BACK": "MESSAGE HAS BEEN TRANSMITTED",
    "END": "TRANSMISSION",
    ">Enter_identity_code_MFIID.C101773_corresponding": ">>Enter_farm_name_Gulen Resources Company",
    "Subnet mask": "127.31.110.174",
    "Link-Local IPV6m Address": "di61:7757:04d:be59:e335%7",
    "Temporary Iv6 Address": "2024:e68:7110:77a6:hrc7:cec3;7d9c:ad13",
    ">>>Enter": "",
    ">>>REN:": "",
    ">>>Permit_arrival_funds_number_SCF-664M388RT667": "",
    "IPV6 address": "2024:e68:5613:77a6:jj34:bv59:c6671",
    "IPV4 Address": "127.31.110.174",
    ">>>Enter_inter_bank_blocking_code_177A:sg11726YYBSB_correspond": "",
    ">>>Enter_access_R.B.C.F777.CI": "",
    ">>>Transaction": "",
    ">>>Enter_": "",
    ">>>TRN:": "",
    ">>>Transfer confirmation report_10B_EUR_NETSFTP_GLOBAL": ">>>SERVER_TRANSFER_SUCCESS_SUCCESS_SUCCESS_SUCCESS",
    ">>>Currency_euro_corresponding": "",
    ">>>Enter_UTR_RBCGCI2011759_2011759_corresponding": ""
}
    
    # Print common keys
    print_common_keys(json1, json2)
