# Human Machine Interface for TSL2561 Project

## Description
This Human-Machine Interface (HMI) allows visualization and logging of data from an STM32 microcontroller via UART. It includes:
- **Graph Page**: Displays real-time data from the STM32.
- **Settings Page**: Configures UART communication.
- **History Page**: Shows all recorded data.
- **Database**: Stores collected data in a `.db` file.

## Installation

### Prerequisites
Make sure you have Python 3 installed along with the required dependencies.

### Clone the Repository
```bash
git clone https://github.com/morb0t/emb-project-HMI.git
cd emb-project-HMI
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### 1. Create or Use an Existing Database
- If you have an existing `.db` file, place it in the project directory.
- If not, the system will create one automatically when you start logging data.

### 2. Run the HMI
```bash
python3 main.py
```

### 3. Connect to STM32
1. Navigate to the **Settings** page.
2. Enter the UART settings (baud rate, port, etc.) as specified in the STM32 code.
3. Click **Connect**.

### 4. Visualize and Store Data
- The **Graph Page** will display real-time data received via UART.
- The **History Page** allows access to previously recorded data.
- All received data is stored in the database for future analysis.

## License
This project is licensed under the Apache License 2.0.

## Author
**ELHARDA Anouar**

## Contributing
Feel free to fork the repository and submit pull requests for improvements.

