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

## Exploitation
- We use `bloodhound-python` to map the relationships.
  ![BloodHound](BloodHound.png)
- We founded that user `henry` have `writeSPN` on user `alfred`. This allows us to perform `Targeted Kerberoasting`.
  ![Outbound](Outbound.png)
- Normally, you can only Kerberoast users who already have a "Service Principal Name" (SPN). Alfred doesn't have one, so we can't roast him yet.
- Since Henry has WriteSPN, we can force an SPN onto Alfred's account (e.g., assign him a fake service like HTTP/test).
- Resulting in `Alfred becomes a "Service Account." Now we request a TGS ticket for him, which will be encrypted with his password. Then we can crack that ticket to get his cleartext password.
- First, set the clock to match the server clock. Kerberos includes a timestamp in every "ticket" request to prevent hackers from capturing old tickets and reusing them later (Replay Attacks). If your clock and the server's clock differ by more than 5 minutes, the server automatically rejects you with the error `KRB_AP_ERR_SKEW`.
  ![Set_Clock](Set_Clock.png)
- Next, inject a fake SPN into Alfred's account.
  ![WriteSPN](WriteSPN.png)
- Then, we request the service from user Alfred.
  ![Get_UserSPN](Get_UserSPN.png)
- Finally, we crack the hash, which will resulting in getting alred's password.
  ![Alfred_Password](Alfred_Password.png)
- Going back to bloodhound relationships, we founded that user Alfred have `AddSelf` to `INFRASTRUCTURE`. Which means the user has the right to add themselves to a specific group (Infrastructure).
  ![Outbound2](Outbound2.png)
- We then add Alfred to Infrastructure group.
  ![AddSelf](AddSelf.png)
- Now, back to the relationships map. The Infrastructure group have `ReadGMSAPassword` to `ANSIBLE_DEV$`. Group Managed Service Accounts (gMSA) are used by servers to run automated tasks (like Ansible). Because they are automated, their passwords are managed by Windows and are incredibly long and complex. We have permission to read that password.
  ![Outbound3](Outbound3.png)
  ![Hash](Hash.png)
- Now that we got a hash password of `ANSIBLE_DEV$`, we will be using technique called Pass-The-Hash. Pass the Hash (PtH) is a hacking technique that allows you to log into a system using a user's password hash instead of their cleartext password.
- From the relationships map, `ANSIBLE_DEV$` have `ForceChangePassword` to user `sam`. So we can change user Sam's password.
  ![Outbound4](Outbound4.png)
  ![ForceChangePassword](ForceChangePassword.png)
- Since User `Sam` have `WriteOwner` to User `John`. The permission WriteOwner is extremely powerful because the Owner of an object can always change the permissions on that object. Meaning we can use WriteOwner to make Sam the owner of John's account.
  ![Outbound5](Outbound5.png)
  ![WriteOwner](WriteOwner.png)
- Now that Sam is the owner, he grants himself the right to modify John.
  ![GenericAll](GenericAll.png)
- Now that Sam has full control, force the password change.
  ![Set_Password](Set_Password.png)
- We then run `nxc` on winrm and able to login with changed password.
  ![NXC_WinRM](NXC_WinRM.png)
- We then capture the user flag.

## Privilege Escalation
- From the relationships map, user `John` have `GenericAll` on the `ADCS (Active Directory Certificate Services)`. This is a vulnerability known as ESC7, It means John has full control over the Certificate Authority (CA). He can reconfigure it to make himself an "Officer" (manager), which allows him to issue certificates for anyone, including the Administrator.
  ![Outbound6](Outbound6.png)
- First, we upload Certify.exe to the machine using `Evil-WinRm`.
- Second, we 
- 

- 





