# PC Writeup - by Thammanant Thamtaranon  

- PC is an easy Linux-based machine hosted on Hack The Box.

## Reconnaissance  
- I began with a full TCP port scan including service/version detection and OS fingerprinting:  `nmap -A -T4 -p- 10.10.11.214`  

![Nmap_Scan](Nmap_Scan.png)  

- The scan revealed two open ports:  
  - 22 (SSH)  
  - 50051 (gRPC)  

## Scanning & Enumeration  
- I connected to the gRPC service:  
![GRPC](GRPC.png)  

- Listing the available methods revealed potential entry points:  
![Methods](Methods.png)  

- The getInfo method required authentication:  
![MissingToken](MissingToken.png)  

- When attempting to register as 'admin', I discovered the account already existed:  
![Duplicate](Duplicate.png)  

- I successfully logged in using admin:admin credentials:  
![Admin](Admin.png)  

- Using verbose mode (`-vv` flag) revealed the authentication token:  
![Token](Token.png)  

- However, the getInfo method didn't return useful information even with the token.

## Exploitation  
- Testing for SQL injection vulnerabilities revealed the ID parameter was vulnerable to the payload `1 UNION SELECT 1`.  

- After identifying the backend as SQLite:  
![SQLite](SQLite.png)  

- Since the response required integer values, I converted database information to hex for extraction:  
![SQLi1](SQLi1.png)  
![SQLi2](SQLi2.png)  
![SQLi3](SQLi3.png)  
![SQLi4](SQLi4.png)  
![SQLi5](SQLi5.png)  
![SQLi6](SQLi6.png)  

- This provided SSH access as user 'sau':  
![Sau](Sau.png)  

- I successfully retrieved the user flag.

## Privilege Escalation  
- Checking sudo permissions showed no privileges for user 'sau':  `sudo -l`  

- I discovered internal services using:  `ss -tulpn`  

- This revealed a service running on port 8000:  
![Internal](Internal.png)  

- I established an SSH tunnel to access the service locally:  `ssh sau@10.10.11.214 -L 8000:localhost:8000`  

- The service was identified as pyLoad (based on the 2022 copyright notice), suggesting potential CVEs from 2022-2023. After researching online, I found **CVE-2023-0297**.  

- Testing for **CVE-2023-0297** by accessing `/flash/addcrypted2`:  
![POC](POC.png)  

- After confirming the vulnerability, I used a public POC from Exploit-DB:  
![Exploit1](Exploit1.png)  
![Exploit2](Exploit2.png)  

- Following a successful callback, I modified the exploit by uploading a reverse shell and executing it, which resulted in root access:  
![Root](Root.png)  

- I successfully retrieved the root flag, completing the machine.
