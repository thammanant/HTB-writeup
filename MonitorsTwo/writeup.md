# MonitorsTwo Writeup - by Thammanant Thamtaranon  

- MonitorsTwo is an easy Linux-based machine hosted on Hack The Box.

## Reconnaissance  
- I began with a full TCP port scan including service/version detection and OS fingerprinting:  `nmap -A -T4 -p- 10.10.11.211`  

![Nmap_Scan](Nmap_Scan.png)  

- The scan revealed two open ports:  
  - 22 (SSH)  
  - 80 (HTTP)  

## Scanning & Enumeration  
- We then notice the Cacti version 1.2.22

![Cacti](Cacti.png) 

## Exploitation  
- We then search for Cacti 1.2.22 CVE and found **CVE-2022-46169**.
- **CVE-2022-46169** is an unauthenticated command injection vulnerability. This flaw allows remote attackers to execute arbitrary commands on affected systems without authentication, potentially leading to full server compromise.
- The vulnerability exists in the remote_agent.php file, which is used for data collection in Cacti. Due to insufficient input validation, an attacker can inject malicious commands via crafted HTTP requests.
- We use burp suite and try crafting GET request to `/remote_agent.php?action=polldata&poller_id=1;id&host_id=1&local_data_ids[]=1`. However, we got and error. This suggested that the server might have a white list of IPs.



## Privilege Escalation  
