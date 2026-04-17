# código para o arquivo: pdf_playwright.py

import os
from playwright.async_api import async_playwright
import logging

async def gerar_pdf_playwright(html_content: str) -> bytes:
    """
    Recebe uma string com conteúdo HTML, renderiza em um navegador invisível
    e retorna os bytes de um arquivo PDF.
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            # Carrega o HTML diretamente da variável
            await page.set_content(html_content, wait_until="networkidle")

            # Espera a página carregar completamente antes de imprimir
            await page.wait_for_selector('body', timeout=10000) 

            pdf_bytes = await page.pdf(
                format="A4", 
                print_background=True, 
                margin={"top": "20px", "bottom": "20px", "left": "20px", "right": "20px"}
            )
            await browser.close()
            return pdf_bytes

    except Exception as e:
        logging.exception(f"[Playwright PDF] Falha ao gerar PDF: {e}")
        raise