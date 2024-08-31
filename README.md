* * *

Shopify Product Watcher
=======================

**Shopify Product Watcher** is a Streamlit-based application designed to monitor product availability on specific Shopify websites (e.g., "Water When Dry" and "Kith"). It allows users to check for specific products and receive email notifications when products become available at a specified price.

The application supports background jobs to periodically check product availability and send email alerts.

The application is also hosted online. You can use it directly at: [Shopify Product Watcher](https://shopifywatcher.streamlit.app/).

Features
--------

*   **Monitor Product Availability**: Check specific products by type and price on Shopify-based websites.
*   **Email Notifications**: Receive notifications when a product matching the criteria is found.
*   **Background Jobs**: Start and stop background jobs for continuous monitoring.
*   **Streamlit Interface**: Intuitive UI to configure and manage product monitoring.

Prerequisites
-------------

*   Python 3.9.6
*   Streamlit
*   Virtual Environment (venv)
*   Gmail account for receiving email notifications (configured in the script)

Setup
-----

### 1\. Clone the Repository


`git clone <repository-url> `
`cd shopify-product-watcher`

### 2\. Create and Activate a Virtual Environment

Create a virtual environment to manage dependencies:

`python -m venv watcher`

Activate the virtual environment:

*   **Windows**:
    
    `watcher\Scripts\activate`
    
*   **macOS/Linux**:

    `source watcher/bin/activate`
    

### 3\. Install Dependencies

Install the required Python packages using `pip`:

`pip install -r requirements.txt`


### 4\. Run the Application

To launch the Streamlit app locally:

`streamlit main app.py`

Usage
-----

### Main Components

1.  **Select Website**: Choose between "Water When Dry" or "Kith".
2.  **Enter Email Address**: The email where notifications will be sent.
3.  **Select Product Type**: Fetch and select the product type from the chosen website.
4.  **Enter Price**: Specify the desired price for the product.
5.  **Actions**:
    *   **Check Now**: Perform a one-time check for product availability.
    *   **Submit Job**: Start a background job to periodically check product availability.
    *   **Stop Job**: Stop the currently running background job.
    *   **(Optional) List Running Jobs**: Display all running background jobs.

### Stopping Background Jobs

The application creates a `background_job.pid` file to store the PID of running jobs. To manually stop jobs, use the "Stop Job" button or terminate the process using the stored PID.

### Hosted Version

The application is also hosted online. You can use it directly at: [Shopify Product Watcher](https://shopifywatcher.streamlit.app/).

How It Works
------------

### Core Functions

*   **load\_jobs()**: Loads the current running jobs from `running_jobs.json`.
*   **save\_jobs(jobs)**: Saves the job state to `running_jobs.json`.
*   **get\_product\_types(url)**: Fetches product types from the selected website's products JSON.
*   **start\_background\_job()**: Starts a new background job using the provided parameters.
*   **stop\_background\_job()**: Stops a running background job using the PID stored in `background_job.pid`.

### Email Notifications

The application uses Gmail's SMTP server to send notifications. Make sure to generate an "App Password" from your Gmail account to allow the application to send emails securely.

### Background Job Script

The `background_job.py` script checks for product availability periodically and sends an email if a product matching the criteria is found.

Important Notes
---------------

*   Ensure your Gmail account allows "less secure apps" or generate an "App Password" for secure access.
*   Monitor the Streamlit app logs for any errors or issues with background jobs.
*   Use the hosted version for a quick start, but consider running locally for more control over email configurations and job management.

Contributing
------------

Feel free to open issues or submit pull requests for any improvements or bug fixes.

License
-------

This project is licensed under the MIT License. See the LICENSE file for more details.

* * *

This README provides a comprehensive guide to setting up, using, and understanding the functionality of your Streamlit application. Adjust any section as needed based on your specific setup and requirements.