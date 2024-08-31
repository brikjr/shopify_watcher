import streamlit as st
import subprocess
import os
import signal
import json
import psutil
import requests

JOB_FILE = "running_jobs.json"
PID_FILE = "background_job.pid"

def load_jobs():
    if os.path.exists(JOB_FILE):
        with open(JOB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_jobs(jobs):
    with open(JOB_FILE, 'w') as f:
        json.dump(jobs, f)

def get_product_types(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            product_types = set(product['product_type'] for product in data['products'])
            return sorted(list(product_types))
        else:
            st.error(f"Failed to fetch product types. Status code: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching product types: {str(e)}")
        return []

def start_background_job(website, product_type, price, email):
    jobs = load_jobs()
    job_id = f"{website}_{product_type}_{price}_{email}"
    
    if job_id in jobs:
        if psutil.pid_exists(jobs[job_id]):
            return f"Job already running for {website} - {product_type} at ${price} (PID: {jobs[job_id]})"
        else:
            del jobs[job_id]
    
    cmd = f"python background_job.py {website} {product_type} {price} {email}"
    process = subprocess.Popen(cmd.split(), start_new_session=True)
    jobs[job_id] = process.pid
    save_jobs(jobs)
    return f"Started background job for {website} - {product_type} at ${price} (PID: {process.pid})"

def stop_background_job(website, product_type, price, email):
    jobs = load_jobs()
    job_id = f"{website}_{product_type}_{price}_{email}"
    
    if job_id in jobs:
        pid = jobs[job_id]
        try:
            if os.path.exists(PID_FILE):
                with open(PID_FILE, 'r') as pid_file:
                    pid = int(pid_file.read().strip())
                os.kill(pid, signal.SIGTERM)
                del jobs[job_id]
                os.remove(PID_FILE)
                save_jobs(jobs)
                return f"Stopped job for {website} - {product_type} at ${price} (PID: {pid})"
            else:
                del jobs[job_id]
                save_jobs(jobs)
                return f"No PID file found for job {website} - {product_type} at ${price}. Job might already be stopped."
        except ProcessLookupError:
            del jobs[job_id]
            save_jobs(jobs)
            return f"Job for {website} - {product_type} at ${price} was not running (PID: {pid})"
    return f"No running job found for {website} - {product_type} at ${price}"

def list_running_jobs():
    jobs = load_jobs()
    if not jobs:
        return "No jobs are currently running."
    
    job_list = "Running jobs:\n"
    for job_id, pid in jobs.items():
        job_parts = job_id.split('_')
        if len(job_parts) >= 4:
            website, product_type, price, email = job_parts[:4]
            if psutil.pid_exists(pid):
                job_list += f"- {website} - {product_type} at ${price} for {email} (PID: {pid})\n"
            else:
                del jobs[job_id]
        else:
            # Handle old format job_ids or invalid entries
            job_list += f"- Invalid job entry: {job_id} (PID: {pid})\n"
    save_jobs(jobs)
    return job_list

def main():
    # Sidebar
    st.sidebar.title("Settings")
    website = st.sidebar.radio("Select Website", ["Water When Dry", "Kith"])
    email = st.sidebar.text_input("Enter your email address:", "hard@kapda.com")
    
    st.title(f"Watching - {website}")

    # Set URL based on website selection
    if website == "Water When Dry":
        url = "https://waterwhendry.com/products.json"
    else:
        url = "https://kith.com/products.json"
    
    # Fetch product types
    product_types = get_product_types(url)
    
    # Main content
    product_type = st.selectbox("Select product type:", product_types)
    price = st.text_input("Enter price (e.g., 55.00):", "20.00")

    col1, col2, col3, col4 = st.columns(4)
    
    if col1.button("Check Now"):
        with st.spinner('Checking availability...'):
            result = subprocess.run(['python', 'background_job.py', website, product_type, price, email, '--once'], capture_output=True, text=True)
            st.text(result.stdout)

    if col2.button("Submit Job"):
        job_status = start_background_job(website, product_type, price, email)
        st.text(job_status)

    if col3.button("Stop Job"):
        stop_status = stop_background_job(website, product_type, price, email)
        st.text(stop_status)

    if col4.button("List Running Jobs"):
        st.text(list_running_jobs())

if __name__ == "__main__":
    main()
