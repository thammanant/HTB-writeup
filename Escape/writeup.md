# Escape Writeup - by Thammanant Thamtaranon

**Escape** is a **Medium**-difficulty Windows machine hosted on Hack The Box.

---

## Reconnaissance
- The engagement began with a full TCP port scan to identify open services and determine the operating system.
  ![Nmap_Scan1.png](Nmap_Scan1.png)
  ![Nmap_Scan2.png](Nmap_Scan2.png)
  ![Nmap_Scan3.png](Nmap_Scan3.png)
- The results revealed a standard Windows Domain Controller environment hosting **DNS** (53), **Kerberos** (88), **SMB** (445), and **LDAP** (389/636).
- Most notably, **1433/tcp** (Microsoft SQL Server) and **5985/tcp** (WinRM) were open, providing potential avenues for entry.

---

## Scanning & Enumeration
- I started by performing an initial enumeration of valid domain users to build a target list.
  ![Users.png](Users.png)
- Shifting focus to the SMB service, we checked for shares accessible to unauthenticated or guest users.
  ![NXC_SMB_Guest1.png](NXC_SMB_Guest1.png)
- A **Public** share was discovered, which contained a file named `SQL Server Procedures.pdf`.
  ![NXC_SMB_Guest2.png](NXC_SMB_Guest2.png)
- Analyzing the PDF proved fruitful; it contained documentation that leaked credentials for a user named `PublicUser`.
  ![PDF1.png](PDF1.png)
  ![PDF2.png](PDF2.png)

---

## Exploitation
- We verified the credentials for `PublicUser` against the MSSQL service and confirmed they were valid.
  ![NXC_MSSQL_PublicUser.png](NXC_MSSQL_PublicUser.png)
- Once authenticated to the database, I attempted to enable and run `xp_cmdshell` to execute commands like `whoami`. However, the database denied permission, forcing us to look for alternative methods.
  ![MSSQL1.png](MSSQL1.png)
- Although permissions were limited, the `xp_dirtree` stored procedure was available. We utilized this to trigger an authentication attempt back to our attacking machine via SMB.
  ![MSSQL2.png](MSSQL2.png)
- With **Responder** listening on the network interface, the command was executed. We successfully captured the NTLMv2 hash for the service account `sql_svc`.
  ![MSSQL3.png](MSSQL3.png)
  ![Crack1.png](Crack1.png)
- The captured hash was then passed to `hashcat`, which quickly retrieved the plaintext password.
  ![Crack2.png](Crack2.png)
- With the new credentials for `sql_svc`, I validated access against SMB, WinRM, and LDAP services.
  ![NXC_SMB_Sql_SVC.png](NXC_SMB_Sql_SVC.png)
  ![NXC_WinRM_Sql_SVC.png](NXC_WinRM_Sql_SVC.png)
  ![NXC_LDAP_Sql_SVC.png](NXC_LDAP_Sql_SVC.png)
- The **BloodHound** ingestor was run to map out the Active Directory environment, though nothing immediately useful stood out at this stage.
  ![BloodHound.png](BloodHound.png)
- We proceeded to log in using `Evil-WinRM`, establishing a stable shell as `sql_svc`.
  ![Evil-WinRM_Sql_SVC.png](Evil-WinRM_Sql_SVC.png)
- Manual enumeration of the file system uncovered SQL Server logs containing a plaintext password for another user, `ryan.cooper`. It appeared he had pasted the password as his username.
  ![Logs1.png](Logs1.png)
  ![Logs2.png](Logs2.png)
- These credentials were validated, confirming that `ryan.cooper` also had remote access privileges.
  ![NXC_Ryan.png](NXC_Ryan.png)
- Pivoting to `ryan.cooper` using `Evil-WinRM` granted access to the user flag.
  ![Evil-WinRM_Ryan.png](Evil-WinRM_Ryan.png)

---

## Privilege Escalation
- To identify a path to Domain Admin, we investigated the Active Directory Certificate Services (AD CS). Running `certipy-ad` to enumerate certificate templates revealed a critical misconfiguration in the `UserAuthentication` template: it was vulnerable to **ESC1**.
  ![Certipy.png](Certipy.png)
- **The Vulnerability (ESC1):** The core issue with this template is that it allows low-privileged users (like `ryan.cooper`) to specify a **Subject Alternative Name (SAN)** in the certificate signing request (CSR). Furthermore, the template is configured to allow client authentication. This means we can request a certificate that claims to be *any* user in the domain (e.g., Administrator), and the CA will issue it without validation.
- I exploited this by requesting a certificate for the **Administrator** account, specifying `Administrator@sequel.htb` as the UPN.
- The request was successful, and we received the `administrator.pfx` file.
- With the forged certificate, we authenticated to the Domain Controller. This process successfully retrieved the NTLM hash for the Administrator account.
  ![ESC1.png](ESC1.png)
- Finally, using the Administrator's hash, we logged in via Evil-WinRM and captured the root flag.
  ![Root.png](Root.png)
