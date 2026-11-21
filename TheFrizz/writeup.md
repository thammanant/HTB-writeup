# TheFrizz Writeup - by Thammanant Thamtaranon

**TheFrizz** is a **Medium**-difficulty Windows machine hosted on Hack The Box.

---

## Reconnaissance
- We began the engagement with a full TCP port scan using Nmap to identify open services and fingerprint the underlying operating system.
  ![Nmap_Scan.png](Nmap_Scan.png)
- The notable open ports on the Domain Controller were:
  - **22/tcp:** SSH (OpenSSH for Windows 9.5)
  - **53/tcp:** DNS (Simple DNS Plus)
  - **80/tcp:** HTTP (Apache httpd 2.4.58)
  - **88/tcp:** Kerberos (Microsoft Windows Kerberos)
  - **135/tcp, 139/tcp, 445/tcp:** SMB / RPC
  - **389/tcp, 636/tcp, 3268/tcp, 3269/tcp:** LDAP / LDAPS
- We then added the `frizz.htb` and `frizzdc.frizz.htb` domain names to our `/etc/hosts` file.

---

## Scanning & Enumeration
- We started by visiting `http://frizzdc.frizz.htb/`. Nothing of immediate interest was found apart from a **Staff Login** button.
  ![Port80.png](Port80.png)
- Clicking the **Staff Login** button redirected us to `/Gibbon-LMS/`, where the bottom left of the page displayed the application version: **Gibbon v25.0.00**.
  ![Staff_Login.png](Staff_Login.png)
- Searching for CVEs related to this version of Gibbon led to **CVE-2023-45878**.
  - **CVE-2023-45878** is an unauthenticated Arbitrary File Write vulnerability in Gibbon Edu version 25.0.1 and prior. The `rubrics_visualise_saveAjax.php` endpoint accepts the `img`, `path`, and `gibbonPersonID` parameters without requiring authentication. Because the `img` parameter is base64 decoded and written directly to the user-controlled file path relative to the installation directory, an attacker can write a malicious PHP file to achieve Remote Code Execution (RCE).
  ![CVE.png](CVE.png)

---

## Exploitation
- We used a public PoC exploit available on [GitHub](https://github.com/ulricvbs/gibbonlms-filewrite_rce).
  ![PoC1.png](PoC1.png)
- Executing the PoC with the `whoami` command confirmed arbitrary command execution as the service account `frizz\w.webservice`.
  ![PoC2.png](PoC2.png)
- Updating the payload to trigger a reverse shell provided an interactive connection back to our listener.
  ![PoC3.png](PoC3.png)
- Enumerating the application further revealed database credentials in the configuration file `config.php`.
  ![DB_Credential.png](DB_Credential.png)
- We used `mysql.exe` on the target machine to query the database using the discovered credentials. User details and credentials in Gibbon are stored in the `gibbonPerson` table.
  ![DB.png](DB.png)
- We retrieved the hash and salt for user `f.frizzle`:
  - **Hash:** `067f746faca44f170c6cd9d7c4bdac6bc342c608687733f80ff784242b0b0c03`
  - **Salt:** `/aACFhikmNopqrRTVz2489`
  ![Hash1.png](Hash1.png)
- Running Hashcat in auto-detection mode listed matching hash structures, but did not specify the exact order of the salt and password.
  ![Hash2.png](Hash2.png)
- By reviewing the open-source Gibbon repository on GitHub, we confirmed that the application calculates passwords using `hash('sha256', $salt . $password)` (corresponding to Hashcat mode `1420`: `sha256($salt.$pass)`).
  ![Hash3.png](Hash3.png)
- Using Hashcat mode `1420` formatted as `hash:salt`, we successfully cracked the password for user `f.frizzle`.
  ![Cracked.png](Cracked.png)
- When verifying these credentials against SMB, authentication failed with a `STATUS_NOT_SUPPORTED` error because NTLM authentication is disabled on the Domain Controller. As a result, Kerberos authentication is required.
  ![SMB.png](SMB.png)
- To enable Kerberos authentication from our Linux attack box, NetExec was used with the `-k --generate-krb5-file krb5.conf` flags to generate a matching Kerberos configuration file defining the realm `FRIZZ.HTB` and KDC `frizzdc.frizz.htb`. We copied this file to `/etc/krb5.conf` and synchronized our system clock with the target domain controller to avoid clock skew errors (`KRB_AP_ERR_SKEW`).
  ![Config.png](Config.png)
- We then executed `kinit f.frizzle` to generate a Ticket Granting Ticket (TGT) for `f.frizzle@FRIZZ.HTB` and verified the active ticket in cache using `klist`.
  ![TGT.png](TGT.png)
- With a valid TGT in our credential cache, we connected to the Domain Controller via SSH using Kerberos domain authentication and captured the user flag.
  ![SSH1.png](SSH1.png)
  ![SSH2.png](SSH2.png)

---

## Privilege Escalation
- Inspecting the machine revealed a deleted 7z archive file inside the Recycle Bin.
  ![Recycle_Bin.png](Recycle_Bin.png)
- We transferred the archive to our local attack box via `scp` and extracted its contents.
  ![Extract.png](Extract.png)
- Within the extracted WAPT deployment files (`wapt/conf/waptserver.ini`), we located a Base64-encoded string assigned to `wapt_password`: `IXN1QmNpZ0BMeHTedWQuHo=`. Decoding this string revealed the cleartext password.
  ![Password.png](Password.png)
- Because the configuration file did not specify which domain user account this password belonged to, we used `f.frizzle` to enumerate domain users on the target.
  ![Users.png](Users.png)
- We then spray-tested the decoded password against all domain accounts using SMB, which confirmed the password was valid for user `M.SchoolBus`.
  ![M_SchooBus.png](M_SchooBus.png)
- After logging in as `M.SchoolBus`, running `whoami /groups` revealed that the account is a member of `frizz\Group Policy Creator Owners`.
  ![Groups.png](Groups.png)
- Membership in `Group Policy Creator Owners` gives the user permission to create and manage Group Policy Objects (GPOs) in Active Directory. We downloaded **SharpGPOAbuse.exe** to the target's desktop.
  ![SharpGPOAbuse1.png](SharpGPOAbuse1.png)
- We then abused GPO permissions with `SharpGPOAbuse` to create a new GPO task linked to the target machine, setting it to run a command that outputs `whoami` to `success.txt`.
  ![SharpGPOAbuse2.png](SharpGPOAbuse2.png)
- Checking `M.SchoolBus`'s Desktop confirmed `success.txt` was created with the content `NT AUTHORITY\SYSTEM`, confirming code execution with full SYSTEM privileges.
  ![SharpGPOAbuse3.png](SharpGPOAbuse3.png)
- Finally, we updated the GPO task to execute a reverse shell command, receiving a connection back as `NT AUTHORITY\SYSTEM` and capturing the root flag.
  ![NT_AUTHORITY.png](NT_AUTHORITY.png)
