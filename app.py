import streamlit as st
import subprocess
import os
import re
import time
import base64
from patterns import count_patterns, list_patterns, pdf_request_patterns, greetings, farewell  # Import patterns
from google.cloud import storage
from tempfile import NamedTemporaryFile
import json
import logging

# Base GCS path and local download path
BASE_GCS_PATH = "gs://fynd-assets-private/documents/daytrader/"
LOCAL_DOWNLOAD_PATH = "/Users/ninadmandavkar/Desktop/daytrader/08-2024/"


def fetch_pdf_from_gcs(pdf_name):
    command = ["gsutil", "cp", f"gs://your_bucket/{pdf_name}", "/local/path/"]
    logging.info(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True)
    if result.returncode != 0:
        logging.error(f"Error: {result.stderr.decode()}")
    return result

def count_invoices_in_month(month_year):
    gcs_search_path = f"{BASE_GCS_PATH}PDFs/**/*{month_year}*.pdf"
    result = subprocess.run(
        ["gsutil", "ls", gcs_search_path],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        files = [os.path.basename(line)[:-4] for line in result.stdout.strip().split("\n") if line]  # Remove .pdf extension
        return len(files), files
    else:
        return None, []

def extract_pdf_id(text):
    match = re.search(r'([A-Z]{2}-[A-Z]-[A-Z0-9]+-FY\d{2})', text)
    return match.group(0) if match else None

def month_to_str(month):
    month_map = {
        "january": "01", "february": "02", "march": "03", "april": "04",
        "may": "05", "june": "06", "july": "07", "august": "08",
        "september": "09", "october": "10", "november": "11", "december": "12"
    }
    if month.isdigit() and 1 <= int(month) <= 12:
        return f"{int(month):02d}-2024"  # Assume the year is 2024 for this context
    return month_map.get(month.lower(), None)

def typing_effect(text):
    typed_text_placeholder = st.empty()
    styled_text = f"""
    <span style="background-image: linear-gradient(to right, #800000, #ff0000); 
                -webkit-background-clip: text; 
                -webkit-text-fill-color: transparent;">
        {text}
    </span>
    """
    for i in range(len(text) + 1):
        typed_text_placeholder.markdown(styled_text.replace(text, text[:i]), unsafe_allow_html=True)
        time.sleep(0.018)
    typed_text_placeholder.markdown(styled_text, unsafe_allow_html=True)

def chatbot_response(user_input):
    lower_input = user_input.lower()

    if any(greet in lower_input for greet in greetings):
        return "Hello. Fynder here. How can I help you today?"

    elif any(fare in lower_input for fare in farewell):
        return "Goodbye! Let me know if you need help again."

    # Check for PDF requests using imported patterns
    for pattern in pdf_request_patterns:
        pdf_request_match = re.search(pattern, lower_input)
        if pdf_request_match:
            pdf_id = pdf_request_match.group(1)
            return f"Looking for PDF for invoice '{pdf_id}'. Please wait...", pdf_id

    # Check for count requests using imported patterns
    for pattern in count_patterns:
        month_year_match = re.search(pattern, lower_input)
        if month_year_match:
            month_year = month_year_match.group(1)
            if len(month_year.split()) == 2:
                month_str = month_to_str(month_year.split()[0])
                if month_str:
                    month_year = f"{month_str}-{month_year.split()[1]}"
            count, _ = count_invoices_in_month(month_year)
            if count is not None:
                return f"There are {count} invoices generated in {month_year}."
            else:
                return "I encountered an error while fetching the invoice count. Please try again later."

    # Check for list requests using imported patterns
    for pattern in list_patterns:
        list_match = re.search(pattern, lower_input)
        if list_match:
            month_year = list_match.group(1)
            if len(month_year.split()) == 2:
                month_str = month_to_str(month_year.split()[0])
                if month_str:
                    month_year = f"{month_str}-{month_year.split()[1]}"
            _, files = count_invoices_in_month(month_year)
            if files:
                return [f"**{file}**" for file in files]  # Use markdown bold for emphasis
            else:
                return "No invoices found for that month."

    pdf_id = extract_pdf_id(user_input)
    if pdf_id:
        if "when" in lower_input and "created" in lower_input:
            return f"Checking creation date for '{pdf_id}'. Please wait...", pdf_id, True
        else:
            return f"Looking for '{pdf_id}' in GCS fynd prod 393805 bucket. Please wait...", pdf_id

    return "I didn't quite understand that ;("

def download_pdf(file_path):
    """Reads a PDF file and returns its content in Base64 format."""
    with open(file_path, "rb") as f:
        pdf_data = f.read()
    return base64.b64encode(pdf_data).decode('utf-8')  # Encode to Base64 and decode to string

def main():
    # st.markdown(
    # """
    # <h1 style="
    #     background-image: linear-gradient(to right, #800000, #ff0000); 
    #     -webkit-background-clip: text; 
    #     -webkit-text-fill-color: transparent; 
    #     font-size: 3rem;  /* Adjust size as needed */
    #     text-align: center; /* Center the title */
    # ">
    #     Fynder
    # </h1>
    # """, 
    # unsafe_allow_html=True
    # )

    # Upload JSON credentials
    uploaded_file = st.file_uploader("Upload your fynd_prod.json file", type="json")
    
    if uploaded_file is not None:
        # Save the file temporarily
        with NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
            temp_file.write(uploaded_file.read())
            json_path = temp_file.name
        
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/ninadmandavkar/Desktop/Fynd/alerter/fynd-prod.json"

        with open(json_path) as f:
            credentials_info = json.load(f)
            st.write("Loaded credentials for:", credentials_info.get("client_email"))


        st.markdown(
            """
            <h1 style="
                background-image: linear-gradient(to right, #800000, #ff0000); 
                -webkit-background-clip: text; 
                -webkit-text-fill-color: transparent; 
                font-size: 3rem;  /* Adjust size as needed */
                text-align: center; /* Center the title */
            ">
                Fynder
            </h1>
            """, 
        unsafe_allow_html=True
        )
        
        
        user_input = st.text_input("", value="", help="Type your prompt here")

        if user_input:
            response = chatbot_response(user_input)

            if isinstance(response, tuple):
                bot_response, pdf_name = response
                typing_effect(bot_response)

                result = fetch_pdf_from_gcs(pdf_name)
                if result.returncode == 0:
                    downloaded_files = [f for f in os.listdir(LOCAL_DOWNLOAD_PATH) if pdf_name in f and f.endswith('.pdf')]
                    
                    if downloaded_files:
                        for pdf_file in downloaded_files:
                            file_path = os.path.join(LOCAL_DOWNLOAD_PATH, pdf_file)
                            pdf_data = download_pdf(file_path)

                            # Create a custom download button with gradient styling
                            download_button_html = f"""
                            <a href="data:application/pdf;base64,{pdf_data}" download="{pdf_file}" 
                            style="
                                    display: inline-block; 
                                    padding: 10px 20px; 
                                    color: white; 
                                    text-decoration: none; 
                                    border-radius: 20px; 
                                    background-image: linear-gradient(to right, #800000, #ff0000); 
                                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                ">
                                Download {pdf_file}
                            </a>
                            """
                            st.markdown(download_button_html, unsafe_allow_html=True)
                    else:
                        typing_effect("No files matching that name were found.")
                else:
                    typing_effect("There was an error fetching the PDF. Please check the name and try again.")
                    st.write(result.stderr)

            elif isinstance(response, list):  # When the response is a list of files
                for pdf_file in response:
                    typing_effect(pdf_file)  # Apply typing effect to each file
            else:
                typing_effect(response)
    else:
        st.markdown("")

if __name__ == "__main__":
    main()
