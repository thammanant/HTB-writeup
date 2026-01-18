# Manager Writeup - by Thammanant Thamtaranon

**Manager** is a **Medium**-difficulty Windows machine hosted on Hack The Box.

---

## Reconnaissance
- I began with a full TCP port scan to identify open services and the operating system.
  ![Nmap_Scan1](Nmap_Scan1.png)
  ![Nmap_Scan2](Nmap_Scan2.png)
- The scan revealed the standard suite of ports for a **Domain Controller**, plus **Microsoft SQL Server (1433)**:
  - **53** — DNS (Simple DNS Plus)
  - **80** — HTTP (Microsoft IIS 10.0)
  - **88** — Kerberos
  - **135/139/445** — RPC/SMB
  - **389/636/3268** — LDAP/LDAPS (Domain: manager.htb)
  - **1433** — MSSQL (SQL Server 2019)
  - **5985** — WinRM
- I added **dc01.manager.htb** and **manager.htb** to my `/etc/hosts` file.

---

## Scanning & Enumeration
- Lacking initial credentials, I used `impacket-lookupsid` (RID Cycling) to enumerate valid usernames from the Domain Controller.
  ![Names](Names.png)
- With the user list in hand, I performed a brute-force attack (password spray) using the usernames as the passwords. This revealed that the user **operator** had the password `operator`.
  ![Operator_Credential](Operator_Credential.png)
- I verified these credentials against SMB, LDAP, and MSSQL using `NetExec` (nxc).
  ![NXC_SMB_Operator](NXC_SMB_Operator.png)
  ![NXC_LDAP_Operator](NXC_LDAP_Operator.png)
  ![NXC_MSSQL_Operator](NXC_MSSQL_Operator.png)
- I used the `operator` account to run **BloodHound** to map the domain trust relationships.
  ![Bloodhound](Bloodhound.png)
- Unfortunately, the BloodHound analysis showed that **operator** had no significant outbound control or group memberships.
  ![Bloodhound_Operator](Bloodhound_Operator.png)
- I turned my attention to the **MSSQL** service. Using `impacket-mssqlclient`, I successfully connected to the database as `operator`.
- I attempted to enable `xp_cmdshell` for remote code execution, but the account lacked the necessary permissions.
  ![MSSQL1](MSSQL1.png)
- I then explored the file system using the `xp_dirtree` command. I specifically enumerated the `C:\inetpub\wwwroot` directory to look for web assets.
  ![MSSQL2](MSSQL2.png)
- Inside `C:\inetpub\wwwroot`, I discovered a website backup file.
  ![MSSQL3](MSSQL3.png)
- I downloaded the backup file to my local machine using `wget`.
  ![Backup](Backup.png)
- Analyzing the backup, specifically within `.old-conf.xml`, I found hardcoded credentials for the user **raven**.
  ![Raven_Credential](Raven_Credential.png)

---

## Exploitation
- I verified Raven's credentials using `NetExec` against SMB and WinRM.
  ![NXC_SMB_Raven](NXC_SMB_Raven.png)
  ![NXC_WinRM_Raven](NXC_WinRM_Raven.png)
- I then connected to the machine using **Evil-WinRM** as `raven` and successfully captured the **user flag**.
  ![Raven](Raven.png)
- I re-ran BloodHound for the user `raven`, but like `operator`, this account had no direct outbound control paths.
  ![Bloodhound_Raven](Bloodhound_Raven.png)

---

## Privilege Escalation
- I ran `certipy-ad` to enumerate Active Directory Certificate Services (AD CS) vulnerabilities and identified that the domain is vulnerable to **ESC7**.
  ![Certipy1](Certipy1.png)
  ![Certipy2](Certipy2.png)
- **Vulnerability Explanation (ESC7):**
  - **ESC7** occurs when a user has the **ManageCA** (also known as "Config CA") or **ManageCertificates** ("Officer") permission on the Certificate Authority (CA).
  - These permissions allow an attacker to modify CA settings (such as enabling disabled templates) or approve pending certificate requests, effectively bypassing security controls to issue malicious certificates.
- I proceeded to exploit this vulnerability to elevate privileges to Administrator:

**Step 1: Enable the Vulnerable Template**
- Since `raven` has the `ManageCA` right, I used this permission to enable the **SubCA** certificate template. This template is vulnerable because it allows users to request certificates, although they typically require manual approval by a CA Manager.

**Step 2: Grant "Manage Certificates" Rights**
- To approve the request we are about to make, we need "Officer" rights. Using `raven`'s `ManageCA` permission, I added `raven` as an **Officer** to the CA, granting the `ManageCertificates` right.
  ![ESC7_1](ESC7_1.png)

**Step 3: Request the Malicious Certificate**
- I requested a certificate using the **SubCA** template on behalf of the **Administrator** (UPN: `administrator@manager.htb`).
- As expected, the request was placed in a **"Pending"** state. The output provided the Request ID: **28**.

**Step 4: Approve the Request**
- Now acting as a CA Officer, I used `raven`'s credentials to issue (approve) the pending request ID **28**.

**Step 5: Retrieve the Certificate**
- With the request approved, I retrieved the issued certificate for the Administrator.
  ![ESC7_2](ESC7_2.png)
- The certificate was saved locally as `administrator.pfx`.
- I used the obtained PFX certificate to authenticate to the Domain Controller via PKINIT. This allowed me to retrieve the **Administrator's NTLM hash**.
- Finally, I used **Evil-WinRM** with the Administrator's hash to log in to the machine.
  ![Admin](Admin.png)
- We captured the **root flag**.
