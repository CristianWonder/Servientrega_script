import os
import logging
import requests
import base64
import re
from typing import Any, Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger("odoo_rpc")

# ===== SWITCH DE AMBIENTE =====
# Lee la variable USE_PRODUCTION del .env
USE_PRODUCTION = os.getenv("USE_PRODUCTION", "false").lower() in ["true", "1", "yes"]

# Selecciona las credenciales según el ambiente
if USE_PRODUCTION:
    log.info("🚀 USANDO AMBIENTE DE PRODUCCIÓN")
    ODOO_JSONRPC = os.getenv("PROD_ODOO_JSONRPC")
    DB = os.getenv("PROD_ODOO_DB")
    UID = int(os.getenv("PROD_ODOO_UID", "0"))
    PWD = os.getenv("PROD_ODOO_PASSWORD")
    CALLBACK_URL = os.getenv("PROD_CALLBACK_URL")
else:
    log.info("🧪 USANDO AMBIENTE DE PRUEBAS")
    ODOO_JSONRPC = os.getenv("TEST_ODOO_JSONRPC")
    DB = os.getenv("TEST_ODOO_DB")
    UID = int(os.getenv("TEST_ODOO_UID", "0"))
    PWD = os.getenv("TEST_ODOO_PASSWORD")
    CALLBACK_URL = os.getenv("TEST_CALLBACK_URL")

TIMEOUT = int(os.getenv("ODOO_TIMEOUT", "35"))


def _post(payload: Dict[str, Any]) -> Tuple[bool, dict]:
    """POST JSON-RPC a Odoo."""
    try:
        if not ODOO_JSONRPC:
            return False, {
                "error": "missing_env",
                "detail": "Falta ODOO_JSONRPC en .env",
            }
        r = requests.post(
            ODOO_JSONRPC,
            json=payload,
            timeout=TIMEOUT,
            headers={"Content-Type": "application/json"},
        )
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            return False, data
        return True, data
    except Exception as e:
        return False, {"error": "odoo_rpc_http_failed", "detail": str(e)}


def execute_kw(
    model: str,
    method: str,
    args: List[Any],
    kwargs: Optional[Dict[str, Any]] = None,
    rpc_id: int = 10,
) -> Tuple[bool, dict]:
    """Llamada genérica execute_kw."""
    payload = {
        "jsonrpc": "2.0",
        "id": rpc_id,
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [DB, UID, PWD, model, method, args] + ([kwargs] if kwargs else []),
        },
    }
    return _post(payload)


def search_read(
    model: str,
    domain: List[Any],
    fields: List[str],
    limit: int = 80,
    order: Optional[str] = None,
) -> Tuple[bool, dict]:
    kwargs = {"fields": fields, "limit": limit}
    if order:
        kwargs["order"] = order
    return execute_kw(model, "search_read", [domain], kwargs, rpc_id=11)


def read(model: str, ids: List[int], fields: List[str]) -> Tuple[bool, dict]:
    return execute_kw(model, "read", [ids], {"fields": fields}, rpc_id=12)


def write(model: str, ids: List[int], vals: Dict[str, Any]) -> Tuple[bool, dict]:
    return execute_kw(model, "write", [ids, vals], None, rpc_id=13)


def create(model: str, vals: Dict[str, Any]) -> Tuple[bool, dict]:
    return execute_kw(model, "create", [vals], None, rpc_id=14)


def attach_pdf_to_record(
    res_model: str, res_id: int, filename: str, pdf_bytes: bytes
) -> Tuple[bool, dict]:
    datas = base64.b64encode(pdf_bytes).decode("ascii")
    vals = {
        "name": filename,
        "type": "binary",
        "mimetype": "application/pdf",
        "res_model": res_model,
        "res_id": res_id,
        "datas": datas,
    }
    return create("ir.attachment", vals)


# ---------- helpers "10/10": tolerancia a campos que no existan ----------
def _extract_unknown_field(err_payload: dict) -> Optional[str]:
    """Intenta extraer el nombre de un campo inválido/desconocido desde un error JSON-RPC de Odoo."""
    try:
        msg = (err_payload.get("error") or {}).get("data", {}).get("message", "") or ""
        m = re.search(r"[Uu]nknown field ([a-zA-Z0-9_]+)", msg)
        if m:
            return m.group(1)
        m = re.search(r"[Ii]nvalid field ['\"]([a-zA-Z0-9_]+)['\"]", msg)
        if m:
            return m.group(1)
    except Exception:
        pass
    return None


def safe_read(
    model: str, ids: List[int], fields: List[str]
) -> Tuple[bool, dict, List[str]]:
    """
    read() con tolerancia a campos desconocidos.
    Retorna (ok, resp, fields_usados).
    """
    f = list(fields)
    for _ in range(5):
        ok, resp = read(model, ids, f)
        if ok:
            return True, resp, f
        unk = _extract_unknown_field(resp)
        if unk and unk in f:
            f.remove(unk)
            continue
        return False, resp, f
    return False, {"error": "safe_read_failed"}, f


def safe_write(
    model: str, ids: List[int], vals: Dict[str, Any]
) -> Tuple[bool, dict, Dict[str, Any]]:
    """
    write() con tolerancia a campos desconocidos.
    Retorna (ok, resp, vals_usados).
    """
    v = dict(vals)
    for _ in range(5):
        ok, resp = write(model, ids, v)
        if ok:
            return True, resp, v
        unk = _extract_unknown_field(resp)
        if unk and unk in v:
            v.pop(unk, None)
            continue
        return False, resp, v
    return False, {"error": "safe_write_failed"}, v


def safe_create(model: str, vals: Dict[str, Any]) -> Tuple[bool, dict, Dict[str, Any]]:
    """
    create() con tolerancia a campos desconocidos.
    Retorna (ok, resp, vals_usados).
    """
    v = dict(vals)
    for _ in range(5):
        ok, resp = create(model, v)
        if ok:
            return True, resp, v
        unk = _extract_unknown_field(resp)
        if unk and unk in v:
            v.pop(unk, None)
            continue
        return False, resp, v
    return False, {"error": "safe_create_failed"}, v


# ✅ CAMBIO (IMPORTANTE): message_post para chatter (lo que te faltaba antes)
def message_post(
    model: str,
    res_id: int,
    body: str,
    message_type: str = "comment",
    subtype_xmlid: str = "mail.mt_comment",
) -> Tuple[bool, dict]:
    """
    Publica un mensaje en el chatter de un registro (ej: stock.picking).
    """
    vals = {
        "body": body,
        "message_type": message_type,
        "subtype_xmlid": subtype_xmlid,
        "res_id": int(res_id),
        "model": model,
    }
    return execute_kw("mail.message", "create", [vals], None, rpc_id=20)


# ✅ CAMBIO (IMPORTANTE): escritura de guía en Odoo (carrier_tracking_ref)
def write_tracking_ref(
    picking_id: int, tracking_ref: str
) -> Tuple[bool, dict, Dict[str, Any]]:
    """
    Escribe la guía (carrier_tracking_ref) en el picking.
    Retorna lo mismo que safe_write: (ok, resp, vals_usados)
    """
    return safe_write(
        "stock.picking",
        [int(picking_id)],
        {"carrier_tracking_ref": tracking_ref},
    )
