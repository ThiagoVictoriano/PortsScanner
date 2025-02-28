# PortsScanner

# Scanner de Portas TCP com Estimativa de SO

Este é um scanner de portas TCP desenvolvido em Python, que permite escanear um intervalo de portas de um host, identificar serviços conhecidos, coletar banners e estimar o sistema operacional do alvo com base nas respostas.

## Funcionalidades

- Escaneamento de portas TCP em paralelo utilizando `ThreadPoolExecutor`
- Identificação de serviços conhecidos para portas bem definidas
- Coleta de banners de serviços
- Estimativa do sistema operacional com base no banner
- Diferenciação entre portas abertas, fechadas e filtradas
- Suporte a IPv6

## Dependências

Para executar este script, instale as seguintes bibliotecas:

```bash
pip install colorama
```

## Como Usar

Execute o script e insira as informações solicitadas:

```bash
python scanner.py
```

O script solicitará:
- O endereço IP ou hostname do alvo
- A porta inicial e final para escaneamento (padrão 1-65535 se não especificado)

### Exemplo de Uso

```plaintext
Digite o Host/IP: 192.168.1.1
Digite a Porta Inicial (padrão 1): 20
Digite a Porta Final (padrão 65535): 1000
```

O scanner irá processar as portas em paralelo e exibirá o resultado no terminal.

## Resultados

Após o escaneamento, o script exibe um resumo com:
- **Portas abertas** e seus serviços
- **Portas filtradas** (possivelmente bloqueadas por firewall)
- **Estimativa do sistema operacional** do alvo

## Suporte a IPv6

O código foi atualizado para suportar IPv6. Para escanear um host IPv6, basta inserir um endereço compatível.

## Vídeo referência: 

https://www.youtube.com/watch?v=nYPV1rCVdvs
