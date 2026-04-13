from __future__ import annotations

from pathlib import Path

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
import xml.etree.ElementTree as ET

@dataclass(frozen=True)
class InputRecord:
    num_linha: int
    cod_pais: int
    codigo: str
    ano_realizacao: int
    mes_realizacao: int
    dia_realizacao: int
    valor_realizacao: Decimal
    ano_aquisicao: int
    mes_aquisicao: int
    dia_aquisicao: int
    valor_aquisicao: Decimal
    valor_despesas_encargos: Decimal
    imposto_pago: Decimal
    cod_pais_contraparte: int
    respeita_valores_mobiliarios: str

def _parse_anexoj_92a_csv(csv_path: str) -> list[InputRecord]:
    """Parse the Anexo J 9.2.A CSV file into a list of InputRecord instances."""
    records = []
    with open(csv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue  # Skip empty lines and comments

            parts = line.split(",")
            if len(parts) != 15:
                print(f"Skipping invalid line (expected 15 fields): {line}")
                continue

            try:
                num_linha = int(parts[0])
                cod_pais = int(parts[1])
                codigo = parts[2]
                ano_realizacao = int(parts[3])
                mes_realizacao = int(parts[4])
                dia_realizacao = int(parts[5])
                valor_realizacao = Decimal(parts[6])
                ano_aquisicao = int(parts[7])
                mes_aquisicao = int(parts[8])
                dia_aquisicao = int(parts[9])
                valor_aquisicao = Decimal(parts[10])
                valor_despesas_encargos = Decimal(parts[11])
                imposto_pago = Decimal(parts[12])
                cod_pais_contraparte = int(parts[13])
                respeita_valores_mobiliarios = parts[14]

                records.append(InputRecord(num_linha=num_linha, cod_pais=cod_pais, codigo=codigo,
                                           ano_realizacao=ano_realizacao, mes_realizacao=mes_realizacao, dia_realizacao=dia_realizacao,
                                           valor_realizacao=valor_realizacao, ano_aquisicao=ano_aquisicao, mes_aquisicao=mes_aquisicao,
                                           dia_aquisicao=dia_aquisicao, valor_aquisicao=valor_aquisicao, valor_despesas_encargos=valor_despesas_encargos,
                                           imposto_pago=imposto_pago, cod_pais_contraparte=cod_pais_contraparte,
                                           respeita_valores_mobiliarios=respeita_valores_mobiliarios))
            except ValueError as exc:
                print(f"Skipping line due to parsing error: {line}\nError: {exc}")

    return records

def _build_xml_tree(record_list: list[InputRecord]) -> ET.Element:
    root = ET.Element("AnexoJ_Q09_2A")
    anexoj_92a = ET.SubElement(root, "AnexoJq092AT01")
    num_linha = 1
    soma_c01 = 0
    soma_c02 = 0
    soma_c03 = 0
    soma_c04 = 0
    for record in record_list:
        record_el = ET.SubElement(anexoj_92a, "AnexoJq092AT01-Linha")
        record_el.set("numero", str(num_linha))
        num_linha += 1

        ET.SubElement(record_el, "NLinha").text = str(record.num_linha)
        ET.SubElement(record_el, "CodPais").text = str(record.cod_pais)
        ET.SubElement(record_el, "Codigo").text = record.codigo
        ET.SubElement(record_el, "AnoRealizacao").text = str(record.ano_realizacao)
        ET.SubElement(record_el, "MesRealizacao").text = str(record.mes_realizacao)
        ET.SubElement(record_el, "DiaRealizacao").text = str(record.dia_realizacao)
        ET.SubElement(record_el, "ValorRealizacao").text = str(record.valor_realizacao)
        soma_c01 += record.valor_realizacao
        ET.SubElement(record_el, "AnoAquisicao").text = str(record.ano_aquisicao)
        ET.SubElement(record_el, "MesAquisicao").text = str(record.mes_aquisicao)
        ET.SubElement(record_el, "DiaAquisicao").text = str(record.dia_aquisicao)
        ET.SubElement(record_el, "ValorAquisicao").text = str(record.valor_aquisicao)
        soma_c02 += record.valor_aquisicao
        ET.SubElement(record_el, "DespesasEncargos").text = str(record.valor_despesas_encargos)
        soma_c03 += record.valor_despesas_encargos
        ET.SubElement(record_el, "ImpostoPagoNoEstrangeiro").text = str(record.imposto_pago)
        soma_c04 += record.imposto_pago
        ET.SubElement(record_el, "CodPaisContraparte").text = str(record.cod_pais_contraparte)
        ET.SubElement(record_el, "RespeitaValoresMobiliarios").text = record.respeita_valores_mobiliarios

    ET.SubElement(root, "AnexoJq092AT01SomaC01").text = str(soma_c01)
    ET.SubElement(root, "AnexoJq092AT01SomaC02").text = str(soma_c02)
    ET.SubElement(root, "AnexoJq092AT01SomaC03").text = str(soma_c03)
    ET.SubElement(root, "AnexoJq092AT01SomaC04").text = str(soma_c04)
    return root

def write_xml_file(xml_tree: ET.Element, output_path: str) -> Path:
    path = Path(output_path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    tree = ET.ElementTree(xml_tree)
    tree.write(path, encoding="utf-8", xml_declaration=True)
    return path

def _prompt_non_empty(prompt_text: str) -> str:
    while True:
        value = input(prompt_text).strip()
        if value:
            return value
        print("Input cannot be empty. Please try again.")


def main() -> None:
    print("Enter the anexoJ_9.2A csv file with the IRS values to generate an XML file.")

    input_csv_path = _prompt_non_empty("CSV file path: ")
    output_xml_path = _prompt_non_empty("Output XML file path: ")

    write_xml_file(_build_xml_tree(_parse_anexoj_92a_csv(input_csv_path)), output_xml_path)
    print(f"XML file generated successfully at: {output_xml_path}")


if __name__ == "__main__":
    main()
