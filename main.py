import streamlit as st
import subprocess
import os
import signal
import json
import psutil

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

def start_background_job(product_type, price):
    jobs = load_jobs()
    job_id = f"{product_type}_{price}"
    
    if job_id in jobs:
        if psutil.pid_exists(jobs[job_id]):
            return f"Job already running for {product_type} at ${price} (PID: {jobs[job_id]})"
        else:
            del jobs[job_id]
    
    cmd = f"python background_job.py {product_type} {price}"
    process = subprocess.Popen(cmd.split(), start_new_session=True)
    jobs[job_id] = process.pid
    save_jobs(jobs)
    return f"Started background job for {product_type} at ${price} (PID: {process.pid})"

def stop_background_job(product_type, price):
    jobs = load_jobs()
    job_id = f"{product_type}_{price}"
    
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
                return f"Stopped job for {product_type} at ${price} (PID: {pid})"
            else:
                del jobs[job_id]
                save_jobs(jobs)
                return f"No PID file found for job {product_type} at ${price}. Job might already be stopped."
        except ProcessLookupError:
            del jobs[job_id]
            save_jobs(jobs)
            return f"Job for {product_type} at ${price} was not running (PID: {pid})"
    return f"No running job found for {product_type} at ${price}"

def list_running_jobs():
    jobs = load_jobs()
    if not jobs:
        return "No jobs are currently running."
    
    job_list = "Running jobs:\n"
    for job_id, pid in jobs.items():
        product_type, price = job_id.split('_')
        if psutil.pid_exists(pid):
            job_list += f"- {product_type} at ${price} (PID: {pid})\n"
        else:
            del jobs[job_id]
    save_jobs(jobs)
    return job_list

def main():
    st.title("Product Availability Checker")
    
    product_type = st.text_input("Enter product type (e.g., Tee, Bottoms):", "Tee")
    price = st.text_input("Enter price (e.g., 55.00):", "20.00")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        check_button = st.button("Check Now")
    with col2:
        submit_button = st.button("Submit Job")
    with col3:
        stop_button = st.button("Stop Job")
    with col4:
        list_button = st.button("List Running Jobs")

    if check_button:
        with st.spinner('Checking availability...'):
            result = subprocess.run(['python', 'background_job.py', product_type, price, '--once'], capture_output=True, text=True)
            st.text(result.stdout)

    if submit_button:
        job_status = start_background_job(product_type, price)
        st.text(job_status)

    if stop_button:
        stop_status = stop_background_job(product_type, price)
        st.text(stop_status)

    if list_button:
        st.text(list_running_jobs())

if __name__ == "__main__":
    main()
