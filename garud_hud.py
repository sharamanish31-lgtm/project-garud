import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.align import Align

console = Console()

def generate_dashboard():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body", size=12),
        Layout(name="footer", size=3)
    )
    
    # 1. Top Bar Header Matrix (Fixed using Align class)
    header_text = "[bold cyan]🤖 PROJECT GARUD : STEALTH COMMAND CENTER V2.0[/bold cyan]"
    layout["header"].update(Panel(Align.center(header_text), border_style="cyan"))
    
    # 2. Main Center Body Data
    core_info = """
    [bold green]COMMANDER:[/bold green] Manish Sharma  |  [bold green]LOCATION:[/bold green] Solan, HP
    [bold yellow]MEMORY CORE:[/bold yellow] 8-Dimension Pinecone DB Online (2026-2030)
    [bold magenta]SERVER REGION:[/bold magenta] AWS Mumbai (ap-south-1) | [bold magenta]IP:[/bold magenta] 52.66.23.197
    [bold red]FIREWALL SECURITY:[/bold red] UFW Active & Enforced to Local Matrix IP
    """
    layout["body"].update(Panel(core_info, title="[bold green]SYSTEM MATRIX PROFILE[/bold green]", border_style="green"))
    
    # 3. Bottom Execution Status (Fixed using Align class)
    footer_text = "[blink bold yellow]🛡️ SYSTEM NOMINAL : ZERO TRUST ARCHITECTURE DEPLOYED[/blink bold yellow]"
    layout["footer"].update(Panel(Align.center(footer_text), border_style="yellow"))
    
    return layout

if __name__ == "__main__":
    console.clear()
    with Live(generate_dashboard(), refresh_per_second=4) as live:
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            console.print("\n[bold red][ALERT] Jarvis Dashboard Standby Mode Engaged.[/bold red]")
