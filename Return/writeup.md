# Return Writeup - by Thammanant Thamtaranon  
- Return is an easy Windows machine hosted on Hack The Box.

## Reconnaissance  
- I started with a full TCP port scan including service/version detection and OS fingerprinting:
```bash
nmap -A -T4 -p- 10.10.10.152
```
![Nmap_Scan](Nmap_Scan.png)  
- The scan showed multiple open ports:  
  - 80 (HTTP)
  - 88 (Kerberos)
  - 135 (MSRPC)
  - 139 (NETBIOS)
  - 389 (LDAP)
  - 445 (SMB)
  - 464 (kpasswd5)
  - 636 (LDAPS)
  - 3268 (LDAPS)
  - 3269 (LDAPS)
  - 5985 (WINRM)
  - 9389 (AD Web Services)

## Scanning & Enumeration 
- I ran a directory brute-force using `dirsearch`:  
  `dirsearch -u 10.10.11.108`  
![Dirsearch_Scan](Dirsearch_Scan.png)
- In `/settings.php`, we founded Server address, Server Port, and Username.
![Setting](Setting.png)
- Clicking the update button sent a request with only IP as the parameter.
![Request](Request.png)
- I then try changing the IP to my IP and run `nc -lvnp 389` on my machine.
- We got a connect that looks like a password.
![Password](Password.png)
- We then use netexec to check if the credential work for any service.
![Services](Services.png)

## Exploitation  
- Since the credntial works for all the services, I try connect to SMB first.
![SMB](SMB.png)
- As we are a high privilege I try use the `psexec` but failed because we do not have the write priviledge.
- So we move on to the WinRM, we use `evil-winrm`:  `evil-winrm -i 10.10.11.108 -u svc-printer -p '1edFg43012!!'`.
![Shell](Shell.png)
- We capture the user flag.

## Privilege Escalation  
- 


