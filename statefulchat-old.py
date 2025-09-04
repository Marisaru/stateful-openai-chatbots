import os
import json
import dotenv
from datetime import datetime
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

dotenv.load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
console = Console()

def save_conversation_to_log(conversation):
    """Guarda la conversación en archivos de log (TXT y JSON) con formato log_dia_hora"""
    # Crear la carpeta logs si no existe
    os.makedirs("logs", exist_ok=True)
    
    # Generar nombre base del archivo con formato log_YYYYMMDD_HHMMSS
    now = datetime.now()
    base_filename = f"log_{now.strftime('%Y%m%d_%H%M%S')}"
    
    # Guardar archivo TXT
    txt_filepath = os.path.join("logs", f"{base_filename}.txt")
    with open(txt_filepath, 'w', encoding='utf-8') as f:
        f.write(f"CONVERSACIÓN GUARDADA EL {now.strftime('%d/%m/%Y a las %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")
        
        for message in conversation:
            role = message["role"]
            content = message["content"]
            timestamp = now.strftime('%H:%M:%S')
            
            if role == "system":
                f.write(f"[SISTEMA - {timestamp}] {content}\n")
            elif role == "user":
                f.write(f"[USUARIO - {timestamp}] {content}\n")
            elif role == "assistant":
                f.write(f"[ASISTENTE - {timestamp}] {content}\n")
            f.write("-" * 40 + "\n")
    
    # Guardar archivo JSON
    json_filepath = os.path.join("logs", f"{base_filename}.json")
    conversation_data = {
        "metadata": {
            "saved_at": now.strftime('%d/%m/%Y a las %H:%M:%S'),
            "timestamp": now.isoformat(),
            "total_messages": len(conversation)
        },
        "conversation": conversation
    }
    
    with open(json_filepath, 'w', encoding='utf-8') as f:
        json.dump(conversation_data, f, ensure_ascii=False, indent=2)
    
    return txt_filepath, json_filepath

def save_conversation_json_only(conversation):
    """Guarda solo la conversación en formato JSON"""
    # Crear la carpeta logs si no existe
    os.makedirs("logs", exist_ok=True)
    
    # Generar nombre del archivo con formato log_YYYYMMDD_HHMMSS.json
    now = datetime.now()
    filename = f"log_{now.strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join("logs", filename)
    
    # Crear estructura de datos con metadata
    conversation_data = {
        "metadata": {
            "saved_at": now.strftime('%d/%m/%Y a las %H:%M:%S'),
            "timestamp": now.isoformat(),
            "total_messages": len(conversation)
        },
        "conversation": conversation
    }
    
    # Escribir archivo JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(conversation_data, f, ensure_ascii=False, indent=2)
    
    return filepath

def list_previous_conversations():
    """Lista las conversaciones anteriores disponibles en la carpeta logs"""
    if not os.path.exists("logs"):
        return []
    
    json_files = []
    for filename in os.listdir("logs"):
        if filename.endswith('.json') and filename.startswith('log_'):
            filepath = os.path.join("logs", filename)
            try:
                # Obtener información del archivo
                stat = os.stat(filepath)
                modified_time = datetime.fromtimestamp(stat.st_mtime)
                
                # Leer metadata del JSON
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    metadata = data.get('metadata', {})
                    total_messages = metadata.get('total_messages', 0)
                
                json_files.append({
                    'filename': filename,
                    'filepath': filepath,
                    'modified_time': modified_time,
                    'total_messages': total_messages,
                    'saved_at': metadata.get('saved_at', 'Fecha desconocida')
                })
            except Exception as e:
                # Si hay error leyendo el archivo, lo omitimos
                continue
    
    # Ordenar por fecha de modificación (más reciente primero)
    json_files.sort(key=lambda x: x['modified_time'], reverse=True)
    return json_files

def load_conversation_from_json(filepath):
    """Carga una conversación desde un archivo JSON"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            conversation = data.get('conversation', [])
            metadata = data.get('metadata', {})
            return conversation, metadata
    except Exception as e:
        raise Exception(f"Error al cargar la conversación: {e}")

def show_startup_menu():
    """Muestra el menú de inicio y retorna la opción elegida"""
    console.print("\n" + "="*60)
    console.print(Panel.fit("🤖 CHATBOT ESTATEFUL - MENÚ DE INICIO", style="bold blue"))
    console.print("="*60)
    console.print()
    console.print("Selecciona una opción:")
    console.print("1️⃣  [bold green]Nuevo chat[/bold green]")
    console.print("2️⃣  [bold blue]Continuar chat anterior[/bold blue]")
    console.print()
    
    while True:
        try:
            choice = input("Ingresa tu opción (1 o 2): ").strip()
            if choice in ['1', '2']:
                return choice
            else:
                console.print("❌ [bold red]Opción inválida. Por favor ingresa 1 o 2.[/bold red]")
        except KeyboardInterrupt:
            console.print("\n\n👋 [bold yellow]Saliendo...[/bold yellow]")
            exit(0)

def show_conversation_list(conversations):
    """Muestra la lista de conversaciones anteriores"""
    if not conversations:
        console.print("❌ [bold red]No se encontraron conversaciones anteriores.[/bold red]")
        return None
    
    console.print(f"\n📋 [bold blue]Conversaciones anteriores encontradas:[/bold blue]")
    console.print("-" * 60)
    
    for i, conv in enumerate(conversations, 1):
        console.print(f"{i:2d}. [bold]{conv['filename']}[/bold]")
        console.print(f"    📅 Guardado: {conv['saved_at']}")
        console.print(f"    💬 Mensajes: {conv['total_messages']}")
        console.print(f"    🕒 Modificado: {conv['modified_time'].strftime('%d/%m/%Y %H:%M:%S')}")
        console.print()
    
    while True:
        try:
            choice = input(f"Ingresa el número de la conversación (1-{len(conversations)}) o '0' para cancelar: ").strip()
            if choice == '0':
                return None
            choice_num = int(choice)
            if 1 <= choice_num <= len(conversations):
                return conversations[choice_num - 1]
            else:
                console.print(f"❌ [bold red]Número inválido. Ingresa un número entre 1 y {len(conversations)}.[/bold red]")
        except ValueError:
            console.print("❌ [bold red]Por favor ingresa un número válido.[/bold red]")
        except KeyboardInterrupt:
            console.print("\n\n👋 [bold yellow]Saliendo...[/bold yellow]")
            exit(0)

def main():
    # Mostrar menú de inicio
    choice = show_startup_menu()
    
    model = "gpt-4o-mini"
    conversation = []
    
    if choice == '1':
        # Nuevo chat
        console.print("\n🆕 [bold green]Iniciando nuevo chat...[/bold green]")
        conversation = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
    elif choice == '2':
        # Continuar chat anterior
        conversations = list_previous_conversations()
        selected_conv = show_conversation_list(conversations)
        
        if selected_conv is None:
            console.print("\n🆕 [bold green]Iniciando nuevo chat...[/bold green]")
            conversation = [
                {"role": "system", "content": "You are a helpful assistant."}
            ]
        else:
            try:
                conversation, metadata = load_conversation_from_json(selected_conv['filepath'])
                console.print(f"\n✅ [bold green]Conversación cargada exitosamente![/bold green]")
                console.print(f"📁 Archivo: {selected_conv['filename']}")
                console.print(f"💬 Mensajes: {metadata.get('total_messages', 0)}")
                console.print(f"📅 Guardado: {metadata.get('saved_at', 'Fecha desconocida')}")
                console.print()
            except Exception as e:
                console.print(f"\n❌ [bold red]Error al cargar la conversación:[/bold red] {e}")
                console.print("🆕 [bold green]Iniciando nuevo chat...[/bold green]")
                conversation = [
                    {"role": "system", "content": "You are a helpful assistant."}
                ]
    
    console.print("💬 [bold blue]Chat iniciado. Escribe 'exit' para salir, 'contexto' para ver el historial.[/bold blue]")
    console.print()
    while True:
        user_input = input("You: ")
        if user_input.lower() in {"exit", "quit"}:
            # Guardar automáticamente la conversación al salir
            try:
                txt_filepath, json_filepath = save_conversation_to_log(conversation)
                console.print(f"\n💾 [bold blue]Conversación guardada automáticamente:[/bold blue]")
                console.print(f"📄 TXT: {txt_filepath}")
                console.print(f"📋 JSON: {json_filepath}")
            except Exception as e:
                console.print(f"\n❌ [bold red]Error al guardar automáticamente:[/bold red] {e}")
            
            console.print("\n👋 [bold yellow]Goodbye![/bold yellow]")
            break
        
        # Verificar si el usuario quiere ver el contexto
        if user_input.lower().strip() in {"contexto", "context", "conversación", "conversacion", "historial", "history"}:
            console.print("\n")
            console.print(Panel.fit("📋 CONTEXTO DE LA CONVERSACIÓN", style="bold blue"))
            console.print()
            
            for i, message in enumerate(conversation):
                role = message["role"]
                content = message["content"]
                
                if role == "system":
                    panel = Panel(
                        content,
                        title="[bold green]SISTEMA[/bold green]",
                        border_style="green",
                        padding=(0, 1)
                    )
                elif role == "user":
                    panel = Panel(
                        content,
                        title="[bold blue]USUARIO[/bold blue]",
                        border_style="blue",
                        padding=(0, 1)
                    )
                elif role == "assistant":
                    panel = Panel(
                        content,
                        title="[bold magenta]ASISTENTE[/bold magenta]",
                        border_style="magenta",
                        padding=(0, 1)
                    )
                
                console.print(panel)
                console.print()
            
            console.print(Panel.fit("✨ Fin del contexto", style="dim"))
            console.print()
            continue
        
        # Verificar si el usuario quiere guardar la conversación
        if user_input.lower().strip() in {"guardar", "save", "exportar", "export"}:
            try:
                txt_filepath, json_filepath = save_conversation_to_log(conversation)
                console.print(f"\n✅ [bold green]Conversación guardada:[/bold green]")
                console.print(f"📄 TXT: {txt_filepath}")
                console.print(f"📋 JSON: {json_filepath}")
                console.print()
            except Exception as e:
                console.print(f"\n❌ [bold red]Error al guardar:[/bold red] {e}")
                console.print()
            continue
        
        # Verificar si el usuario quiere guardar solo JSON
        if user_input.lower().strip() in {"json", "exportar json", "export json"}:
            try:
                json_filepath = save_conversation_json_only(conversation)
                console.print(f"\n✅ [bold green]Conversación guardada en JSON:[/bold green] {json_filepath}")
                console.print()
            except Exception as e:
                console.print(f"\n❌ [bold red]Error al guardar JSON:[/bold red] {e}")
                console.print()
            continue
        
        conversation.append({"role": "user", "content": user_input})
        try:
            response = client.chat.completions.create(
                model=model,
                messages=conversation
            )
            text = response.choices[0].message.content.strip()
            print(f"Bot: {text}")
            conversation.append({"role": "assistant", "content": text})
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
