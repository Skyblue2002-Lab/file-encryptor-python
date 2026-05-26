# CyberSec Encryption Tool 🔐

## Description
A full GUI desktop security application built with Python that allows 
users to encrypt and decrypt both text messages and files using 
AES military-grade encryption. Built as a cybersecurity project at 
the Federal University of Lafia.

## Features
- 🔑 Password protected login system with SHA256 hashing
- 💬 Encrypt and decrypt text messages using AES-EAX encryption
- 📁 Encrypt and decrypt any file type (Word, PDF, images etc)
- 📝 Activity logging for all encryption and decryption actions
- 🛡️ Tamper detection — alerts if encrypted data has been modified
- 📋 Copy encrypted messages to clipboard for safe sharing

## How to Run
1. Install Python 3.x from https://python.org
2. Install the required library:
   pip install pycryptodome
3. Run the application:
   python project.py
4. Set a password when prompted on first launch

## How to Test
1. Click "Encrypt Message" — type any message and copy the result
2. Click "Decrypt Message" — paste the encrypted text to restore it
3. Click "Encrypt File" — select any file to encrypt it as .enc
4. Click "Decrypt File" — select the .enc file to restore original

## Technologies Used
- Python 3
- AES-EAX Encryption (PyCryptodome)
- SHA256 Password Hashing
- Tkinter GUI

## Developer
Ihekaji Joshua  
Cybersecurity Student — Federal University of Lafia  
SIWES Trainee — Lafia E-Library
