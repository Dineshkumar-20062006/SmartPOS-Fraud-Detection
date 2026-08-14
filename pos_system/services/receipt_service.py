import os
from decimal import Decimal


def generate_receipt(bill):
    receipt_folder = "receipts"
    if not os.path.exists(receipt_folder):
        os.makedirs(receipt_folder)

    file_name = os.path.join(receipt_folder, f"bill_{bill.bill_no}.txt")

    with open(file_name, "w", encoding="utf-8") as file:
        file.write("================================\n")
        file.write("          ABC SUPERMARKET\n")
        file.write("================================\n\n")

        file.write(f"Bill No : {bill.bill_no}\n")
        file.write(f"Date    : {bill.bill_date}\n")
        file.write(f"Time    : {bill.bill_time}\n")

        file.write("\n--------------------------------\n")
        file.write(f"{'Product':15}{'Qty':8}{'Amount':10}\n")
        file.write("--------------------------------\n")

        for item in bill.items:
            prod_name = item.product.name if item.product else f"ID:{item.product_id}"
            file.write(
                f"{prod_name[:14]:15}"
                f"{item.quantity:<8}"
                f"${Decimal(str(item.subtotal)):.2f}\n"
            )

        file.write("--------------------------------\n")
        file.write(f"TOTAL   : ${Decimal(str(bill.total_amount)):.2f}\n")
        file.write(f"PAID    : ${Decimal(str(bill.paid_amount)):.2f}\n")
        file.write(f"CHANGE  : ${Decimal(str(bill.change_amount)):.2f}\n")
        file.write(f"PAYMENT : {bill.payment_method}\n")
        file.write("--------------------------------\n\n")

        file.write("          Thank You!\n")
        file.write("          Visit Again\n")
        file.write("================================\n")

    return file_name


def generate_pdf_receipt(bill):
    receipt_folder = "receipts"
    if not os.path.exists(receipt_folder):
        os.makedirs(receipt_folder)

    pdf_filename = os.path.join(receipt_folder, f"bill_{bill.bill_no}.pdf")

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        doc = SimpleDocTemplate(
            pdf_filename,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        elements = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Heading1"],
            fontSize=20,
            leading=24,
            alignment=1, # Center
            textColor=colors.HexColor("#1A365D")
        )

        subtitle_style = ParagraphStyle(
            "SubTitleStyle",
            parent=styles["Normal"],
            fontSize=10,
            leading=12,
            alignment=1,
            textColor=colors.HexColor("#4A5568")
        )

        elements.append(Paragraph("ABC SUPERMARKET", title_style))
        elements.append(Paragraph("123 Main Street, Commerce City | Phone: (555) 019-2831", subtitle_style))
        elements.append(Spacer(1, 15))

        # Bill Metadata Table
        meta_data = [
            [f"Bill Number: {bill.bill_no}", f"Date: {bill.bill_date}"],
            [f"Payment Method: {bill.payment_method}", f"Time: {bill.bill_time}"]
        ]
        meta_table = Table(meta_data, colWidths=[270, 270])
        meta_table.setStyle(TableStyle([
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#2D3748")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 15))

        # Items Table
        table_data = [["Product Name", "Qty", "Unit Price", "Subtotal"]]
        for item in bill.items:
            prod_name = item.product.name if item.product else f"Product #{item.product_id}"
            table_data.append([
                prod_name,
                str(item.quantity),
                f"${Decimal(str(item.unit_price)):.2f}",
                f"${Decimal(str(item.subtotal)):.2f}"
            ])

        items_table = Table(table_data, colWidths=[260, 70, 100, 110])
        items_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("ALIGN", (3, 0), (3, -1), "RIGHT"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 15))

        # Summary Table
        summary_data = [
            ["Total Amount:", f"${Decimal(str(bill.total_amount)):.2f}"],
            ["Paid Amount:", f"${Decimal(str(bill.paid_amount)):.2f}"],
            ["Change Given:", f"${Decimal(str(bill.change_amount)):.2f}"]
        ]
        summary_table = Table(summary_data, colWidths=[430, 110])
        summary_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("ALIGN", (0, 0), (0, -1), "RIGHT"),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1A202C")),
            ("LINEABOVE", (0, 0), (-1, 0), 1, colors.HexColor("#2B6CB0")),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 25))

        footer_style = ParagraphStyle(
            "FooterStyle",
            parent=styles["Normal"],
            fontSize=11,
            alignment=1,
            textColor=colors.HexColor("#4A5568")
        )
        elements.append(Paragraph("Thank you for shopping with us!", footer_style))

        doc.build(elements)
        return pdf_filename
    except Exception:
        # Fallback to txt receipt if PDF build encounters any environment issue
        return generate_receipt(bill)