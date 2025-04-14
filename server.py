from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import socketserver
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, formatdate
from urllib.parse import parse_qs
import ssl
import time

PORT = 8000

# Configuración del correo electrónico
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = 'sermalite2@gmail.com'
EMAIL_PASSWORD = 'ljcj biyd gocq loqp'
DESTINATION_EMAIL = 'xxleoxx2175@outlook.com'

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/'):
            self.path = self.path[1:]
        
        if self.path == '':
            self.path = 'index.html'
        
        file_path = os.path.join(os.getcwd(), self.path)
        if not os.path.exists(file_path):
            self.send_error(404, 'File not found')
            return
        
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/send_email':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                form_data = parse_qs(post_data)
                
                name = form_data.get('name', [''])[0]
                email = form_data.get('email', [''])[0]
                phone = form_data.get('phone', [''])[0]
                message = form_data.get('message', [''])[0]
                
                html_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2c3e50;">Nuevo Mensaje de Contacto - Sermalite</h2>
                        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px;">
                            <p><strong>Nombre:</strong> {name}</p>
                            <p><strong>Correo:</strong> {email}</p>
                            <p><strong>Teléfono:</strong> {phone}</p>
                            <h3 style="color: #2c3e50;">Mensaje:</h3>
                            <p style="white-space: pre-wrap;">{message}</p>
                        </div>
                        <hr style="border: 1px solid #eee; margin: 20px 0;">
                        <p style="color: #666; font-size: 12px;">
                            Este mensaje fue enviado desde el formulario de contacto de Sermalite.
                            Por favor, responda directamente a este correo para contactar al remitente.
                        </p>
                    </div>
                </body>
                </html>
                """
                
                msg = MIMEMultipart('alternative')
                msg.attach(MIMEText(html_content, 'html'))
                
                msg['Subject'] = f'Mensaje de Contacto - {name} - Sermalite'
                msg['From'] = formataddr(('Sermalite Contacto', EMAIL_USER))
                msg['To'] = DESTINATION_EMAIL
                msg['Reply-To'] = formataddr((name, email))
                msg['Date'] = formatdate(time.time(), localtime=True)
                msg['Message-ID'] = f"<{int(time.time())}@sermalite.com>"
                msg['X-Mailer'] = 'Sermalite Contact Form'
                
                context = ssl.create_default_context()
                with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
                    server.starttls(context=context)
                    server.login(EMAIL_USER, EMAIL_PASSWORD)
                    server.send_message(msg)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'status': 'success',
                    'message': 'Mensaje enviado exitosamente'
                }).encode())
                
            except Exception as e:
                print(f"Error al enviar el correo: {str(e)}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'status': 'error',
                    'message': f'Error al enviar el mensaje: {str(e)}'
                }).encode())
        else:
            self.send_error(404, 'Not Found')

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        SimpleHTTPRequestHandler.end_headers(self)

with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    print(f"Servidor corriendo en el puerto {PORT}")
    httpd.serve_forever()
