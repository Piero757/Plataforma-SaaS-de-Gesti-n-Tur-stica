import os
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from .models import Venta, FacturaElectronica

def generar_xml_simulado(venta):
    """Genera un XML básico siguiendo el estándar UBL 2.1 (Simulado)"""
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" 
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" 
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cbc:UBLVersionID>2.1</cbc:UBLVersionID>
    <cbc:ID>{venta.serie}-{venta.numero}</cbc:ID>
    <cbc:IssueDate>{venta.fecha.date()}</cbc:IssueDate>
    <cac:AccountingSupplierParty>
        <cac:Party>
            <cac:PartyName><cbc:Name>Asociación Turística Peruana</cbc:Name></cac:PartyName>
        </cac:Party>
    </cac:AccountingSupplierParty>
    <cac:AccountingCustomerParty>
        <cac:Party>
            <cac:PartyName><cbc:Name>{venta.cliente.nombre_razon_social}</cbc:Name></cac:PartyName>
        </cac:Party>
    </cac:AccountingCustomerParty>
    <cac:LegalMonetaryTotal>
        <cbc:PayableAmount currencyID="PEN">{venta.total}</cbc:PayableAmount>
    </cac:LegalMonetaryTotal>
</Invoice>"""
    return xml_content

def generar_pdf_factura(venta):
    """Genera un PDF profesional con los datos del comprobante"""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "ASOCIACIÓN TURÍSTICA PERUANA")
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 70, "RUC: 20123456789")
    p.drawString(50, height - 85, "Calle Turismo 123, Cusco - Perú")

    # Recuadro Comprobante
    p.rect(width - 250, height - 100, 200, 80)
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width - 150, height - 40, venta.get_tipo_comprobante_display().upper())
    p.drawCentredString(width - 150, height - 60, f"{venta.serie}-{venta.numero}")

    # Datos Cliente
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 150, "CLIENTE:")
    p.setFont("Helvetica", 12)
    p.drawString(120, height - 150, venta.cliente.nombre_razon_social)
    p.drawString(50, height - 170, f"{venta.cliente.tipo_documento}: {venta.cliente.numero_documento}")
    p.drawString(50, height - 190, f"FECHA EMISIÓN: {venta.fecha.strftime('%d/%m/%Y %H:%M')}")

    # Tabla Detalle (Simulada)
    p.line(50, height - 220, width - 50, height - 220)
    p.drawString(50, height - 235, "DESCRIPCIÓN")
    p.drawString(400, height - 235, "CANT.")
    p.drawString(480, height - 235, "SUBTOTAL")
    p.line(50, height - 240, width - 50, height - 240)

    # ... iterar detalles ...
    
    # Total
    p.setFont("Helvetica-Bold", 12)
    p.drawString(400, 150, "TOTAL:")
    p.drawString(480, 150, f"S/ {venta.total}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

def procesar_comprobante_electronico(venta_id):
    """Orquestador para generar XML, PDF y QR de una venta"""
    try:
        venta = Venta.objects.get(id=venta_id)
        factura, created = FacturaElectronica.objects.get_or_create(venta=venta)

        # 1. XML
        xml_data = generar_xml_simulado(venta)
        factura.xml_file.save(f"{venta.serie}-{venta.numero}.xml", ContentFile(xml_data), save=False)

        # 2. PDF
        pdf_buffer = generar_pdf_factura(venta)
        factura.pdf_file.save(f"{venta.serie}-{venta.numero}.pdf", ContentFile(pdf_buffer.read()), save=False)

        # 3. QR (Hash simulado + URL)
        qr_data = f"ID:{venta.id}|RUC:20123456789|TOTAL:{venta.total}|FECHA:{venta.fecha.date()}"
        qr_img = qrcode.make(qr_data)
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        factura.qr_image.save(f"{venta.serie}-{venta.numero}_qr.png", ContentFile(qr_buffer.getvalue()), save=False)

        factura.hash_cpe = "ABC123XYZ789" # Hash simulado
        factura.save()
        
        venta.estado_sunat = 'ACEPTADO'
        venta.save()
        
        return True
    except Exception as e:
        print(f"Error procesando comprobante: {e}")
        return False
