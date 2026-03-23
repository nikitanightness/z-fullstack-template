from app import config


def main() -> None:
    import uvicorn

    # Run ASGI Server
    uvicorn.run(
        "app.web.app:build_app",
        factory=True,
        host=config.app.host,
        port=config.app.port,
        proxy_headers=config.app.enable_proxy_mode,  # Allow 'x-forwarded*' headers passed by proxy (e.g. nginx)
        forwarded_allow_ips=config.security.trusted_proxy_ips,  # IP address of proxy (e.g. nginx container ip)
        reload=config.debug,  # Hot reload in debug mode
    )


if __name__ == "__main__":
    main()
