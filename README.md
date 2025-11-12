# 🏠 ha-djv_meter  
**Home Assistant Custom Integration for [DJV-COM](https://djv-com.net/) Portal**

---

## 📘 Overview  
`ha-djv_meter` is a **Home Assistant custom integration** that connects to the [DJV-COM](https://djv-com.net/](https://djv-com.net/web/public/pv/#/login)) online portal to fetch gas meter data for gas meters in the Republic of Moldova.

It provides access to key metrics from your DJV-COM account:

- 📅 **Current Month** consumption  
- ⛽ **Gas Price**  
- 🕒 **Last Day** reading  
- 🔢 **Meter Indications**

To log in, you’ll need:
- The **serial number of your radio module** (used as **username**)  
- The **serial number of your meter** (used as **password**)

---

## 🔐 Login Information

| Field | Description | Example Image |
|:------|:-------------|:--------------|
| **Username** | The **serial number of your radio module** | [<img src="docs/user_name_help.jpg" width="250"/>](docs/user_name_help.jpg) |
| **Password** | The **serial number of your meter** | [<img src="docs/password_help.jpg" width="250"/>](docs/password_help.jpg) |


---

## ✨ Features  
✅ Secure connection to the DJV-COM web portal  
✅ Automatic data retrieval and updates  
✅ Home Assistant sensor entities for all readings  
✅ Easy setup through UI or YAML  
✅ Works with Lovelace dashboards and automations  

---

## 🧩 Requirements  
- Home Assistant (latest version recommended)  
- Active DJV-COM account  
- Radio Module Serial Number  
- Meter Serial Number  
- Internet connection to access the DJV-COM portal  
