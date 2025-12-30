import os
import base64
import logging
import requests
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any, List, Tuple
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger("servientrega_ws22")

SERVI_URL = os.getenv("SERVI_URL_QA")
SERVI_LOGIN = os.getenv("SERVI_LOGIN")
SERVI_PWD_ENC = os.getenv("SERVI_PWD_ENC")
SERVI_COD_FACT = os.getenv("SERVI_COD_FACT")
TIMEOUT = int(os.getenv("SERVI_TIMEOUT", "60"))

SOAPENV = "http://schemas.xmlsoap.org/soap/envelope/"
TEM = "http://tempuri.org/"

NS = {"soapenv": SOAPENV, "tem": TEM}


def _localname(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _parse_xml(xml: str) -> ET.Element:
    return ET.fromstring(xml.encode("utf-8") if isinstance(xml, str) else xml)


def _find_first_text_by_localname(root: ET.Element, names: List[str]) -> Optional[str]:
    targets = {n.lower() for n in names}
    for el in root.iter():
        if _localname(el.tag).lower() in targets:
            if el.text and el.text.strip():
                return el.text.strip()
    return None


def _extract_soap_fault(xml_resp: str) -> Optional[Dict[str, Any]]:
    try:
        root = _parse_xml(xml_resp)
        for el in root.iter():
            if _localname(el.tag).lower() == "fault":
                return {
                    "error": "soap_fault",
                    "fault_xml": ET.tostring(el, encoding="unicode"),
                }
    except Exception:
        pass
    return None


def _soap_post(xml: str) -> str:
    headers = {"Content-Type": "text/xml; charset=utf-8"}
    r = requests.post(
        SERVI_URL, data=xml.encode("utf-8"), headers=headers, timeout=TIMEOUT
    )
    r.raise_for_status()
    return r.text


def _envelope(body: ET.Element) -> str:
    env = ET.Element(f"{{{SOAPENV}}}Envelope")
    hdr = ET.SubElement(env, f"{{{SOAPENV}}}Header")
    auth = ET.SubElement(hdr, f"{{{TEM}}}AuthHeader")
    ET.SubElement(auth, f"{{{TEM}}}login").text = SERVI_LOGIN
    ET.SubElement(auth, f"{{{TEM}}}pwd").text = SERVI_PWD_ENC
    ET.SubElement(auth, f"{{{TEM}}}Id_CodFacturacion").text = SERVI_COD_FACT
    ET.SubElement(auth, f"{{{TEM}}}Nombre_Cargue").text = "Odoo Servientrega"
    bod = ET.SubElement(env, f"{{{SOAPENV}}}Body")
    bod.append(body)
    return ET.tostring(env, encoding="unicode")


def create_shipment_envios_externo(envio_xml_inner: str) -> Tuple[bool, Dict[str, Any]]:
    root = ET.Element(f"{{{TEM}}}CargueMasivoExterno")
    envios = ET.SubElement(root, f"{{{TEM}}}envios")
    dto = ET.SubElement(envios, f"{{{TEM}}}CargueMasivoExternoDTO")
    obj = ET.SubElement(dto, f"{{{TEM}}}objEnvios")

    obj.append(ET.fromstring(envio_xml_inner))
    xml_resp = _soap_post(_envelope(root))

    fault = _extract_soap_fault(xml_resp)
    if fault:
        fault["raw_xml"] = xml_resp
        return False, fault

    root_resp = _parse_xml(xml_resp)
    guia = _find_first_text_by_localname(root_resp, ["Num_Guia", "NumeroGuia"])
    if not guia:
        return False, {"error": "no_num_guia", "raw_xml": xml_resp}

    return True, {"num_guia": guia, "raw_xml": xml_resp}


def print_label(num_guia: str) -> Tuple[bool, Dict[str, Any]]:
    root = ET.Element(f"{{{TEM}}}GenerarGuiaSticker")
    ET.SubElement(root, f"{{{TEM}}}num_Guia").text = num_guia
    ET.SubElement(root, f"{{{TEM}}}num_GuiaFinal").text = num_guia
    ET.SubElement(root, f"{{{TEM}}}ide_CodFacturacion").text = SERVI_COD_FACT
    ET.SubElement(root, f"{{{TEM}}}sFormatoImpresionGuia").text = "1"
    ET.SubElement(root, f"{{{TEM}}}interno").text = "false"

    xml_resp = _soap_post(_envelope(root))

    fault = _extract_soap_fault(xml_resp)
    if fault:
        fault["raw_xml"] = xml_resp
        return False, fault

    root_resp = _parse_xml(xml_resp)
    b64 = _find_first_text_by_localname(root_resp, ["bytesReport"])
    if not b64:
        return False, {"error": "no_pdf", "raw_xml": xml_resp}

    return True, {"pdf_bytes": base64.b64decode(b64)}
