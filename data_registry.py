from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import unquote
from zoneinfo import ZoneInfo

import requests
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class ProviderSpec:
    provider_id: str
    name: str
    capabilities: tuple[str, ...]
    env_keys: tuple[str, ...] = field(default_factory=tuple)


PROVIDERS = (
    ProviderSpec(
        "opendart",
        "OpenDART",
        (
            "stock.profile",
            "stock.financials",
            "stock.disclosures",
            "stock.business_report",
        ),
        ("DART_CRTFC_KEY",),
    ),
    ProviderSpec(
        "data_go_kr_stock",
        "금융위원회 주식시세정보",
        ("stock.search", "stock.quote"),
        ("DATA_GO_KR_SERVICE_KEY",),
    ),
)


def configured(spec: ProviderSpec) -> bool:
    return all(bool(os.getenv(key, "").strip()) for key in spec.env_keys)


def capabilities() -> set[str]:
    active = set()
    for spec in PROVIDERS:
        if configured(spec):
            active.update(spec.capabilities)
    return active


def _result(provider_id: str, status: str, detail: str, started: float):
    return {
        "provider_id": provider_id,
        "status": status,
        "detail": detail,
        "latency_ms": round((time.perf_counter() - started) * 1000),
        "checked_at": datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S"),
    }


def health(spec: ProviderSpec) -> dict:
    started = time.perf_counter()
    if not configured(spec):
        return _result(spec.provider_id, "not_configured", "인증정보 미설정", started)

    try:
        if spec.provider_id == "opendart":
            key = os.getenv("DART_CRTFC_KEY", "").strip()
            response = requests.get(
                "https://opendart.fss.or.kr/api/company.json",
                params={"crtfc_key": key, "corp_code": "00126380"},
                timeout=(5, 12),
            )
            response.raise_for_status()
            payload = response.json()
            code = str(payload.get("status", ""))
            if code == "000":
                return _result(spec.provider_id, "ok", "연결·인증 정상", started)
            known = {
                "010": "키 미등록",
                "011": "키 사용 중지",
                "012": "IP 제한",
                "020": "호출 한도 초과",
                "013": "연결됨 · 자료 없음",
                "800": "기관 점검 중",
            }
            return _result(spec.provider_id, "error", known.get(code, f"응답코드 {code or '확인 필요'}"), started)

        if spec.provider_id == "data_go_kr_stock":
            raw_key = os.getenv("DATA_GO_KR_SERVICE_KEY", "").strip()
            key_variants = [("입력값 그대로", raw_key)]
            decoded_key = unquote(raw_key)
            if decoded_key != raw_key:
                key_variants.append(("URL 디코딩값", decoded_key))

            response = None
            key_mode = ""
            for mode, key in key_variants:
                candidate = requests.get(
                    "https://apis.data.go.kr/1160100/GetStockSecuritiesInfoService_V2/getStockPriceInfo",
                    params={"serviceKey": key, "resultType": "json", "numOfRows": 1, "pageNo": 1},
                    timeout=(5, 12),
                )
                response = candidate
                key_mode = mode
                try:
                    candidate_payload = candidate.json()
                    candidate_code = str(candidate_payload.get("response", {}).get("header", {}).get("resultCode", ""))
                    if candidate_code in {"00", "0", "000"}:
                        return _result(spec.provider_id, "ok", f"연결·인증 정상 · {mode}", started)
                except (ValueError, TypeError, AttributeError):
                    pass
                if candidate.status_code == 400:
                    body_preview = (candidate.text or "").replace("\n", " ").replace("\r", " ")[:180]
                    return _result(
                        spec.provider_id,
                        "error",
                        f"HTTP 400 · V2 요청 형식 오류 · 인증키 전송: {mode} · 응답: {body_preview or '본문 없음'}",
                        started,
                    )
            # 공공데이터포털은 인증 오류도 HTTP 500 + XML로 반환할 수 있어 본문을 먼저 해석합니다.
            code = ""
            message = ""
            try:
                payload = response.json()
                header = payload.get("response", {}).get("header", {})
                code = str(header.get("resultCode", ""))
                message = str(header.get("resultMsg", ""))
            except (ValueError, TypeError, AttributeError):
                try:
                    root = ET.fromstring(response.text)
                    code = str(
                        root.findtext(".//resultCode")
                        or root.findtext(".//returnReasonCode")
                        or ""
                    )
                    message = str(
                        root.findtext(".//resultMsg")
                        or root.findtext(".//returnAuthMsg")
                        or root.findtext(".//errMsg")
                        or ""
                    )
                except ET.ParseError:
                    return _result(
                        spec.provider_id,
                        "error",
                        f"응답 형식 오류 · HTTP {response.status_code}",
                        started,
                    )

            if code in {"00", "0", "000"}:
                return _result(spec.provider_id, "ok", "연결·인증 정상", started)

            known = {
                "20": "서비스 활용신청·접근권한 확인 필요",
                "22": "호출 한도 초과",
                "30": "등록되지 않은 서비스키",
                "31": "서비스키 이용기간 만료",
                "32": "등록되지 않은 IP",
                "99": "공공데이터포털 서비스 오류",
                "SERVICE_ACCESS_DENIED_ERROR": "서비스 활용신청·접근권한 확인 필요",
                "SERVICE_KEY_IS_NOT_REGISTERED_ERROR": "등록되지 않은 서비스키",
                "DEADLINE_HAS_EXPIRED_ERROR": "서비스키 이용기간 만료",
            }
            detail = known.get(code)
            if detail == "서비스 활용신청·접근권한 확인 필요":
                detail += f" · 현재 앱 호출: V2/getStockPriceInfo · 인증키 전송: {key_mode}"
            if not detail:
                upper_message = message.upper()
                http_known = {
                    401: "인증 실패 · 서비스키 확인 필요",
                    403: "서비스 활용신청·접근권한 확인 필요",
                    429: "호출 한도 초과",
                    500: "공공데이터포털 인증 또는 서비스 상태 확인 필요",
                    503: "공공데이터포털 일시 점검 중",
                }
                detail = next(
                    (label for token, label in known.items() if token in upper_message),
                    message
                    or http_known.get(response.status_code)
                    or f"응답코드 {code or '없음'} · HTTP {response.status_code}",
                )
            return _result(spec.provider_id, "error", detail, started)

        return _result(spec.provider_id, "unknown", "진단 미구현", started)
    except requests.Timeout:
        return _result(spec.provider_id, "error", "응답 시간 초과", started)
    except requests.exceptions.SSLError:
        return _result(spec.provider_id, "error", "TLS 보안 연결 실패", started)
    except requests.ConnectionError:
        return _result(spec.provider_id, "error", "네트워크 연결 실패", started)
    except (requests.RequestException, ValueError, KeyError, TypeError):
        return _result(spec.provider_id, "error", "정상 응답을 확인하지 못함", started)


def health_all() -> list[dict]:
    return [{**health(spec), "name": spec.name, "capabilities": list(spec.capabilities)} for spec in PROVIDERS]


def missing_capabilities(required: list[str] | tuple[str, ...]) -> list[str]:
    active = capabilities()
    return [cap for cap in required if cap not in active]
