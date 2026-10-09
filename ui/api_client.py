import httpx

from settings import API_ACCESS_KEY, API_URL


class ApiError(Exception):
    pass


def ask(question: str) -> dict:
    try:
        response = httpx.post(
            f"{API_URL}/chat",
            json={"question": question},
            headers={"X-API-Key": API_ACCESS_KEY},
            timeout=90,
        )
    except httpx.RequestError as exc:
        raise ApiError("Could not reach the API. Is the server running?") from exc

    if response.status_code == 200:
        return response.json()

    try:
        detail = response.json().get("detail")
    except ValueError:
        detail = None
    if not isinstance(detail, str):
        detail = f"Request failed (status {response.status_code})."
    raise ApiError(detail)