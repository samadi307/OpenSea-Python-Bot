# OpenSea-Python-Bot
OpenSea Python Bot can be used in 2 modes. When `--nft` parameter is passed, it will allow you to continuously monitor an NFT project and automatically snipe/buy if the price of the NFT is 50% or lower than it's floor value. If the price of the NFT is 20-40% below it's floor, then the bot can send a notification on Discord or print the result on-screen. The script can also be used to buy a specific NFT by passing the `--url` parameter. In that case, the bot will automatically buy the NFT at its current price value.

# Usage
### Installation:

The OpenSea Python3 bot only works with Python3. To install the required packages you can do the following:
```
git clone https://github.com/OpenSeaSnipers/OpenSea-Python-Bot.git
cd OpenSea-Python-Bot
pip3 install -r requirements.txt
```
Usage of the script is straightforward:
```
Usage: python3 python_sniper.py [-h] [--nft NFT] --mnemonic MNEMONIC --wallet WALLET [--url URL]

optional arguments:
  -h, --help           show this help message and exit
  --nft NFT            Name of the NFT collection. Eg: boredapeyachtclub
  --mnemonic MNEMONIC  The mnemonic/seed phrase of the wallet to use.(Trustwallet, MetaMask etc)
  --wallet WALLET      The ETH address linked to the mnemonic above.
  --url URL            URL of the NFT asset on OpenSea. Eg: https://opensea.io/assets/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d/5875

```

### NFT Collection:
To input the exact nft name, navigate to the NFT collection and copy the value as shown below:
![alt text](https://github.com/OpenSeaSnipers/OpenSea-Python-Bot/blob/main/nft-name.png?raw=true)

## Continous Monitor Mode
The continous monitor mode allow you to look at an NFT continously and alert in the case the NFT is below floor price. If the value is below 50% floor then an automatic buy can be triggered. Recently OpenSea has made it difficult for sales bot to work by rate limiting API calls. The code has been altered to add delays and use new techniques to bypass this. With that, the bot will function smoothly but at times OpenSea can crash so keep an eye out. The parameters `--nft`, `--mnemonic` & `--wallet` are mandatory to make the call.
```
Example:

C:\> python3 python_sniper.py --nft mekaverse --mnemonic 'bore apple cloud gray solid winter people ' --wallet '0xf2946C517462e8d70c7cfad32eE5ce024d9dA21c'

Fetching mekaverse
==================================
NFT Contract Address:  0x9a534628b4062e123ce7ee2222ec20b86e16ca8f
Floor: 0.4851 ETH
Website:  https://themekaverse.com/
Verified Status:  verified
Fetching periodic listing for NFT:  mekaverse

Potential Listing Below floor: https://opensea.io/assets/0x9a534628b4062e123ce7ee2222ec20b86e16ca8f/6186
```

## Automatic Buy Mode (curretly in beta)
Few tweaks are being made so expect a full commit in a few days. Currently in beta stage.
```
Example:

C:\> python3 python_sniper.py --url https://opensea.io/assets/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d/5875

Fetching NFT
=================================
NFT Contract Address: 0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d
Price: 38 ETH
Performing Transaction.....
Success!
```
