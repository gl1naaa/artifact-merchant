"""Initial command-line entry point."""

from . import __version__


def main() -> None:
    print(f"Artifact Merchant v{__version__}")
    print("Проект создан. Игровой вертикальный срез находится в разработке.")


if __name__ == "__main__":
    main()
