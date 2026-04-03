# Release Notes

## English
Version v1.1.2 includes:
- Startup dependency bootstrap for required tools
- Automatic check for OpenSSH Client (ssh-keygen, ssh-add) on app launch
- Prompted background installation of OpenSSH Client from the app when missing
- Installer check for OpenSSH Client with optional automatic install during setup
- Optional auto-install prompt for missing `paramiko` when running from Python source

Files (SHA256):
- SSHKeyForge.exe - SHA256: AB1E00BE5ED0BFD3C13CB463C9C82C825397D6EB83330931A5BE8DA2C2B27199 (53.11 MB)
- SSHKeyForge-Setup.exe - SHA256: 5FA452313DEF908E2EB26C97B1CC731CC130FA15BE0E17FF9E7BD2B5AC867F36 (52.93 MB)
- SSHKeyForge_v1.1.2_win64.zip - SHA256: 22A8C59F4538B394A0646CFE27203FA53A2158BE7138FC8CA74E1FB8D0ACC8CC (52.78 MB)

Version v1.1.1 includes:
- Instruction content expanded and clarified
- More descriptive, intuitive button labels
- Added upload of selected local .pub key to remote device
- Remote key replacement now uses the selected .pub below
- White titlebar icons (min/max/restore) with proper minimize line
- Instruction dialog height tuned (no scrollbar, less empty space)
- Removed redundant local-key upload button

Files (SHA256):
- SSHKeyForge.exe - SHA256: 8E1E63BF7C24351E79F70944CCE3C96D11CA1BA5802548325FBDD5A4B4DBA221 (53.1 MB)
- SSHKeyForge-Setup.exe - SHA256: 0FB5CB88F49A3256B13D254C588EECF017267C94F79A94AD156670C9C8D18623 (52.92 MB)
- SSHKeyForge_v1.1.1_win64.zip - SHA256: 24CC38CAE693434C2FBDB407F217DF1DFB815A1213C5B0F46688D4EC986C1299 (52.78 MB)

Version v1.0.1 includes:
- New ssh-agent key management section (list, remove selected, clear agent)
- Agent keys label warning about duplicates causing connection issues
- Fixed maximize/restore icon rendering in the title bar
- Polish instructions line break for the Auto-yes tip

Version v1.0.0 includes:
- Embedded terminal for ssh-keygen / ssh-add prompts and confirmations
- Auto-add generated keys to Windows ssh-agent
- Remote authorized_keys management (detect, remove, replace)
- English + Polish UI
- Updated README with screenshots

## Polski
Wersja v1.1.2 zawiera:
- Startowy mechanizm sprawdzania wymaganych zaleznosci
- Automatyczne sprawdzanie OpenSSH Client (ssh-keygen, ssh-add) przy uruchomieniu aplikacji
- Propozycje instalacji OpenSSH Client z poziomu aplikacji (w tle, z uprawnieniami admina)
- Sprawdzanie OpenSSH Client w instalatorze i opcjonalna automatyczna instalacja podczas setupu
- Opcjonalna propozycja instalacji brakujacego `paramiko` przy uruchamianiu ze zrodla Python

Pliki (SHA256):
- SSHKeyForge.exe - SHA256: AB1E00BE5ED0BFD3C13CB463C9C82C825397D6EB83330931A5BE8DA2C2B27199 (53.11 MB)
- SSHKeyForge-Setup.exe - SHA256: 5FA452313DEF908E2EB26C97B1CC731CC130FA15BE0E17FF9E7BD2B5AC867F36 (52.93 MB)
- SSHKeyForge_v1.1.2_win64.zip - SHA256: 22A8C59F4538B394A0646CFE27203FA53A2158BE7138FC8CA74E1FB8D0ACC8CC (52.78 MB)

Wersja v1.1.1 zawiera:
- Uzupelniona i doprecyzowana instrukcja
- Bardziej opisowe i intuicyjne etykiety przyciskow
- Dodana mozliwosc wgrania wybranego lokalnego klucza .pub na urzadzenie zdalne
- Zamiana kluczy zdalnych korzysta z wybranego nizej pliku .pub
- Biale ikony min/max/przywracania w pasku tytulu (minimalizacja jako linia)
- Okno instrukcji dopasowane: bez scrolla i bez nadmiaru pustego miejsca
- Usuniety zbedny przycisk wgrywania lokalnego klucza

Pliki (SHA256):
- SSHKeyForge.exe - SHA256: 8E1E63BF7C24351E79F70944CCE3C96D11CA1BA5802548325FBDD5A4B4DBA221 (53.1 MB)
- SSHKeyForge-Setup.exe - SHA256: 0FB5CB88F49A3256B13D254C588EECF017267C94F79A94AD156670C9C8D18623 (52.92 MB)
- SSHKeyForge_v1.1.1_win64.zip - SHA256: 24CC38CAE693434C2FBDB407F217DF1DFB815A1213C5B0F46688D4EC986C1299 (52.78 MB)

Wersja v1.0.1 zawiera:
- Nowa sekcja zarzadzania kluczami w ssh-agent (lista, usun zaznaczone, wyczysc agenta)
- Ostrzezenie przy kluczach agenta o duplikatach powodujacych problemy z polaczeniem
- Naprawiona ikona powiekszania/przywracania w pasku tytulu
- Nowa linia w instrukcji PL dla wskazowki o Auto-yes

Wersja v1.0.0 zawiera:
- Wbudowany terminal do pytan ssh-keygen / ssh-add i potwierdzen
- Auto-dodanie wygenerowanych kluczy do Windows ssh-agent
- Zarzadzanie authorized_keys na zdalnym hoscie (wykrywanie, usuwanie, zamiana)
- Interfejs po angielsku i po polsku
- Zaktualizowany README ze screenami




