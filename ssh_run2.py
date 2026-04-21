if __name__ == "__main__":
    commands = [
        "cd /opt/contenedores/Arquitectura/ && docker compose ps",
        "cd /opt/contenedores/Arquitectura/ && docker logs frontend_portal"
    ]
    run_ssh_command("192.168.1.208", "wmfernandez", "Winston-2010", commands)
