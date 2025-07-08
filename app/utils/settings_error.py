from __future__ import annotations
import sys

from pydantic import ValidationError


def abort_with_validation_errors(exc: ValidationError) -> None:  # pragma: no cover
    """
    Mostra erros de validação de forma amigável e encerra o programa.
    • Se Rich estiver instalado: tabela colorida
    • Caso contrário: texto simples
    """
    try:
        from rich.console import Console
        from rich.table import Table
    except ModuleNotFoundError:          # Rich não instalado
        print("❌  Erro de configuração – aplicação abortada:")
        for err in exc.errors():
            loc = ".".join(str(p) for p in err["loc"])
            print(f"  • {loc}: {err['msg']}")
        sys.exit(1)

    console = Console()
    table = Table(
        title="🚫  Configuração de ambiente inválida",
        style="red",
        show_header=True,
        header_style="bold",
    )
    table.add_column("Campo")
    table.add_column("Problema")

    for err in exc.errors():
        loc = ".".join(str(p) for p in err["loc"])
        table.add_row(loc, err["msg"])

    console.print(table)
    sys.exit(1)
