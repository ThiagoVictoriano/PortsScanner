import socket
import threading
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore, Style
import math
import curses

init(autoreset=True)

WELL_KNOWN_PORTS = {
    20: "FTP Data", 21: "FTP Control", 22: "SSH", 23: "Telnet",
    25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP",
    443: "HTTPS", 3389: "RDP"
}

open_ports = []
filtered_ports = []
closed_ports = []
os_guesses = []
port_details = []

print_lock = threading.Lock()

def get_banner(host, port, family):
    try:
        with socket.socket(family, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((host, port))
            s.send(b'HEAD / HTTP/1.0\r\n\r\n')
            banner = s.recv(1024).decode('utf-8', errors='ignore')
            return banner.strip()
    except:
        return None

def guess_os_from_banner(banner):
    banner = banner.lower()
    if "ubuntu" in banner or "debian" in banner:
        return "Linux (Ubuntu/Debian)"
    elif "centos" in banner or "red hat" in banner:
        return "Linux (CentOS/Red Hat)"
    elif "windows" in banner:
        return "Windows"
    elif "freebsd" in banner:
        return "FreeBSD"
    elif "macos" in banner or "darwin" in banner:
        return "MacOS"
    return None

def scan_tcp_range(args):
    host, start_port, end_port, family = args
    for port in range(start_port, end_port + 1):
        try:
            with socket.socket(family, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                result = s.connect_ex((host, port))

                if result == 0:
                    banner = get_banner(host, port, family)
                    service = WELL_KNOWN_PORTS.get(port, "Desconhecido")
                    os_guess = guess_os_from_banner(banner) if banner else None

                    if os_guess:
                        os_guesses.append(os_guess)

                    with print_lock:
                        print(f"{Fore.GREEN}Porta {port:<6} ABERTA  - {service} | Banner: {banner[:50] if banner else 'Sem banner'}{Style.RESET_ALL}")
                    open_ports.append(port)
                    port_details.append((port, service, banner[:50] if banner else "Sem banner"))
                elif result == 111:
                    with print_lock:
                        print(f"{Fore.RED}Porta {port:<6} FECHADA - {WELL_KNOWN_PORTS.get(port, 'Desconhecido')}{Style.RESET_ALL}")
                    closed_ports.append(port)
                else:
                    with print_lock:
                        print(f"{Fore.YELLOW}Porta {port:<6} FILTRADA - {WELL_KNOWN_PORTS.get(port, 'Desconhecido')}{Style.RESET_ALL}")
                    filtered_ports.append(port)
        except Exception as e:
            with print_lock:
                print(f"{Fore.MAGENTA}Erro ao escanear a porta {port}: {str(e)}{Style.RESET_ALL}")

def display_results():
    print("\n" + "-" * 50)
    print(f"{Fore.CYAN}Resumo do Escaneamento:{Style.RESET_ALL}")
    if open_ports:
        print(f"{Fore.GREEN}Portas Abertas:{Style.RESET_ALL}")
        for port, service, banner in port_details:
            print(f"  {Fore.GREEN}Porta {port:<6} - {service} | Banner: {banner}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Nenhuma porta aberta encontrada.{Style.RESET_ALL}")

    if filtered_ports:
        print(f"{Fore.YELLOW}Portas Filtradas: {', '.join(map(str, filtered_ports))}{Style.RESET_ALL}")

    if os_guesses:
        os_detected = max(set(os_guesses), key=os_guesses.count)
    else:
        os_detected = "Desconhecido"

    print(f"\n{Fore.BLUE}Sistema Operacional Estimado: {os_detected}{Style.RESET_ALL}")
    print("-" * 50)

def menu_selector(stdscr):
    curses.curs_set(0)  # Esconde o cursor
    stdscr.clear()
    options = ["IPv4", "IPv6"]
    selected_idx = 0

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Selecione o tipo de IP para escanear:\n", curses.A_BOLD)

        for i, option in enumerate(options):
            if i == selected_idx:
                stdscr.addstr(i + 1, 0, f"> {option}", curses.A_REVERSE)  # Opção destacada
            else:
                stdscr.addstr(i + 1, 0, f"  {option}")

        key = stdscr.getch()

        if key == curses.KEY_UP and selected_idx > 0:
            selected_idx -= 1
        elif key == curses.KEY_DOWN and selected_idx < len(options) - 1:
            selected_idx += 1
        elif key == 10:  # Tecla ENTER
            return selected_idx  # Retorna 0 para IPv4, 1 para IPv6

def get_ip_version():
    return curses.wrapper(menu_selector)  # Chama o menu interativo

def scan():
    # Seleção de IPv4 ou IPv6
    ip_choice = get_ip_version()
    family = socket.AF_INET if ip_choice == 0 else socket.AF_INET6

    host = input(f"{Fore.CYAN}Digite o Host/IP: {Style.RESET_ALL}").strip()
    try:
        start_port = int(input(f"{Fore.CYAN}Digite a Porta Inicial (padrão 1): {Style.RESET_ALL}") or 1)
        end_port = int(input(f"{Fore.CYAN}Digite a Porta Final (padrão 65535): {Style.RESET_ALL}") or 65535)
    except ValueError:
        print(f"{Fore.RED}Erro: Insira números válidos para as portas.{Style.RESET_ALL}")
        return

    print(f"\n{Fore.CYAN}Escaneando {host} nas portas {start_port}-{end_port} em paralelo...\n{'-'*50}{Style.RESET_ALL}")

    MAX_THREADS = 50
    total_ports = end_port - start_port + 1
    chunk_size = math.ceil(total_ports / MAX_THREADS)

    port_ranges = [
        (host, start_port + i * chunk_size, min(start_port + (i + 1) * chunk_size - 1, end_port), family)
        for i in range(MAX_THREADS)
        if start_port + i * chunk_size <= end_port
    ]

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(scan_tcp_range, port_ranges)

    display_results()

if __name__ == "__main__":
    scan()
