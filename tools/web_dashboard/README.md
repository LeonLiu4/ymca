# Web Dashboard

Web-based dashboard and interface for the YMCA Volunteer Data Processing System.

## 🌐 **Available Components:**

### **Flask Web Application**
- **File**: `app.py`
- **Purpose**: Main Flask web application for the dashboard
- **Usage**: `python app.py` or `./run_web_dashboard.sh`

### **Web Dashboard Runner**
- **File**: `run_web_dashboard.sh`
- **Purpose**: Shell script to launch the web dashboard
- **Usage**: `./run_web_dashboard.sh`

### **HTML Templates**
- **Directory**: `templates/`
- **Purpose**: HTML templates for the web interface

#### **Base Template**
- **File**: `templates/base.html`
- **Purpose**: Base template with common layout and styling

#### **Dashboard Template**
- **File**: `templates/dashboard.html`
- **Purpose**: Main dashboard interface

#### **Reports Template**
- **File**: `templates/reports.html`
- **Purpose**: Reports viewing interface

#### **Status Template**
- **File**: `templates/status.html`
- **Purpose**: System status and monitoring interface

## 🚀 **Quick Start:**

### **Launch Web Dashboard:**
```bash
./run_web_dashboard.sh
```

### **Or run directly:**
```bash
python app.py
```

### **Access Dashboard:**
Open your web browser and navigate to:
```
http://localhost:5000
```

## 📊 **Dashboard Features:**

- **Data Visualization**: Interactive charts and graphs
- **Report Viewing**: View generated reports in the browser
- **System Status**: Monitor system health and status
- **Data Export**: Download reports in various formats
- **Real-time Updates**: Live data updates and monitoring

## 🎨 **Interface Components:**

### **Dashboard Page**
- Overview of volunteer statistics
- Key metrics and KPIs
- Recent activity summary
- Quick access to reports

### **Reports Page**
- Browse available reports
- Filter and search reports
- Download reports
- View report details

### **Status Page**
- System health monitoring
- Processing status
- Error logs and alerts
- Performance metrics

## 🔧 **Configuration:**

The web dashboard can be configured for:
- **Port**: Default port 5000 (configurable)
- **Host**: Local or network access
- **Authentication**: Optional user authentication
- **Data Sources**: Configure data source connections

## 📚 **Documentation:**

- `docs/WEB_DASHBOARD_README.md` - Comprehensive web dashboard documentation

## 🛠 **Requirements:**

- Flask web framework
- Python 3.7+
- Modern web browser
- Network access (for remote access)

## 🔒 **Security:**

- Local access by default
- Optional authentication
- Secure data handling
- Input validation and sanitization
