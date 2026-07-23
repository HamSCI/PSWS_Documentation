# What is the HF PSWS Reciever?

The HF PSWS Receiver is a direct-sampling, GPS-disciplined Software Defined Radio (SDR) system able to simultaneously receive and process the full MF and HF bands (from 0.3 to 30 MHz). The instrument uses a commercially available RX-888 MkII 16-bit SDR receiver, with additional filters and a GPSDO interface (described in detail below) custom-designed built, supplied and supported by Turn Island Systems, via project participant Paul Elliott 9WB6CXC). 
To complete the instrument, it requires a computer to run KA9Q-Radio and WSPR-Daemon software, such a Beelink, an external GPSDO, and an antenna.

The receiver makes two primary types of observations: HF Doppler measurements (measurements of the Doppler shifts of the transmissions of HF government time standard stations, such as WWV and CHU) and WSPR/FST4W decodes (signal and noise estimates for each WSPR spot, and Doppler shift measurements, when precision frequency references are available).

# Modifications to the RX-888 SDR: 

Before connecting the RX-888 SDR to anything, there are some necessary modifications to make. We need a sampling clock with an accuracy of 10 mHz, which is higher what the RX-888 internal oscillator provides, so we need to connect the RX-888's circuit board to an external clock. And the RX-888 has poor thermal control which can be addressed by adding a large thermal pad to the bottom of the board. [The RX888 Clock Kit and Thermal Pad ](https://tapr.org/product/rx888-clock-kit-and-thermal-pad/) contains the supplies to make these modifications, and the manual for it is available online [RX888 Clock Kit Manual](https://turnislandsystems.com/wp-content/uploads/2024/05/RX888-Kit-2.pdf).



# Installing the wsprdaemon Software: 

## BIOS Settings
1) Begin by plugging in the Beelink computer, and connecting it with an HDMI or Display Port to your monitor. 
2) Then, plug a keyboard into the monitor; no mouse required
3) Power on the PC, and then quickly hit **Delete** on the keyboard. This will bring you to the BIOS setup screen
   * If it doesn't bring you there, it's likely because you didn't hit **Delete** fast enough, and your PC's default operating system booted up instead. Shutdown the PC, and try again
4) On the BIOS setup screen, use the arrow keys to open the **Advanced tab**. Move down to **Smart Fan Function** then press **Enter** to enter the sub menu. From there, select **Smart CPU_Fan Mode** using again **Enter** and then move the cursor up to **Full on Mode** and select it
5) Press **Escape** to exit the sub menus until you return to the Advanced tab again
6) Now, move down to **AMD CBS** and press **Enter** into the sub menu, then select **FCH Common Options**. Then move down to **Ac Power Loss Options** and press **Enter**. Enter over **Ac Loss Control**, move the cursor down to **Always On** and select it
7) Return to the **Advanced Tab**. Then, move to the **Save & Exit** tab, move down to **Save Changes and Exit**, and select **Yes** to confirm the changes

You have now configured the computer to automatically turn back on in case of a power outage, and set the internal fans to always run at full speed to prevent overheating

## Installing the Operating System
Before you can set up any software, you need to install the required OS, Ubuntu. [On this site](https://ubuntu.com/download/server), download a LTS 24.04 version of Ubuntu; the file will be an a .iso file, indicating it's a disk image

### Flashing the Installation Media
If you're using a Windows operating system:
1) Download [Rufus](https://rufus.ie/en/) onto your personal computer
2) Then, plug in a USB flash drive (with at least 8 GB) into your computer
3) Next, open Rufus and press the **Select** Button towards the top of the screen, navigate to the Ubuntu disk image, and select it
4) Then, select your flash drive from the **Device** drop down menu
5) Make sure that under **File System** that Fat32 is selected rather than NTFS
6) Now select the **Start** button on the bottom right. Eject the USB drive when the operation is complete and remove the flash drive
   * Select **OK** to the prompt telling you the flash drive will be erased
   * You might see a screen after that offering different ways the drive can be formatted; select the default


If you're using a Mac or Linux operating system:
1) Download [Balena Etcher](https://etcher.balena.io/#download-etcher) onto your personal computer
2) Then, plug in a USB flash grab (with at least 8 GB) into your computer
3) Next, select **Flash from File** which will open a file browser window; navigate to the Ubuntu disk image and select it
4) Then, select **Select Target** and click the check mark of the flash drive you will be using
5) Finally, click **Flash!** and wait until the process finishes. Eject the USB when the operation is complete and remove the flash drive



### Starting the OS Installation
1) Plug in the flash drive into the Beelink. Make sure the computer is turned off when you do. 
2) Now, turn on the computer, then immediately and repeatedly press the **F7** Button 
   * If you are using a computer other than the recommended Beelink mini PC, look up what the hotkey is to enter that computer's Boot Menu
3) In the Boot Menu, select the USB flash drive
   * If the screen shows an option that says UEFI and one that doesn't, select the **UEFI** option
4) Now the computer should start up, and you should see a menu with a list of options. Select the one labeled **Try or Install Ubuntu Server** with **Enter**
If a bunch of text flies up the screen, everything is working well! 
5) After, you'll be shown a screen that gives your language options; use the arrow keys to move the cursor, and use the **Space** bar to select **English** 
6) Next, you'll see a menu to select your Keyboard layout. Leave the default options, and select done with **Space**
7) On the next screen, scroll through the options to the section labeled Ubuntu Server (minimized) and select it with **Space**
8) Move the cursor down to select done using **Enter**

### Connecting to Wifi/Internet
If you are using Ethernet, you can simply connect the Ethernet cable to the Beelink computer, and skip to part four of this section. If you're using Wifi:
1) On the next screen, you should see a section called "wlo1" and text underneath it saying disabled. Underneath that is some text that looks like _12:34:a5:b6:7c_, but with different values. This is the MAC address of the computer: write down this number and save it for later
2) Then, move the cursor up to **"wlo1"** and press **Space** to select it. Move the cursor to **Edit Wifi** and press **Space**, then move the cursor down to **Choose a visible network** and press **Space**
3) Then, connect to your Wifi network
   * If you're using a university network, you may need to register your device with that service; this is where the MAC address from earlier will be of use
4) On the next screen, you'll be asked to enter a proxy address. **Leave blank**, and select **Done**
5) Next, the screen will test the network. Wait a minute or two until the top of screen reads **This mirror location passed tests.** Then select **Done** 

### Finishing Installation
1) You will likely get a message asking if you would like to update the installer. Move the cursor up to **Update to the new installer** and select it with **Space**
2) You may need to wait a few minutes, then you will see a screen asking for the storage configuration. Move down to de-select the option labeled **Set up this disk as an LVM group** using **Space**
   * Make sure there is no X in the brackets here
3) Leave the **Use an entire disk** option enabled; this will erase the whole internal drive of the computer. Then, select **Done**
4) Next, you will see a summary of the storage configuration. Select **Done** 
5) Next, you will see a warning confirming destructive action, move the cursor to **Continue** and select it with **Space**
6) Next, you'll be prompted to set up the default account. Once you've made your choices, select **Done**
    * We recommend setting the username to be wsprdaemon, but no matter what you set the username and password to, make sure to write them down
7) On the next page, you will be asked about upgrading to ubuntu pro. Keep the default option with **Skip for Now** and continue
8) Next, you will see a menu for SSH configuration. If you have a VPN, you can set this up so that you can SSH into the PC from your personal computer, but it is not required
9) Next, you will see a screen that may list third party drivers. Select any if applicable (if you have any additional hardware connected to the system, for example), and select **Continue**
10) The next screen will list several extra software that can be installed on the system. These should **not** be installed, so you can select **Done**
11) The system will now start installing. This process may take 5-10 minutes. When it's finished, a button will appear that says **Reboot Now**. Select it
12) Then, you will see a screen saying "Please remove the installation media then press enter". Remove the flash drive, then press **Enter** to restart the system

## Configuring the System

### Update the Software and Operating System
1) You'll be asked to login to the system: enter the username and password you created earlier
2) Now that you're logged in, start by updating the preinstalled software and operating system with the following commands:
    * After entering the commands, you will be asked to enter your password for approval
    * You may also see a question asking if you would like to continue. Enter y, and press **Enter**

```
sudo apt update
sudo apt upgrade
```
After each command runs, you will see lots of text running across the screen, showing what it is doing. Wait until you see `[username]@[server-name]:~$` which is the terminal prompt that indicates you can enter a command again     

3) After the updates are installed, run the following commands to disable a system component called snap:
    * Snap is a type of software management tool; you don't want it running on your system because it will auto-update some programs which can cause issues with our automated scripts

```
sudo apt autoremove --purge snapd gnome-software-plugin-snap
sudo apt-mark hold snapd
```

### Installing wsprdaemon
1) Begin by installing some prerequisite tools and utilities with the following command:
     * Type y to agree to any prompts that come up
```
sudo apt install btop nmap git tmux vim net-tools iputils-ping avahi-daemon libnss-mdns mdns-scan avahi-utils avahi-discover build-essential make cmake gcc libairspy-dev libairspyhf-dev libavahi-client-dev libbsd-dev libfftw3-dev libhackrf-dev libiniparser-dev libncurses5-dev libopus-dev librtlsdr-dev libusb-1.0-0-dev libusb-dev portaudio19-dev libasound2-dev uuid-dev rsync sox libsox-fmt-all opus-tools flac tcpdump libhdf5-dev libsamplerate-dev
```

2) Next, you want to configure your system to run sudo commands without needed a password, and to do this, you need to start by installing a text editor, such as neovim. Run the following commands:

```
sudo apt install neovim
sudo nvim /etc/sudoers.d/wsprsudo
```
3) This puts us into neovim's normal mode. Now, press **i**, which takes you into insert mode, which allows you to edit. Enter in the following:
```
wsprdaemon ALL=(ALL) NOPASSWD: ALL
```
4) To escape insert mode, press **esc**. Then, to save what you've just edited, press **:** and then type `wq!`
     * w is to save, q is to quit, and ! is to force the operation, since the directory is protected
5) Next, you need to install git, which allows you to download the source code for wsprdaemon. Run:
```
sudo apt install git
```
6) With git now installed, run the following to clone the installation files from the source repository onto your computer, then run the main script inside, which will create a template configuration to be edited:
```
cd ~
git clone https://github.com/rrobinett/wsprdaemon.git
cd wsprdaemon
./wsprdaemon.sh -V
```
### Configuring wsprdaemon 
1) Making sure you are in you're in your newly cloned wsprdaemon directory (it should look like: `[username]@[server-name]:~/wsprdaemon$` ), run the following code to open the configuration file in the text editor
```
nvim wsprdaemon.conf
```
The template should look something like this:
```
#!/bin/bash

### These first two bash variables *must* be changed from their default values.
### To do so, uncomment the following two lines by removing the leading '#' and change the "<....>" fields
# WSPRNET_REPORTER_ID="<YOUR_REPORTER_ID>
# REPORTER_GRID="<YOUR_GRID>" #Ex. REPORTER_GRID="FN20vr" (NJIT's GRID Location)


WSPRNET_REPORTER_ID="${WSPRNET_REPORTER_ID-<NOT_DEFINED>}"           ### The ID of spots uploaded to wsprnet.org by this site
REPORTER_GRID="${REPORTER_GRID-<NOT_DEFINED>}"
ANTENNA_DESCRIPTION="<NOT_DEFINED>"   ### If defined, this is included in the reports to PSKReporter e.g '80m Dipole' and displayed on the KA9Q-web page

KA9Q_WEB_TITLE="${WSPRNET_REPORTER_ID}_@${REPORTER_GRID}_${ANTENNA_DESCRIPTION}"

# WD stations contributing to the HamSCI.org Personal Space Weather Project obtain these values from their dashboard at https://pswsnetwork.eng.ua.edu
# PSWS_STATION_ID="<PSWS_STATION_ID>" 
# PSWS_DEVICE_ID="<PSWS_DEVICE_ID>"

## The default is to upload extented spot and background noise level data to wsprdaemon.org.  These are small files, so they add little to the site's Internet bandwidth usage
# SIGNAL_LEVEL_UPLOAD="no"

## If "yes" the site uploads a 150 KByte .png file to wsprnet.org where it can be viewed at http://wsprdaemon.org/graphs/${WSPRNET_REPORTER_ID}/
## Since better, configurable Grafana graphs are available from the wsprdeamon.org, to conserve your site's Internet usage I now discourage the use of this feature
#SIGNAL_LEVEL_UPLOAD_GRAPHS="yes"

declare RECEIVER_LIST=(
        "KA9Q_0                     wspr-pcm.local     ${WSPRNET_REPORTER_ID}        ${REPORTER_GRID}    <SDR_PASSWORD_IF_NEEDED>"
        "KA9Q_0_WWV                   wwv-iq.local     ${WSPRNET_REPORTER_ID}        ${REPORTER_GRID}    <SDR_PASSWORD_IF_NEEDED>"
)

### Here are two examples of WSPR_SCHEDULEs.  Much more complex SDR configurations and schedules are desribed in wd_template_full.conf
declare WSPR_SCHEDULE_only_rx888=(
    "00:00             KA9Q_0,2200,W2:F2:F5:F15:F30  KA9Q_0,630,W2:F2:F5  KA9Q_0,160,W2:F2:F5   KA9Q_0,80,W2:F2:F5  KA9Q_0,80eu,W2:F2:F5  KA9Q_0,60,W2:F2:F5  KA9Q_0,60eu,W2:F2:F5  KA9Q_0,40,W2:F2:F5
                       KA9Q_0,30,W2:F2:F5            KA9Q_0,22,W2         KA9Q_0,20,W2:F2:F5    KA9Q_0,17,W2:F2:F5  KA9Q_0,15,W2:F2:F5    KA9Q_0,12,W2:F2:F5  KA9Q_0,10,W2:F2:F5    KA9Q_0,6,W2:F2:F5

                       KA9Q_0_WWV,WWVB,I1            KA9Q_0_WWV,WWV_2_5,I1  KA9Q_0_WWV,WWV_5,I1  KA9Q_0_WWV,WWV_10,I1   KA9Q_0_WWV,WWV_15,I1  KA9Q_0_WWV,WWV_20,I1  KA9Q_0_WWV,WWV_25,I1
                       KA9Q_0_WWV,CHU_3,I1           KA9Q_0_WWV,CHU_7,I1    KA9Q_0_WWV,CHU_14,I1"
)

### Configure the Kiwi in 8 channel mode and this WSPR_SCHEDULE configuration will use the 6 audio-only Kiwi channels to record spots on the most trafficed WSPR bands
###    while leaving the 2 Kiwi waterfall channels free for listeners

### Default to use the WSPR_SCHEDULE_only_rx888 schedule
declare WSPR_SCHEDULE=( "${WSPR_SCHEDULE_only_rx888[@]}" )
```
2) To modify this template for your station, you need to edit a few lines of code:
  * Uncomment **Line 5**, and replace "\<YOUR_REPORTER_ID>" with your FCC issued call sign; if you don't have a personal call sign, you can use your university/club's call sign. If you have neither, you can use a short nickname
 * Uncomment **Line 6**, and replace \"<YOUR_GRID>" with your geographic grid square, which you can find by going to [this website](https://levinecentral.com/ham/) and entering in your call sign or zip code to get your grid square. It will look like AA11aa
 * On **Line 14**, you can optionally modify ANTENNA_DESCRIPTION with information about your antenna; if you don't, keep it set to "\<NOT_DEFINED>"
 * For your next edits, you first need to set up a PSWS account:
    1) First by making a account at [Personal Space Weather Station Central Control System](https://pswsnetwork.eng.ua.edu/signup/) website. 
    2) Once your account is registered, head to the [Station Tab](https://pswsnetwork.eng.ua.edu/stations/stations/) and click the **Add New Station** button.
    3) Complete the form; only the station nickname and grid square are required
        * Station Nickname: If you have a FCC call sign, your nickname should contain it, and if you're part of a larger organization, add that as well. 
        * Grid Square: Same one from the configuration file
        * Elevation: Elevation of your station, in meters above sea level
        * Antenna: Specify what type of antennas you have installed at your site
        * Finish by adding your address and contact info, then hit **Add Station**
   4) Once the Stations page reloads, select **View My Stations**, and then take note of your Station ID; it will look like S000111
   5) Then, at the bottom of this page, select **Add New Instrument**, and fill out that form; only instrument and instrument type are required:
        * Instrument: Describe your instrument; for us here, write something like **RX-888 MK II - Beelink Mini PC**
        * Date Instrument Added: The date you connect your instrument to the PSWS server 
        * Date Instrument Removed: The date you shut down your instrument, disconnecting from the PSWS server
        * Nickname: Good to do if you have multiple of the same instruments for identification
        * Serial Number: Serial Number of your instrument
        * Status: Identifies if the station is operational or inactive
        * Instrument Type: Select the type of radio from the drop-down menu; we are using a **rx888**
    6) Then, hit **Add Instrument** and take note of the instrument ID, which will look like 111
 * After setting up your PSWS account: 
      * Uncomment **Line 19** and replace "\<PSWS_STATION_ID>" with your station's ID
      * Uncomment **Line 20** and replace "\<PSWS_DEVICE_ID>" with you instrument ID
* Lastly, Uncomment **Line 27**, SIGNAL_LEVEL_UPLOAD_GRAPHS="YES"

After modifications, you file should look something like:

```
#!/bin/bash

### These first two bash variables *must* be changed from their default values.
### To do so, uncomment the following two lines by removing the leading '#' and change the "<....>" fields
WSPRNET_REPORTER_ID="XX7XXX" 
REPORTER_GRID="AA11aa"


WSPRNET_REPORTER_ID="${WSPRNET_REPORTER_ID-<NOT_DEFINED>}"           ### The ID of spots uploaded to wsprnet.org by this site
REPORTER_GRID="${REPORTER_GRID-<NOT_DEFINED>}"
ANTENNA_DESCRIPTION="<NOT_DEFINED>"   ### If defined, this is included in the reports to PSKReporter e.g '80m Dipole' and displayed on the KA9Q-web page

KA9Q_WEB_TITLE="${WSPRNET_REPORTER_ID}_@${REPORTER_GRID}_${ANTENNA_DESCRIPTION}"

# WD stations contirbuting to the HamSCI.org Personal Space Weather Project obtain these values from their dashboard at https://pswsnetwork.caps.ua.edu
PSWS_STATION_ID="S000111" 
PSWS_DEVICE_ID="111" 

## The default is to upload extented spot and background noise level data to wsprdaemon.org.  These are small files, so they add little to the site's Internet bandwidth usage
# SIGNAL_LEVEL_UPLOAD="no"

## If "yes" the site uploads a 150 KByte .png file to wsprnet.org where it can be viewed at http://wsprdaemon.org/graphs/${WSPRNET_REPORTER_ID}/
## Since better, configurable Grafana graphs are available from the wsprdeamon.org, to conserve your site's Internet usage I now discourage the use of this feature
SIGNAL_LEVEL_UPLOAD_GRAPHS="yes"

declare RECEIVER_LIST=(
        "KA9Q_0                     wspr-pcm.local     ${WSPRNET_REPORTER_ID}        ${REPORTER_GRID}    <SDR_PASSWORD_IF_NEEDED>"
        "KA9Q_0_WWV                   wwv-iq.local     ${WSPRNET_REPORTER_ID}        ${REPORTER_GRID}    <SDR_PASSWORD_IF_NEEDED>"
)

### Here are two examples of WSPR_SCHEDULEs.  Much more complex SDR configurations and schedules are desribed in wd_template_full.conf
declare WSPR_SCHEDULE_only_rx888=(
    "00:00             KA9Q_0,2200,W2:F2:F5:F15:F30  KA9Q_0,630,W2:F2:F5  KA9Q_0,160,W2:F2:F5   KA9Q_0,80,W2:F2:F5  KA9Q_0,80eu,W2:F2:F5  KA9Q_0,60,W2:F2:F5  KA9Q_0,60eu,W2:F2:F5  KA9Q_0,40,W2:F2:F5
                       KA9Q_0,30,W2:F2:F5            KA9Q_0,22,W2         KA9Q_0,20,W2:F2:F5    KA9Q_0,17,W2:F2:F5  KA9Q_0,15,W2:F2:F5    KA9Q_0,12,W2:F2:F5  KA9Q_0,10,W2:F2:F5    KA9Q_0,6,W2:F2:F5

                       KA9Q_0_WWV,WWVB,I1            KA9Q_0_WWV,WWV_2_5,I1  KA9Q_0_WWV,WWV_5,I1  KA9Q_0_WWV,WWV_10,I1   KA9Q_0_WWV,WWV_15,I1  KA9Q_0_WWV,WWV_20,I1  KA9Q_0_WWV,WWV_25,I1
                       KA9Q_0_WWV,CHU_3,I1           KA9Q_0_WWV,CHU_7,I1    KA9Q_0_WWV,CHU_14,I1"
)

### Configure the Kiwi in 8 channel mode and this WSPR_SCHEDULE configuration will use the 6 audio-only Kiwi channels to record spots on the most trafficed WSPR bands
###    while leaving the 2 Kiwi waterfall channels free for listeners

### Default to use the WSPR_SCHEDULE_only_rx888 schedule
declare WSPR_SCHEDULE=( "${WSPR_SCHEDULE_only_rx888[@]}" )
```
   
3) Once you have finished editing the configuration file , press **esc**, then **:** and then type `wq!` to save
4) Then, run `./wsprdaemon.sh -V` again

This will install a lot of packages, and will take a while, potentially a few hours. Once it's finished, it should say something like "ka9q-radio added your user to the radio group, log out and log back in to save changes"
* If instead, you receive an error along the lines of "Update_ini_file_section_variable /etc/radio .....", attempt to run `./wsprdaemon.sh -V` again.
* If the error occurs again, reboot the computer by running:
```
sudo reboot now
```

* Then, run

```
 cd ~/wsprdaemon
 ./wsprdaemon.sh -V 
```

Once everything finishes up, you should get a prompt saying that the RX-888 MkII is not attached to a USB port.

### Setting up the GPS Disciplined Oscillator
Before you can connect your RX-888 and your GPS Disciplined Oscillator to you PC, you need to set up the GPS's clock speed.
1) Head to the [Leobodnar website ](https://www.leobodnar.com/shop/index.php?main_page=index&cPath=107) on your personal computer, and select what model of GPS Disciplined Oscillator you have
2) Scroll down instrument page until you find the download link for your GPS's configuration software. Download whatever software runs with your operating system
3) Open the configuration software and then connect your GPS to your personal computer. Once they are connected, your GPS's LED will light up, and the configuration software will respond
4) In the configuration software, there will be a box labeled OUT1. In that box, type 27000000, and then hit **Set**
   * This sets the clock to 27MHz output which is the required frequency for the RX-888.
5) Then, unplug the GPS Disciplined Oscillator from your personal computer, then attach it via it's OUTPUT 1 SMA connector to the RX-888. Then, connect both the GPS clock and the RX-888 to the Beelink PC via the Beelink's USB ports. It should like something like this:
<img width="587" height="452" alt="receiever_set_up" src="https://github.com/user-attachments/assets/dd2b84b2-76e6-4eae-8298-34fe18f3b457" />

_Schematic of the receiver set up: the Beelink PC, RX-888 Receiver, and the GPS Disciplined Oscillator are all labeled, and the connections between them are color-coded with small dots on the wire: yellow for the Oscillator-Receiver cord, red for the Oscillator-PC cord, and green for the Receiver-PC cord_

### Setting up WSPRDaemon to run on the PSWS Computer
1) After connecting the GPS oscillator and the RX-888, run `./wsprdaemon.sh -V` again:
2) Now, you should not get any more errors but you should get a prompt asking ``Enter file in which to save the key (/home/wsprdaemon/.ssh/id_ed25519):``.
When you get here, press **Enter** 3 or 4 times, including when it asks for a passphrase.
3) Then, you should receive an SSH public key. Take note of it, and then return to the [PSWS website's Stations Page](https://pswsnetwork.eng.ua.edu/stations/stations/). Navigate to **View My Stations**, click on your station, then **Edit Station Details**. Scroll down to find a textbox asking for an **SSH Public Key**, and in that box, enter the SSH key you took note of before. This will add your station to the PSWS Server.
4) Then, run the following code:
```
sudo systemctl enable radiod@rx888-wsprdaemon
sudo systemctl enable ft8-decode.service
sudo systemctl enable ft4-decode.service
sudo reboot now
```
5) Then, run the following code again:
```
 cd ~/wsprdaemon
 ./wsprdaemon.sh -V 
```

This time, it should print out the version number on the console. 

6) Once that happens, run `wd -A` in the console, which will start wsprdaemon and add it as a login item to start when the server turns on
7) Then, run `wdg p` to initialize the PSWS recording,
   * If you run into any errors, you can reference the [wsprdaemon Operation Guide](https://hamsci.jmclynch.org/operation.html)
8) Then, to confirm that the server is running, run `wds` into the console. Then, you should get a display like this:
<img width="405" height="633" alt="image_17" src="https://github.com/user-attachments/assets/b338168c-2bf6-4fc3-b3df-4237451ac2f0" />

Your server should also now show up as active on the [PSWS Website](https://pswsnetwork.eng.ua.edu/home)

# Connecting to the Antenna

For the HF receiver, the current standard antenna is the DX Engineering [RSEAV-1](https://www.dxengineering.com/parts/dxe-rseav-1). 

While it allows for one cable to be used for both the RF and the DC, since HamSCI wants to study the received transmissions, we want to minimize the signal's noise as much as possible. To do so, we will use a separate cable to supply the antenna it's power-- this requires a simple internal adjustment to the antenna (moving a jumper), as described on the **sixth and seventh page**s in the the RSEAV-1 [manual](https://static.dxengineering.com/global/images/instructions/dxe-rseav-1fvi.pdf?_gl=1*gvjbi2*_gcl_aw*R0NMLjE3ODEyNzM4NDkuRUFJYUlRb2JDaE1JMGVibS1PNkJsUU1WNDBUX0FSM0ZCemZBRUFBWUFTQUFFZ0tyOF9EX0J3RQ..*_gcl_au*MzIxODM4MDkuMTc3OTgyNDIzMS4xMDIyNjczNzQyLjE3ODEyNzM4ODcuMTc4MTI3Mzg4Nw..*_ga*MTU2MjkyMTYwNy4xNzc5ODI0MjMx*_ga_NZB590FMHY*czE3ODI0OTA0MzkkbzQkZzAkdDE3ODI0OTA0NDkkajUwJGwwJGgw). The manual also includes further assembly instructions.

Then, to power the antenna, connect the Jameco power supply to the F-Type Female to RCA Female Adapter, and then to the Female to RCA Male Power Adapter Cable, which will then connect to the antenna.





