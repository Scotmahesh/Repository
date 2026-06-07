import urllib.parse
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import streamlit as st
import io

st.set_page_config(page_title="Scot Agritech", page_icon="🚜", layout="wide")

st.title("🚜 Scot Agritech Pvt Ltd")
st.subheader("Ledger Reminder Portal")
st.write("Upload your Excel sheet below to generate payment reminders.")

uploaded_file = st.file_uploader("Upload your Excel file here", type=["xlsx", "xls"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    current_month = datetime.now().strftime("%B %Y")
    
    st.success("File uploaded successfully!")
    st.write("### Choose a dealer to send message:")

    # Loop through each row to display a clean layout for your staff
    for index, row in df.iterrows():
        try:
            dealer_id = str(row.iloc[1])    # Column B
            firm_name = str(row.iloc[2])    # Column C
            dealer_name = str(row.iloc[3])  # Column D
            steam = str(row.iloc[10])       # Column K
            days_30 = str(row.iloc[11])     # Column L
            days_60 = str(row.iloc[12])     # Column M
            days_90 = str(row.iloc[13])     # Column N
            total = str(row.iloc[14])       # Column O
            phone_raw = str(row.iloc[5]).strip() # Column F

            phone_number = "".join(filter(str.isdigit, phone_raw))
            if not phone_number.startswith("91") and len(phone_number) == 10:
                phone_number = "91" + phone_number

            # Create PDF in computer memory (safe for web)
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, 750, "Scot Agritech Pvt Ltd")
            c.setFont("Helvetica", 12)
            c.drawString(50, 730, f"Date: {current_month}")
            c.drawString(50, 710, f"Ledger Report for: {firm_name} ({dealer_id})")
            c.drawString(50, 690, f"Dealer: {dealer_name}")
            c.line(50, 675, 550, 675)
            c.drawString(50, 640, f"Steam Account: {steam}")
            c.drawString(50, 610, f"30 Days Pending: {days_30}")
            c.drawString(50, 580, f"60 Days Pending: {days_60}")
            c.drawString(50, 550, f"90 Days Pending: {days_90}")
            c.line(50, 535, 550, 535)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, 510, f"Total Pending Amount: {total}")
            c.save()
            
            pdf_data = buffer.getvalue()

            # Message body formatting
            whatsapp_msg = (
                f"Hi {dealer_name},\n\n"
                f"{dealer_id} {firm_name},\n\n"
                f"Thank you for connecting with us.\n\n"
                f"Your pending payment details till this {current_month}.\n\n"
                f"{steam}\n\n"
                f"30 Days pending amount is : {days_30}\n"
                f"60 Days pending amount is : {days_60}\n"
                f"90 Days pending amount is : {days_90}\n"
                f"Total pending Amount is : {total}\n\n"
                f"Can you please pay amount as soon as possible\n\n"
                f"Thanking you\n"
                f"Scot Agritech Pvt Ltd"
            )
            
            encoded_msg = urllib.parse.quote(whatsapp_msg)
            # Universal WhatsApp API link works on both Desktop and Mobile phones!
            whatsapp_url = f"https://whatsapp.com{phone_number}&text={encoded_msg}"

            # Create a nice visual box for each dealer row
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.write(f"**{dealer_name}** ({firm_name})")
                with col2:
                    # Staff clicks this button to download the PDF to their device
                    st.download_button(
                        label=f"📥 Download PDF Ledger",
                        data=pdf_data,
                        file_name=f"Ledger_{dealer_id}.pdf",
                        mime="application/pdf",
                        key=f"pdf_{index}"
                    )
                with col3:
                    # Staff clicks this link to launch WhatsApp and send message text
                    st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="text-decoration:none;"><button style="background-color:#25D366; color:white; border:none; padding:6px 12px; border-radius:4px; cursor:pointer; width:100%;">💬 Send WhatsApp Text</button></a>', unsafe_base64=True)
            st.divider()

        except Exception as e:
            st.error(f"Row {index} has bad data format.")
