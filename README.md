# OBD Driver 🚗💨

Aplicativo desenvolvido com **Flet** (Python) para monitoramento de veículos em tempo real via adaptadores OBD-II (ELM327). Focado em veículos da linha Chevrolet (Astra, Zafira, Corsa, Vectra), mas compatível com outros modelos via protocolo AUTO.

## 📱 Como baixar o APK

O APK é gerado automaticamente a cada atualização do código através do GitHub Actions. Para baixar a versão mais recente:

1.  Acesse a aba [**Actions**](https://github.com/Leoturbo/obd-driver/actions) do repositório.
2.  Clique no build mais recente que tenha um check verde (✅).
3.  Role a página até a seção **Artifacts**.
4.  Clique em **obd-driver-apk** para baixar o arquivo `.zip`.
5.  Extraia o arquivo `.apk` de dentro do zip e instale no seu Android.

> **Nota:** Ao instalar, o Android pode perguntar se você deseja instalar de "fontes desconhecidas". Como este é um app em desenvolvimento, você pode autorizar com segurança.

## 🛠️ Requisitos e Preparação

1.  **Adaptador OBD-II**: Você precisará de um ELM327 Bluetooth ou USB.
2.  **Pareamento**: Antes de abrir o app, pareie o seu celular com o adaptador nas configurações de Bluetooth (geralmente senha `1234` ou `0000`).
3.  **Permissões**: O app solicitará acesso à **Localização** e **Dispositivos Próximos** (Bluetooth). Ambas são obrigatórias no Android para que a comunicação serial-bluetooth funcione.

## 🚀 Funcionalidades

- **Dashboard Real-time**: Monitoramento de RPM, Velocidade, Temperatura do Fluido e Voltagem da ECU.
- **Log de Dados**: Salva as leituras em um arquivo CSV (`logs/obd_log.csv`) para análise posterior.
- **Diagnóstico (DTC)**: Leitura e limpeza de códigos de erro da injeção eletrônica.
- **Perfis de Veículos**: Configurações pré-definidas para Astra, Zafira, Corsa e Vectra.

## 🔧 Tecnologias

- [Flet](https://flet.dev/) - Framework de interface baseada em Flutter.
- [Python-OBD](https://python-obd.github.io/python-obd/) - Biblioteca para comunicação com o ELM327.
- [GitHub Actions](https://github.com/features/actions) - Automação de build para Android.

---
Desenvolvido por Leo.
