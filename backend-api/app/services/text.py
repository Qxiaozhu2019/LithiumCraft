from urllib.parse import urlparse


def normalize_title(title: str) -> str:
    return " ".join(title.strip().lower().split())


def domain_from_url(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")


def csv_to_set(value: str | None) -> set[str]:
    if not value:
        return set()
    return {item.strip() for item in value.replace("\n", ",").split(",") if item.strip()}
