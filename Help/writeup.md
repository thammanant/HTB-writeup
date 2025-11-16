# Help Writeup - by Thammanant Thamtaranon  
- Help is an easy Linux-based machine hosted on Hack The Box.

## Reconnaissance  
- I began with a full TCP port scan including service/version detection and OS fingerprinting:  
  `nmap -A -T4 -p- 10.10.10.121`  
  ![Nmap_Scan](Nmap_Scan.png)  
- The scan revealed the following open ports:  
  - **22** — SSH  
  - **80** — HTTP  
  - **3000** — HTTP  
- I added `Help.htb` to `/etc/hosts` for proper hostname resolution.

## Scanning & Enumeration  
- I run the Vhost enumeratoin with `ffuf -u http://help.htb -H "Host: FUZZ.help.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -mc all -ac`, but nothing was founded.
- I then run `dirsearch` on both port 80 and 3000
  ![Dirsearch_Scan1](Dirsearch_Scan1.png)
  ![Dirsearch_Scan2](Dirsearch_Scan2.png)
- Visiting `http://htb.help/support/` found a website using `HelpDeskZ`.
  ![HelpDeskZ](HelpDeskZ.png)
- Visiting `http://htb.help:3000` found the message for user `Shiv`.
  ![Message](Message.png)
- visiting `http://help.htb:3000/graphql/` shows `GET query missing.`.
- I then modify the request and sent a query.
  ![QueryPOC](QueryPOC.png)
- This confirm the API Endpoint.
- I then change the query to `{
  "query": "query IntrospectionQuery { __schema { queryType { name fields { name type { name } } } mutationType { name fields { name type { name } } } types { name fields { name type { name kind } } } } }"
}`, This show  everything about its internal structure and the data it can handle.
- We found data type User with username and password field.
  ![API](API.png)
- I then change the query to `{
  "query": "query { user { username password } }"
}`.
  ![Helpme](Helpme.png)
- We then put the password to crackstation and options helme's credentials.
  ![Helpme_Password](Helpme_Password.png)
- Using this credential we logged in to HelpDeskZ.
  ![Login](Login.png)
- 

## Exploitation  


## Privilege Escalation  

