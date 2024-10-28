from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")  
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")  


class ContactForm(BaseModel):
    name: str = Field(..., title="Name", min_length=2, max_length=50)
    lastName: str = Field(..., title="Last Name", min_length=2, max_length=50) 
    email: EmailStr
    message: str = Field(..., title="Message", min_length=10, max_length=500)


def send_verification_email(form_data: ContactForm, email_to: str, subject: str):
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = email_to
        msg['Subject'] = subject
        
        html_body = f"""
  <html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif; 
            line-height: 1.6; 
            color: #333; 
            margin: 0; 
            padding: 0; 
            background-color: #f9f9f9;
        }}
        .container {{
            max-width: 600px; 
            margin: auto; 
            background-color: #ffffff; 
            padding: 20px; 
            border-radius: 8px; 
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }}
        h2 {{
            color: #333; 
            margin-bottom: 10px; 
            font-size: 24px;
        }}
        p {{
            margin-bottom: 10px; 
            font-size: 16px;
        }}
        .message {{
            border: 1px solid #ccc; 
            padding: 10px; 
            background-color: #f2f2f2; 
            border-radius: 4px;
        }}
        footer {{
            margin-top: 20px; 
            font-size: 0.9em; 
            color: #777; 
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
         <h2>Hola {form_data.name} {form_data.lastName},</h2>
        <p>Gracias por contactarnos.</p>
        <p><strong>Tu mensaje:</strong></p>
        <p class="message">{form_data.message}</p>
        <p>Te contactaremos pronto.</p>
        <footer>
            <p>Este es un correo automático, por favor no respondas.</p>
        </footer>
    </div>
</body>
</html>

        """
        
        msg.attach(MIMEText(html_body, 'html'))

        server.sendmail(SENDER_EMAIL, email_to, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send verification email")


@app.post("/contact")
async def contact_form(form_data: ContactForm, background_tasks: BackgroundTasks):
    try:
        subject = "Verificación de correo electrónico"
        body = f"Hola {form_data.name},\n\nGracias por contactarnos.\n\nTu mensaje: {form_data.message}\n\nTe contactaremos pronto."
        
        background_tasks.add_task(send_verification_email, form_data, form_data.email, subject)
        
        return {"message": "Formulario recibido. Se ha enviado un correo de verificación."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al procesar el formulario")
