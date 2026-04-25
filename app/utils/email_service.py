# app/utils/email_service.py
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def enviar_email_com_anexo(destinatarios, assunto, corpo, pdf_bytes, nome_arquivo="relatorio.pdf"):
    """
    Função utilitária para envio seguro de e-mails usando SMTP e TLS.
    Requer configuração do .env com EMAIL_USER e EMAIL_PASS.
    """
    # Puxando dinamicamente do arquivo .env
    EMAIL_ADDRESS = os.environ.get('EMAIL_USER')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("❌ E-mail ou Senha não configurados no ambiente (.env).")
        return False

    try:
        msg = EmailMessage()
        msg['Subject'] = assunto
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = ", ".join(destinatarios)
        msg.set_content(corpo)

        # Anexando o PDF lido da memória
        msg.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename=nome_arquivo)

        # Configuração do SMTP (Padrão Gmail)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

        print(f"✅ E-mail enviado com sucesso para: {destinatarios}")
        return True

    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")
        return False