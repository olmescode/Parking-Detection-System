# Parking Detection System

A web application to manage and monitor parking spaces using computer vision.

## How it Works

This system uses **OpenCV** to detect vehicle presence by comparing the live video feed against a static reference image of the empty parking lot.

1. **Image Processing:** Each frame is converted to grayscale and smoothed using a 5x5 Gaussian Blur to reduce noise.
2. **Pixel Comparison:** The system calculates the absolute difference between the current frame and the reference image.
3. **Thresholding:**
   - **Pixel Tolerance:** A pixel is considered "changed" if the difference value exceeds **30** (on a 0-255 scale).
   - **Occupancy Threshold:** A parking spot is marked as **Occupied** if more than **15%** of its pixels have changed compared to the reference.

## Project Structure

```
├── apps/
│   ├── authentication/  # User login and management
│   ├── dashboard/       # Main interface and calibration tool
│   ├── detection/       # Core OpenCV detection logic
│   └── parking/         # Database models (Camera, ParkingSpace)
├── config/              # Django project settings
├── media/               # Storage for reference images
├── static/              # CSS and JavaScript files
└── templates/           # HTML templates
```

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Database**
   ```bash
   python manage.py migrate
   ```

3. **Create Admin User**
   ```bash
   python manage.py createsuperuser
   ```

4. **Run Server**
   ```bash
   python manage.py runserver
   ```

Visit `http://127.0.0.1:8000` and log in.
