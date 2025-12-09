# TombWatcher Writeup - by Thammanant Thamtaranon

**TombWatcher** is an medium-difficulty Windows machine hosted on Hack The Box.

## Reconnaissance
- I began with a full TCP port scan, including service/version detection and OS fingerprinting:
  `nmap -A -T4 -p- 10.10.11.72`
  ![Nmap_Scan1](Nmap_Scan1.png)
  ![Nmap_Scan2](Nmap_Scan2.png)
- The scan revealed the following open ports:
  - **53** — DNS (Simple DNS Plus)
  - **80** — HTTP (Microsoft IIS httpd 10.0)
  - **88** — Kerberos (Microsoft Windows Kerberos)
  - **135** — MSRPC (Microsoft Windows RPC)
  - **139** — NetBIOS-SSN
  - **389** — LDAP (Microsoft Windows Active Directory LDAP)
  - **445** — Microsoft-DS (SMB)
  - **464** — kpasswd
  - **593** — RPC over HTTP (Microsoft Windows RPC over HTTP 1.0)
  - **636** — LDAPS (SSL/LDAP)
  - **3268** — Global Catalog LDAP
  - **3269** — Global Catalog LDAPS
  - **5985** — WinRM (Microsoft HTTPAPI httpd 2.0)
  - **9389** — AD Web Services (.NET Message Framing)
  - **49666 - 49720** — RPC High Ports (Microsoft Windows RPC)
- I added `tombwatcher.htb` and `dc01.tombwatcher.htb` to `/etc/hosts` for proper hostname resolution.

## Scanning & Enumeration
- We ran `dirsearch` on both `tombwatcher.htb` and `dc01.tombwatcher.htb`, but nothing of interesting was founded.
- I then use `nxc` with the given username and password on smb. However, after enumerated nothing of use was founded.
  ![NXC_SMB](NXC_SMB.png)
- We then use `rpcclient` to find more information.
  ![MSRPC](MSRPC.png)
- We found user `Alfred`, `sam`, and `john`.
- We then use `bloodhound-python` to map the relationships.
  ![BloodHound](BloodHound.png)
- We founded that user `henry` have writeSPN on user `alfred`. This allows us to perform `Targeted Kerberoasting`.
  ![Outbound](Outbound.png)
- Normally, you can only Kerberoast users who already have a "Service Principal Name" (SPN). Alfred doesn't have one, so we can't roast him yet.
- Since Henry has WriteSPN, we can force an SPN onto Alfred's account (e.g., assign him a fake service like HTTP/test).
- Resulting in `Alfred becomes a "Service Account." Now we request a TGS ticket for him, which will be encrypted with his password. Then we can crack that ticket to get his cleartext password.
- First, inject a fake SPN into Alfred's account.
- 

## Exploitation


## Privilege Escalation
