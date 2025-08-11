# CozyHosting Writeup - by Thammanant Thamtaranon  

- CozyHosting is an easy Linux-based machine hosted on Hack The Box.

## Reconnaissance  
- I began with a full TCP port scan including service/version detection and OS fingerprinting:  `nmap -A -T4 -p- 10.10.11.230`  

![Nmap_Scan](Nmap_Scan.png)  

- The scan revealed two open ports:  
  - 22 (SSH)  
  - 80 (HTTP)  

- I added `cozyhosting.htb` to `/etc/hosts` for proper hostname resolution.

## Scanning & Enumeration  
- I performed directory brute-forcing using `dirsearch`:  `dirsearch -u http://cozyhosting.htb`  

![Dirsearch_Scan](Dirsearch_Scan.png)  

- VHost enumeration yielded no results.  
- The scan revealed two interesting paths:  
  - `/actuator`  
  - `/login`  

- The `/actuator` endpoint contained multiple subpaths:  
![Actuator](Actuator.png)  

- The `/actuator/sessions` endpoint revealed active session IDs:  
![Session](Session.png)  

- The `/actuator/mapping` endpoint showed various application routes:  
![Mappings](Mappings.png)  

- I hijacked `kanderson`'s session by modifying my `JSESSIONID` cookie, gaining access as K. Anderson:  
![Dashboard](Dashboard.png)  

## Exploitation  
- Using Burp Suite, I tested for command injection vulnerabilities. Since whitespace was blocked, I used `${IFS}` as a separator:  
![Command_Injection1](Command_Injection1.png)  
![Command_Injection2](Command_Injection2.png)  

- After confirming command injection worked, I attempted to upload a reverse shell. Permission issues forced me to use the `/tmp` directory:  
![Command_Injection3](Command_Injection3.png)  
![Command_Injection4](Command_Injection4.png)  

- Executing the reverse shell granted access as the `app` user:  
![Command_Injection5](Command_Injection5.png)  

- Inspecting `/etc/passwd` confirmed the existence of user `josh`:  
![PASSWD](PASSWD.png)  

- I extracted the application JAR file:  `unzip cloudhosting-0.0.1.jar -d /tmp/extracted_jar/`  

- This revealed PostgreSQL database credentials. I connected to the database:  `psql -h localhost -U postgres -d cozyhosting -W`  

![Credentials](Credentials.png)  

- The database contained hashed credentials for users `kanderson` and `admin`. Using John the Ripper, I cracked the admin hash:  
![Cracked](Cracked.png)  

- The credentials allowed SSH access as `josh`:  
![Josh](Josh.png)  

- I then retrieved the user flag.

## Privilege Escalation  
- Checking sudo permissions revealed an interesting entry:  `sudo -l`  
![SUDO](SUDO.png)  

- Consulting GTFOBins revealed an SSH privilege escalation vector:  
![GTFOBins](GTFOBins.png)  

- Executing the suggested command granted root access:  
![Root](Root.png)  

- Finally, I obtained the root flag, completing the machine.
