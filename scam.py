import socket
from colorama import init, Fore, Style

# Dicionário de portas bem conhecidas
WELL_KNOWN_PORTS = {
    20: "FTP Data",
    21: "FTP Control",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3389: "RDP"
}

open_ports = []
filtered_ports = []

# Identificação de sistema operacional simples a partir do banner
def identify_os(banner):
    """Tenta identificar o sistema operacional a partir do banner."""
    if banner:
        banner = banner.lower()
        if 'linux' in banner:
            return "Linux"
        elif 'windows' in banner:
            return "Windows"
        elif 'bsd' in banner:
            return "BSD"
        elif 'mac' in banner:
            return "Mac OS"
        elif 'android' in banner:
            return "Android"
        else:
            return "Sistema Operacional Desconhecido"
    return "Sistema Operacional Desconhecido"

def get_banner(host, port):
    """Tenta obter o banner de um serviço na porta especificada."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((host, port))
            s.send(b'HEAD / HTTP/1.0\r\n\r\n')  # Envia uma requisição HTTP simples para tentar pegar o banner
            banner = s.recv(1024).decode('utf-8', errors='ignore')
            return banner.strip()
    except:
        return None

def scan_port(host, port):
    """Tenta conectar ao host e verificar o estado da porta."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            
            if result == 0:  # Porta aberta
                open_ports.append(port)
                banner = get_banner(host, port)
                if banner:
                    os_identification = identify_os(banner)
                    return f"{Fore.GREEN}Porta {port} ABERTA - {WELL_KNOWN_PORTS.get(port, 'Desconhecido')} | Banner: {banner[:50]}... | OS: {os_identification}{Style.RESET_ALL}"
                else:
                    return f"{Fore.GREEN}Porta {port} ABERTA - {WELL_KNOWN_PORTS.get(port, 'Desconhecido')} | Sem banner identificado{Style.RESET_ALL}"
            elif result == 111:  # Porta fechada
                return f"{Fore.RED}Porta {port} FECHADA - {WELL_KNOWN_PORTS.get(port, 'Desconhecido')}{Style.RESET_ALL}"
            else:  # Porta filtrada (timeout ou RST)
                filtered_ports.append(port)
                return f"{Fore.YELLOW}Porta {port} FILTRADA (TIMEOUT ou RST) - {WELL_KNOWN_PORTS.get(port, 'Desconhecido')}{Style.RESET_ALL}"
    except Exception as e:
        return f"{Fore.MAGENTA}Erro ao escanear a porta {port}: {str(e)}{Style.RESET_ALL}"

def display_results():
    """Exibe os resultados de portas abertas e filtradas."""
    print(f"\n{Fore.CYAN}Portas abertas:{Style.RESET_ALL}")
    for port in open_ports:
        print(f"{Fore.GREEN}Porta {port} - {WELL_KNOWN_PORTS.get(port, 'Desconhecido')}{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}Portas filtradas:{Style.RESET_ALL}")
    if filtered_ports:
        for port in filtered_ports:
            print(f"{Fore.YELLOW}Porta {port} - {WELL_KNOWN_PORTS.get(port, 'Desconhecido')}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Nenhuma porta filtrada encontrada.{Style.RESET_ALL}")

def scan():
    """Executa o escaneamento de portas de acordo com os inputs do usuário."""
    host = input(f"{Fore.CYAN}Digite o Host/IP: {Style.RESET_ALL}")
    
    try:
        start_port = int(input(f"{Fore.CYAN}Digite a Porta Inicial (padrão 1): {Style.RESET_ALL}") or 1)
        end_port = int(input(f"{Fore.CYAN}Digite a Porta Final (padrão 65535): {Style.RESET_ALL}") or 65535)
    except ValueError:
        print(f"{Fore.RED}Erro: Insira números válidos para as portas.{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.CYAN}Escaneando {host} nas portas {start_port}-{end_port}\n{'-'*50}{Style.RESET_ALL}")
    
    # Inicia o escaneamento de portas
    for port in range(start_port, end_port + 1):
        result = scan_port(host, port)
        if result:
            print(result)

    # Exibe os resultados
    display_results()

if __name__ == "__main__":
    init(autoreset=True)  # Inicializa o colorama
    scan()
