import typer

app = typer.Typer(no_args_is_help=True)


@app.command(no_args_is_help=True)
def hello(name: str):
    print(f"Hello {name}")


@app.command(no_args_is_help=True)
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")
