# Codify Writeup - by Thammanant Thamtaranon  
- Codify is an easy Linux-based machine hosted on Hack The Box.

## Reconnaissance  
- I started with a full TCP port scan including version detection and OS fingerprinting:  
  `nmap -A -T4 -p- 10.10.11.243`  
![Nmap_Scan1](Nmap_Scan1.png)  
![Nmap_Scan2](Nmap_Scan2.png)  
- Port 80 redirected to port 8161, which prompted for credentials.  
- Tried `admin:admin` and successfully logged in.  
- Other ports returned unreadable or unknown data formats.  
- Nmap revealed the server is running Jetty 9.4.39.v20210325 and ActiveMQ OpenWire transport 5.15.15.

## Scanning & Enumeration  


## Exploitation  

## Privilege Escalation  
