# Usage Writeup - by Thammanant Thamtaranon

**Usage** is an **Easy**-difficulty Linux machine hosted on Hack The Box.

---

## Reconnaissance
- I began with a full TCP port scan to identify open services and the operating system.
  ![Nmap_Scan](Nmap_Scan.png)
- The scan revealed an HTTP service. I added `usage.htb` to my `/etc/hosts` file.
- Using **Burp Suite** to inspect the traffic and enumerate subdomains, I discovered `admin.usage.htb`. I added this to my `/etc/hosts` file as well.
  ![VHost](VHost.png)

---

## Scanning & Enumeration
- I attempted to test for SQL injection on several requests before identifying a vulnerability in the "Forgot Password" feature.
- Specifically, I discovered a **SQL Injection** vulnerability in the `email` parameter of the POST request.
- I exploited this vulnerability to query the database and successfully extracted the administrator's password hash.
  ![SQLi1](SQLi1.png)
  ![SQLi2](SQLi2.png)
  ![SQLi3](SQLi3.png)
  ![SQLi4](SQLi4.png)
  ![SQLi5](SQLi5.png)
- I saved the hash and used **Hashcat** to crack it.
  ![Cracked](Cracked.png)
- Using the cracked credentials, I successfully logged into the Admin Dashboard.
  ![Admin_Dashboard](Admin_Dashboard.png)

---

## Exploitation
- Inside the dashboard, I identified the software version as **encore/laravel-admin 1.8.18**. Research confirmed this version is vulnerable to **CVE-2023-24249** (Arbitrary File Upload).
  ![CVE](CVE.png)
- I exploited this vulnerability by attempting to upload a PHP web shell via the administrator's profile avatar.
- I intercepted the upload request and modified the file to include my web shell payload.
  ![File_Upload](File_Upload.png)
- The upload was successful. I opened the image path in a new tab and appended `?cmd=id` to the URL. The output confirmed code execution as the user **dash**.
  ![Web_Shell](Web_Shell.png)
- I then injected a reverse shell command into the `cmd` parameter and established a connection back to my listener.
  ![Dash](Dash.png)
- We captured the **user flag**.
- Navigating to the user Dash's home directory, I found the `.ssh` directory containing a private key (`id_rsa`).
  ![ID_RSA](ID_RSA.png)
- I copied the key to my local machine and used it to SSH into the target for a stable session.
  ![SSH](SSH.png)

---

## Lateral Movement
- While exploring Dash's home directory, I found a hidden file named `.monitrc` which contained a plaintext password.
  ![Password](Password.png)
- I checked `/etc/passwd` and discovered another user on the system named **xander**.
  ![PASSWD](PASSWD.png)
- I attempted to SSH into the machine as **xander** using the password found in `.monitrc`, which was successful.
  ![Xander](Xander.png)

---

## Privilege Escalation
- I ran `sudo -l` to check Xander's privileges. The output showed that Xander can run `/usr/bin/usage_management` as **root**.
  ![SUDO](SUDO.png)
- I ran the tool to observe its behavior.
  ![Usage_management](Usage_management.png)
- Since the binary is compiled, I used `strings` to analyze the underlying commands it executes.
  ![Usage_management_code](Usage_management_code.png)
- The analysis revealed that the tool executes the following command:
  `/usr/bin/7za a /var/backups/project.zip -tzip -snl -mmt -- *`
- **Vulnerability Explanation:**
  - The command uses the wildcard `*` to include all files in the current directory.
  - The `7za` tool supports a special syntax where arguments starting with `@` are treated as "listfiles" (files containing a list of filenames to process).
  - By creating a file named `@filelist` in the current directory, the wildcard expansion passes `@filelist` to `7za`.
  - `7za` then reads the content of `filelist` and tries to archive the files listed inside it.
- **Exploitation:**
  - I created an empty file named `@filelist` to trigger the injection via the wildcard.
  - I created a symlink named `filelist` pointing to the root SSH private key (`ln -s /root/.ssh/id_rsa filelist`).
  - When I ran the sudo command, `7za` processed `@filelist`, followed the symlink to `/root/.ssh/id_rsa`, and attempted to parse the private key as a list of filenames.
  - Since the key content is not a valid list of files, `7za` generated error messages displaying the lines it couldn't parse—effectively leaking the Root private key in the error output.
  ![Root_ID_RSA](Root_ID_RSA.png)
- I copied the leaked private key to my local machine and used it to SSH into the server as **root**.
- We captured the **root flag**.
  ![Root](Root.png)
