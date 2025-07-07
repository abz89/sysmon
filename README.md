# 🔧 System Monitoring Dashboard

A lightweight, modern and responsive system monitoring dashboard (inspired by Turing Smart Screen) built with:

- 🐍 Python (`psutil`, `Flask`)
- 📊 Chart.js for visualizing CPU, RAM, SWAP, network and battery data
- ☁️ Weather & time widgets
- 🌐 Web-based front-end, runs on any modern browser
- ⚙️ Fully configurable via `config.ini`

## 🚀 Features

- **Real-time system metrics**: CPU usage, memory, disk, swap, battery, uptime
- **Beautiful charts**: Radial usage charts and network history line graphs
- **Weather integration** using [Open-Meteo](https://open-meteo.com/)
- **Auto-refreshing UI**
- **Responsive dark mode layout**
- **Flexible mode**: run API only, front-end only, or both
- **Portable**: Runs on macOS (tested), Linux (tested), Raspberry Pi (tested) & Windows (tested)

## 🖥️ Preview

![Screenshot](media/preview.png)

## 🔧 Requirements

- Python 3.7+
- pip (Python package manager)

## 📦 Installation

### **1. Clone the Repository**

```bash
git clone https://github.com/abz89/sysmon.git
cd sysmon
```

### **2. Create a Virtual Environment**

#### **On macOS/Linux:**

```bash
python3 -m venv venv  # Create virtual environment
source venv/bin/activate  # Activate the virtual environment
```

#### **On Windows:**

```bash
python -m venv venv  # Create virtual environment
Set-ExecutionPolicy Unrestricted -Scope Process # If needed
.\venv\Scripts\activate  # Activate the virtual environment
```

### **3. Install Dependencies**

Make sure you have a `requirements.txt` file in your repository. Install the required Python packages with:

```bash
pip install -r requirements.txt
```

## 🧪 Usage

You can run the app in three modes:

### 1. API only

```bash
python systems_monitoring.py --mode api --port 8000
```

### 2. Frontend only (pointing to remote API)

```bash
python systems_monitoring.py --mode frontend --api-host <API_HOST> --api-port <API_PORT>
```

### 3. Both API + frontend (recommended for local dashboard)

```bash
python systems_monitoring.py --mode both --port 8000
```

Then open: [http://localhost:8000](http://localhost:8000)

## ⚙️ Configuration

On first run, a `config.ini` file will be automatically created.
You can manually or programmatically edit:

```ini
[general]
mode = both
port = 8000

[api]
host = localhost
port = 8000

[location]
lat = -6.8705552
lon = 107.5461454

```

## 📁 File Structure

```
.
├── LICENSE
├── README.md                 # this document
├── config.ini                # Auto-generated on first run
├── requirements.txt
├── static/
│   └── index.html            # Web UI
├── systems_monitoring.py     # Flask app (API + frontend)
└── media/
    └── preview.png
```

## 📜 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change or improve.

## ❤️ Acknowledgments

- [psutil](https://github.com/giampaolo/psutil)
- [Chart.js](https://www.chartjs.org/)
- [Bootstrap 5](https://getbootstrap.com/)
- [Open-Meteo](https://open-meteo.com/)
- [Icons8](https://icons8.com/) – for modern UI icons
