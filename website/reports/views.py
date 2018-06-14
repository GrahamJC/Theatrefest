import os
import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.template import Template, Context
from django.views import View
from django.urls import reverse
from django.http import HttpResponse

import arrow

from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.units import cm
from reportlab.lib import colors

from program.models import BoxOffice, Show, Performance
from tickets.models import Sale, Refund, Ticket

@login_required
def sale_pdf(request, sale_id):

    # Get sale to be printed
    sale = get_object_or_404(Sale, pk = sale_id)

    # Create receipt as a Platypus story
    response = HttpResponse(content_type = "application/pdf")
    response["Content-Disposition"] = f"attachment; filename=sale{sale.id}.pdf"
    doc = SimpleDocTemplate(
        response,
        pagesize = portrait(A4),
        leftMargin = 2.5*cm,
        rightMargin = 2.5*cm,
        topMargin = 2.5*cm,
        bottomMargin = 2.5*cm,
    )
    styles = getSampleStyleSheet()
    story = []

    # Theatrefest banner
    banner = Image(os.path.join(settings.STATIC_ROOT, "BridgeBanner.png"), width = 16*cm, height = 4*cm)
    banner.hAlign = 'CENTER'
    story.append(banner)
    story.append(Spacer(1, 1*cm))

    # Customer and sale number
    table = Table(
        (
            (Paragraph("<para><b>Customer:</b></para>", styles['Normal']), sale.customer),
            (Paragraph("<para><b>Sale no:</b></para>", styles['Normal']), sale.id),
        ),
        colWidths = (4*cm, 12*cm),
        hAlign = 'LEFT'
    )
    story.append(table)
    story.append(Spacer(1, 1*cm))

    # Buttons and fringers
    if sale.buttons or sale.fringers.count():
        tableData = []
        if sale.buttons:
            tableData.append((Paragraph("<para><b>Buttons</b></para>", styles['Normal']), sale.buttons, f"£{sale.button_cost}"))
        if sale.fringers.count():
            tableData.append((Paragraph("<para><b>Fringers</b></para>", styles['Normal']), sale.fringers.count(), f"£{sale.fringer_cost}"))
        table = Table(
            tableData,
            colWidths = (8*cm, 4*cm, 4*cm),
            hAlign = 'LEFT',
            style = (
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            )
        )
        story.append(table)
        story.append(Spacer(1, 0.5*cm))

    # Tickets
    is_first = True
    for performance in sale.performances:
        if not is_first:
            story.append(Spacer(1, 0.5*cm))
        is_first = False
        tableData = []
        tableData.append((Paragraph(f"<para>{performance['date']:%a, %e %b} at {performance['time']:%I:%M %p} - <b>{performance['show']}</b></para>", styles['Normal']), "", "", ""))
        for ticket in performance['tickets']:
            tableData.append((f"{ticket['id']}", "", ticket['description'], f"£{ticket['cost']}"))
        table = Table(
            tableData,
            colWidths = (4*cm, 4*cm, 4*cm, 4*cm),
            hAlign = 'LEFT',
            style = (
                ('SPAN', (0, 0), (3, 0)),
                ('ALIGN', (0, 1), (0, -1), 'RIGHT'),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
            )
        )
        story.append(table)

    # Total
    story.append(Spacer(1, 1*cm))
    table = Table(
        (
            ("", Paragraph("<para><b>Total:</b></para>", styles['Normal']), f"£{sale.total_cost}"),
        ),
        colWidths = (8*cm, 4*cm, 4*cm),
        hAlign = 'LEFT',
        style = (
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        )
    )
    story.append(table)

    # Create PDF document and return it
    doc.build(story)
    return response
    
def refund_pdf(request, refund_id):

    # Get refund to be printed
    refund = get_object_or_404(Refund, pk = refund_id)

    # Create receipt as a Platypus story
    response = HttpResponse(content_type = "application/pdf")
    response["Content-Disposition"] = f"attachment; filename=refund{refund.id}.pdf"
    doc = SimpleDocTemplate(
        response,
        pagesize = portrait(A4),
        leftMargin = 2.5*cm,
        rightMargin = 2.5*cm,
        topMargin = 2.5*cm,
        bottomMargin = 2.5*cm,
    )
    styles = getSampleStyleSheet()
    story = []

    # Theatrefest banner
    banner = Image(os.path.join(settings.STATIC_ROOT, "BridgeBanner.png"), width = 16*cm, height = 4*cm)
    banner.hAlign = 'CENTER'
    story.append(banner)
    story.append(Spacer(1, 1*cm))

    # Customer, refund number and amount
    table = Table(
        (
            (Paragraph("<para><b>Customer:</b></para>", styles['Normal']), refund.customer),
            (Paragraph("<para><b>Refund no:</b></para>", styles['Normal']), refund.id),
            (Paragraph("<para><b>Amount:</b></para>", styles['Normal']), f"£{refund.amount}"),
        ),
        colWidths = (4*cm, 12*cm),
        hAlign = 'LEFT'
    )
    story.append(table)
    story.append(Spacer(1, 1*cm))

    # Tickets
    is_first = True
    for performance in refund.performances:
        if not is_first:
            story.append(Spacer(1, 0.5*cm))
        is_first = False
        tableData = []
        tableData.append((Paragraph(f"<para>{performance['date']:%a, %e %b} at {performance['time']:%I:%M %p} - <b>{performance['show']}</b></para>", styles['Normal']), "", "", ""))
        for ticket in performance['tickets']:
            tableData.append((f"{ticket['id']}", "", ticket['description'], f"£{ticket['cost']}"))
        table = Table(
            tableData,
            colWidths = (4*cm, 4*cm, 4*cm, 4*cm),
            hAlign = 'LEFT',
            style = (
                ('SPAN', (0, 0), (3, 0)),
                ('ALIGN', (0, 1), (0, -1), 'RIGHT'),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
            )
        )
        story.append(table)

    # Create PDF document and return it
    doc.build(story)
    return response
