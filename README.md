# Neuro Lamp PC Sync

Do you like Neuro-sama's Lava Lamp? What if she could also control your PC RGBs?

**Now she can!** 

<img width="545" height="347" alt="G508H95bkAMqk2h" src="https://github.com/user-attachments/assets/0be9097c-cbe1-4801-9ca9-744de18048a6" />


---

## [Download v1.3.0](https://github.com/Kurokatana94/neuro-lamp-pc-sync/releases/download/v1.3.0/NeuroLampSync-Setup-1.3.0.exe)

---

## Requirements

- [**OpenRGB**](https://openrgb.org/releases.html) (Recommended)

If you're not sure which version to download, check the supported devices section on the OpenRGB website.

<img width="530" height="334" alt="Recording 2026-06-26 015119" src="https://github.com/user-attachments/assets/a5eaf847-1d52-4704-bec8-77b0a81999f4" />

But be sure that the chosen one uses **SDK Version 5**

<img width="707" height="148" alt="image" src="https://github.com/user-attachments/assets/3e0bad09-0e40-458d-a262-3d537059b3dc" />

**or**

- [**SignalRGB**](https://signalrgb.com/)

⚠️ **Epilepsy Warning** ⚠️  

SignalRGB support is **experimental**.

There may be a noticeable flicker when Neuro changes the color due to how SignalRGB handles custom effects.

This is a known limitation.

---

## Setting Things Up
1. Be sure to have installed either OpenRGB or SignalRGB
2. Run the installer
3. Launch **Neuro Lamp Sync** (it will appear in your system tray)

<img width="606" height="290" alt="Recording 2026-06-26 022029" src="https://github.com/user-attachments/assets/66c2a968-5be7-455f-87be-17df392ea974" />

Right-click the tray icon and click **Settings** to configure the app.

<img width="357" height="242" alt="image" src="https://github.com/user-attachments/assets/997b2fd8-677b-4f1e-a426-37c0376e4a94" />

### **OpenRGB**

- To allow Neuro Lamp Sync to control your RGBs the OpenRGB server needs to be running.<br>
  Make sure it always does by either:

  - By choosing the "Install System Service" option when installing OpenRGB (this will allow OpenRGB's server to be always running, even when the app itself isn't);
  <img width="495" height="387" alt="image" src="https://github.com/user-attachments/assets/6627bf04-e746-4e55-aa7e-b9375ccfee96" />

  - By checking the "Start Server" option in the settings (which will start the server automatically every time OpenRGB gets started;
  <img width="634" height="364" alt="20260715-2305-48 3466613" src="https://github.com/user-attachments/assets/c0e6e2e6-eefd-468c-ba6e-aa3a6459afde" />

  - Or by manually starting the server from the "SDK Server" tab.

- Make sure the IP address and port match your OpenRGB settings.

<img width="1424" height="544" alt="Recording 2026-06-26 023305" src="https://github.com/user-attachments/assets/324c1658-971d-4e30-a8df-c91f787a0752" />

### **SignalRGB**
- Download the effect from [here](https://github.com/Kurokatana94/neuro-lamp-pc-sync/blob/main/assets/signal_rgb_effects/NeuroLampSync.html)

<img width="460" height="268" alt="Recording 2026-07-05 032428" src="https://github.com/user-attachments/assets/e2fee851-efbd-4deb-a908-d7f34795f9cb" />

- Insert it in SignalRGB's effects folder.

Generally found in: 
```
%USERNAME%\Documents\WhirlwindFX\Effects
```
- Restart SignalRGB's app and activate it!

- (Optional) If you want to create a personalized effect, you must first read the [template](https://github.com/Kurokatana94/neuro-lamp-pc-sync/blob/main/assets/signal_rgb_effects/template/NeuroLampSyncSolid-template.html) and follow the instructions

---

## Heads Up

If the fade effect looks laggy, your ARGB controller might be struggling. Try switching the Effect to **Direct**.

---

## Credits

Created using [myfaceisausome](https://github.com/face3210)'s Neuro Lava Lamp API.
