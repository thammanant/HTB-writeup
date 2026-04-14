# Horizontall Writeup - by Thammanant Thamtaranon

**Horizontall** is an **Easy**-difficulty Linux machine hosted on Hack The Box.

---

## Reconnaissance
- The engagement began with a full TCP port scan to identify open services and determine the underlying operating system.
  ![Nmap_Scan.png](Nmap_Scan.png)
- The results indicated that only **80/tcp** (HTTP) and **22/tcp** (SSH) were open. To ensure proper routing, we added `horizontall.htb` to our `/etc/hosts` file.

---

## Scanning & Enumeration
- We initiated a directory brute-force scan using `dirsearch` against port 80 to map out the application's structure, but the results were largely unhelpful.
- Navigating to `http://horizontall.htb` in the browser revealed a static web page where none of the buttons were interactive.
  ![Main_Page.png](Main_Page.png)
- Digging deeper, we inspected the source code and investigated the JavaScript files loaded by the page. 
  ![Request.png](Request.png)
- Among the JavaScript files, we found hardcoded references to a backend API virtual host: `http://api-prod.horizontall.htb/reviews`.
  ![VHost.png](VHost.png)
- We immediately added `api-prod.horizontall.htb` to our `/etc/hosts` file to access this new endpoint.
- Visiting `/reviews` on the new virtual host returned a JSON response containing user reviews and names, which we noted down for potential username enumeration.
  ![Reviews.png](Reviews.png)
- Running another `dirsearch` scan against the `api-prod` subdomain revealed three interesting paths: `/reviews`, `/admin`, and `/robots.txt`.
- While `/robots.txt` contained nothing useful, navigating to `/admin` presented a Strapi CMS login portal.
  ![Admin_Login1.png](Admin_Login1.png)
- By inspecting the HTTP responses during our interaction with the login page, we identified the exact version of the CMS: **Strapi 3.0.0-beta.17.4**.
  ![Admin_Login2.png](Admin_Login2.png)
- A quick search for vulnerabilities associated with this specific version revealed two critical CVEs that could be chained together for Remote Code Execution (RCE): **CVE-2019-18818** and **CVE-2019-19609**.
  ![CVE1.png](CVE1.png)
  ![CVE2.png](CVE2.png)
  
---

## Exploitation (Initial Access)
- **Understanding the Vulnerabilities:**
  - **CVE-2019-18818:** This is a logic flaw in Strapi's password reset mechanism. The application improperly validates the reset `code` parameter. If an attacker submits an empty JSON object (`{}`) instead of a valid token string, the backend check bypasses the validation, allowing an unauthenticated user to reset the password of any known account.
  - **CVE-2019-19609:** Once authenticated as an administrator, this vulnerability allows for command injection. The Strapi plugin installer endpoint insecurely passes the `plugin` parameter directly to a system shell execution function (`exec()`), leading to RCE.
- To exploit the first CVE, we needed a valid registered email address. We utilized the "Forgot Password" function to enumerate potential users based on the names we found earlier.
- Testing emails like `wail@horizontall.htb`, `doe@horizontall.htb`, and `john@horizontall.htb` returned a "This email does not exist" error.
  ![Invalid_Email1.png](Invalid_Email1.png)
  ![Invalid_Email2.png](Invalid_Email2.png)
- However, when we tested `admin@horizontall.htb`, the server responded differently, confirming it was a valid registered email address.
  ![Valid_Email1.png](Valid_Email1.png)
  ![Valid_Email2.png](Valid_Email2.png)
- With a valid administrator email, we crafted our exploit payload, sending an empty object in the `code` parameter to force a password reset for the admin account.
  ![PoC1.png](PoC1.png)
- The server responded with a success message. Using our newly set credentials, we successfully logged into the Strapi CMS dashboard as an administrator.
  ![PoC2.png](PoC2.png)
  ![PoC3.png](PoC3.png)
- Now authenticated, we moved on to exploiting the second vulnerability (CVE-2019-19609) to achieve RCE. We crafted a malicious payload that injected a reverse shell command into the plugin installation request.
  ![PoC4.png](PoC4.png)
- After starting a Netcat listener on our attacking machine, we fired the payload and caught a reverse shell as the `strapi` user.
  ![Strapi.png](Strapi.png)
- Checking the `/etc/passwd` file, we identified another user on the system named `developer`, who appeared to be our next target.
  ![PASSWD.png](PASSWD.png)
- Further enumeration of the Strapi web directory revealed a `database.json` file containing MySQL credentials for the `developer` user.
  ![MySQL.png](MySQL.png)
- We attempted to reuse this password to SSH into the machine as `developer`, and also tried switching users (`su developer`) from our current shell, but both attempts failed. We also found no usable data within the MySQL database itself.
- To secure a more stable connection, we generated an SSH key pair, placed our public key into the `strapi` user's `authorized_keys` file, and successfully established an SSH connection.
  ![SSH1.png](SSH1.png)
  ![SSH2.png](SSH2.png)
  ![SSH3.png](SSH3.png)
- With our stable SSH shell, we discovered that the `strapi` user actually had read permissions for the `developer`'s home directory. We simply navigated there and captured the `user.txt` flag.

---

## Privilege Escalation
- Having found no immediate path to root via standard enumeration, we checked the local network connections to see if any internal services were running.
  ![Internal_Services1.png](Internal_Services1.png)
- We spotted a service listening on `127.0.0.1:8000`. Utilizing our SSH access, we set up a local port forward to tunnel port 8000 back to our attacking machine.
  ![Internal_Services2.png](Internal_Services2.png)
- Visiting `http://localhost:8000` in our browser revealed a hidden Laravel web application. The page conveniently leaked the framework version: **Laravel v8 (PHP v7.4.18)**.
  ![Internal_Services3.png](Internal_Services3.png)
- Researching this version led us to **CVE-2021-3129**, a severe vulnerability in Laravel's Ignition debug page. 
  ![CVE3.png](CVE3.png)
- **Understanding the Privilege Escalation:**
  CVE-2021-3129 allows unauthenticated attackers to execute arbitrary code. The flaw exists because the Ignition page insecurely handles the `solution` execution endpoint. When combined with PHP's `phar://` wrapper and log poisoning, we can force the server to deserialize malicious data.
- To verify the vulnerability, we first generated a test `.phar` payload designed to execute the `id` command.
  ![PoC5.png](PoC5.png)
- **Exploitation Steps:**
  1. **Generate the Payload:** We used `phpggc` (PHP Generic Gadget Chains) to generate a malicious `.phar` archive. Specifically, we used the `monolog/rce1` gadget chain to pack our reverse shell command into the archive's metadata. 
  2. **Deliver and Execute:** Next, we ran an exploit script against the forwarded local port. The script works in two stages: first, it poisons the Laravel application's log file by injecting our generated `.phar` payload into it. Then, it abuses the Ignition vulnerability to read that log file via the `phar://` wrapper. This forces the underlying PHP engine to deserialize the log file, triggering the Monolog gadget chain's destructor, which seamlessly executes our embedded bash reverse shell.
  ![PoC6.png](PoC6.png)
  3. **Capture the Flag:** Our listener caught the incoming connection, granting us a shell as `root`. We then navigated to the root directory and captured the final `root.txt` flag.
  ![Root.png](Root.png)
