import subprocess
import webbrowser
import os
from urllib.parse import quote_plus
import re
import comtypes
from pycaw.pycaw import AudioUtilities
def execute_command(command: str):

    command = command.lower().strip()

    # ==================================================
    # CHROME / BROWSER
    # ==================================================

    browser_words = [
        "open chrome",
        "launch chrome",
        "start chrome",
        "open browser",
        "launch browser",
        "start browser",
        "launch my browser",
        "open my browser",
        "start my browser",
    ]

    if any(word in command for word in browser_words):
        subprocess.Popen(["cmd", "/c", "start", "", "chrome"])
        return "Opening Chrome."

    # ==================================================
    # VS CODE
    # ==================================================

    vscode_words = [
        "open vscode",
        "open vs code",
        "launch vscode",
        "launch vs code",
        "start vscode",
        "start vs code",
        "open visual studio code",
        "launch visual studio code",
        "start visual studio code",
        "ವಿಎಸ್ ಕೋಡ್ ತೆರೆಯಿರಿ",
        "ವಿಎಸ್ ಕೋಡ್ ಓಪನ್ ಮಾಡಿ",
    ]

   
    if any(word in command for word in vscode_words):
        subprocess.Popen([
            r"D:\Microsoft VS Code\Code.exe"
        ])
        return "Opening Visual Studio Code."


    # ==================================================
    # CALCULATOR
    # ==================================================

    calculator_words = [
        "open calculator",
        "open calc",
        "launch calculator",
        "launch calc",
        "start calculator",
        "start calc",
        "start the calculator",
        "launch the calculator",
        "open the calculator",
        "calculator for me",
    ]

    if any(word in command for word in calculator_words):
        subprocess.Popen("calc.exe")
        return "Opening Calculator."

    # ==================================================
    # NOTEPAD
    # ==================================================

    notepad_words = [
        "open notepad",
        "launch notepad",
        "start notepad",
        "open the notepad",
        "start the notepad",
        "launch the notepad",
    ]

    if any(word in command for word in notepad_words):
        subprocess.Popen("notepad.exe")
        return "Opening Notepad."

    # ==================================================
    # FILE EXPLORER
    # ==================================================

    explorer_words = [
        "open file explorer",
        "launch file explorer",
        "start file explorer",
        "open explorer",
        "launch explorer",
        "start explorer",
        "open my files",
        "open files",
    ]

    if any(word in command for word in explorer_words):
        subprocess.Popen("explorer.exe")
        return "Opening File Explorer."

    # ==================================================
    # YOUTUBE
    # ==================================================

    youtube_words = [
        "open youtube",
        "launch youtube",
        "start youtube",
        "go to youtube",
        "take me to youtube",
    ]

    if any(word in command for word in youtube_words):
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube."

    # ==================================================
    # GOOGLE
    # ==================================================

    google_words = [
        "open google",
        "launch google",
        "start google",
        "go to google",
    ]

    if any(word in command for word in google_words):
        webbrowser.open("https://www.google.com")
        return "Opening Google."

    # ==================================================
    # LOCK WINDOWS
    # ==================================================

    lock_words = [
        "lock my laptop",
        "lock laptop",
        "lock my computer",
        "lock computer",
        "lock pc",
    ]

    if any(word in command for word in lock_words):
        subprocess.run(
            ["rundll32.exe", "user32.dll,LockWorkStation"]
        )
        return "Locking your computer."

    
    # ==================================================
    # OPEN DOWNLOADS
    # ==================================================

    downloads_words = [
        "open downloads",
        "open my downloads",
        "show downloads",
        "show my downloads",
    ]

    if any(word in command for word in downloads_words):
        subprocess.Popen(["explorer.exe", "shell:Downloads"])
        return "Opening Downloads."


    # ==================================================
    # OPEN DESKTOP
    # ==================================================

    desktop_words = [
        "open desktop",
        "show desktop files",
        "open my desktop",
    ]

    if any(word in command for word in desktop_words):
        desktop_path = os.path.join(
            os.path.expanduser("~"),
            "Desktop"
        )
        subprocess.Popen(["explorer.exe", desktop_path])
        return "Opening your Desktop."

    # ==================================================
    # OPEN RECYCLE BIN
    # ==================================================

    open_recycle_words = [
        "open recycle bin",
        "open the recycle bin",
        "show recycle bin",
        "show the recycle bin",
        "ರೀಸೈಕಲ್ ಬಿನ್ ತೆರೆಯಿರಿ",
        "ರೀಸೈಕಲ್ ಬಿನ್ ಓಪನ್ ಮಾಡಿ",
    ]

    if any(word in command for word in open_recycle_words):
        subprocess.Popen([
            "explorer.exe",
            "shell:RecycleBinFolder"
        ])
        return "Opening Recycle Bin."

    # ==================================================
    # EMPTY RECYCLE BIN
    # ==================================================

    recycle_words = [
        "empty recycle bin",
        "clear recycle bin",
        "delete recycle bin",
    ]

    if any(word in command for word in recycle_words):
        subprocess.run(
            [
                "powershell",
                "-Command",
                "Clear-RecycleBin -Force"
            ],
            capture_output=True
        )
        return "Recycle Bin emptied."


    # ==================================================
    # OPEN SETTINGS
    # ==================================================

    settings_words = [
        "open settings",
        "launch settings",
        "start settings",
        "windows settings",
    ]

    if any(word in command for word in settings_words):
        subprocess.Popen("start ms-settings:", shell=True)
        return "Opening Windows Settings."

    # ==================================================
    # OPEN TASK MANAGER
    # ==================================================

    task_words = [
        "open task manager",
        "launch task manager",
        "start task manager",
    ]

    if any(word in command for word in task_words):
        subprocess.Popen("taskmgr.exe")
        return "Opening Task Manager."

    # ==================================================
    # OPEN DOCUMENTS
    # ==================================================

    if command in [
        "open documents",
        "open my documents",
        "show documents",
        "show my documents"
    ]:
        documents_path = r"C:\Users\parth\OneDrive\Desktop\Documents"
        subprocess.Popen(["explorer.exe", documents_path])
        return "Opening Documents."

    # ==================================================
    # OPEN PICTURES
    # ==================================================

    if command in [
        "open pictures",
        "open my pictures",
        "show pictures",
        "show my pictures"
    ]:
        pictures_path = r"C:\Users\parth\OneDrive\Pictures"
        subprocess.Popen(["explorer.exe", pictures_path])
        return "Opening Pictures."

    # ==================================================
    # OPEN VIDEOS
    # ==================================================

    if command in [
        "open videos",
        "open my videos",
        "show videos",
        "show my videos"
    ]:
        videos_path = r"C:\Users\parth\OneDrive\Videos"
        subprocess.Popen(["explorer.exe", videos_path])
        return "Opening Videos."

    # ==================================================
    # OPEN MUSIC
    # ==================================================

    if command in [
        "open music",
        "open my music",
        "show music",
        "show my music"
    ]:
        music_path = r"C:\Users\parth\OneDrive\Music"
        subprocess.Popen(["explorer.exe", music_path])
        return "Opening Music."

    # ==================================================
    # GOOGLE SEARCH
    # ==================================================

    if command.startswith("google "):

        query = command[7:].strip()

        if query:
            url = (
                "https://www.google.com/search?q="
                + quote_plus(query)
            )

            webbrowser.open(url)

            return f"Searching Google for {query}."

    # ==================================================
    # YOUTUBE SEARCH
    # ==================================================

    if command.startswith("search youtube for "):

        query = command[
            len("search youtube for "):
        ].strip()

        if query:
            url = (
                "https://www.youtube.com/results?search_query="
                + quote_plus(query)
            )

            webbrowser.open(url)

            return f"Searching YouTube for {query}."

    # ==================================================
    # YOUTUBE SEARCH - SHORT VERSION
    # ==================================================

    if command.startswith("youtube "):

        query = command[
            len("youtube "):
        ].strip()

        if query:
            url = (
                "https://www.youtube.com/results?search_query="
                + quote_plus(query)
            )

            webbrowser.open(url)

            return f"Searching YouTube for {query}."

    # ==================================================
    # VOLUME UP
    # ==================================================

    volume_up_words = [
        "volume up",
        "increase volume",
        "increase the volume",
        "turn volume up",
        "make volume louder",
        "louder",
    ]

    if any(word in command for word in volume_up_words):

        powershell_command = """
        Add-Type -TypeDefinition @'
        using System;
        using System.Runtime.InteropServices;

        public class Keyboard {
            [DllImport("user32.dll")]
            public static extern void keybd_event(
                byte bVk,
                byte bScan,
                uint dwFlags,
                UIntPtr dwExtraInfo
            );
        }
'@

        [Keyboard]::keybd_event(0xAF, 0, 0, [UIntPtr]::Zero)
        [Keyboard]::keybd_event(0xAF, 0, 2, [UIntPtr]::Zero)
        """

        subprocess.run(
            ["powershell", "-NoProfile", "-Command", powershell_command],
            capture_output=True
        )

        return "Volume increased."

    # ==================================================
    # VOLUME DOWN
    # ==================================================

    volume_down_words = [
        "volume down",
        "decrease volume",
        "decrease the volume",
        "turn volume down",
        "make volume lower",
        "quieter",
    ]

    if any(word in command for word in volume_down_words):

        powershell_command = """
        Add-Type -TypeDefinition @'
        using System;
        using System.Runtime.InteropServices;

        public class Keyboard {
            [DllImport("user32.dll")]
            public static extern void keybd_event(
                byte bVk,
                byte bScan,
                uint dwFlags,
                UIntPtr dwExtraInfo
            );
        }
'@

        [Keyboard]::keybd_event(0xAE, 0, 0, [UIntPtr]::Zero)
        [Keyboard]::keybd_event(0xAE, 0, 2, [UIntPtr]::Zero)
        """

        subprocess.run(
            ["powershell", "-NoProfile", "-Command", powershell_command],
            capture_output=True
        )

        return "Volume decreased."

    
   
    # ==================================================
   
    mute_words = [
        "mute",
        "mute volume",
        "mute the volume",
        "silence volume",
    ]

    unmute_words = [
        "unmute",
        "unmute volume",
        "turn sound on",
        "restore sound",
    ]

    # Check unmute before mute
    if any(word in command for word in unmute_words):
        initialized = False
        try:
            comtypes.CoInitialize()
            initialized = True

            devices = AudioUtilities.GetSpeakers()
            interface = devices.EndpointVolume

            print("Mute state before:", interface.GetMute())
            interface.SetMute(0, None)
            muted = interface.GetMute()
            print("Mute state after:", muted)

            if muted == 0:
                return "Volume unmuted."

            return "Unable to unmute the volume."

        except Exception as error:
            print("UNMUTE ERROR:", error)
            return "Unable to unmute the volume."

        finally:
            if initialized:
                comtypes.CoUninitialize()

    if any(word in command for word in mute_words):
        initialized = False
        try:
            comtypes.CoInitialize()
            initialized = True

            devices = AudioUtilities.GetSpeakers()
            interface = devices.EndpointVolume

            print("Mute state before:", interface.GetMute())
            interface.SetMute(1, None)
            muted = interface.GetMute()
            print("Mute state after:", muted)

            if muted == 1:
                return "Volume muted."

            return "Unable to mute the volume."

        except Exception as error:
            print("MUTE ERROR:", error)
            return "Unable to mute the volume."

        finally:
            if initialized:
                comtypes.CoUninitialize()

    


    # ==================================================
    # BRIGHTNESS UP
    # ==================================================

   
    brightness_up_words = [
        "brightness up",
        "increase brightness",
        "increase the brightness",
        "turn brightness up",
        "make screen brighter",
        "make it brighter",
        "ಪರದೆಯ ಹೊಳಪನ್ನು ಹೆಚ್ಚಿಸಿ",
        "ಪರದೆಯ ಹೊಳಪನ್ನು ಹೆಚ್ಚಿಸು",
        "ಹೊಳಪನ್ನು ಹೆಚ್ಚಿಸಿ",
        "ಹೊಳಪನ್ನು ಹೆಚ್ಚಿಸು",
        "ಬ್ರೈಟ್ನೆಸ್ ಹೆಚ್ಚಿಸಿ",
        "ಬ್ರೈಟ್ನೆಸ್ ಹೆಚ್ಚಿಸು",
    ]

    if any(word in command for word in brightness_up_words):
        powershell_command = r"""
$ErrorActionPreference = 'Stop'
try {
    $brightness = Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightness -ErrorAction Stop
    $methods = Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightnessMethods -ErrorAction Stop

    if (-not $brightness -or -not $methods) {
        throw "Brightness control is unavailable."
    }

    $new = [Math]::Min(100, $brightness[0].CurrentBrightness + 10)

    foreach ($method in $methods) {
        Invoke-CimMethod -InputObject $method -MethodName WmiSetBrightness -Arguments @{
    Timeout = [uint32]1
    Brightness = [byte]$new
} -ErrorAction Stop | Format-List *
         Write-Output "WMI RETURN VALUE:"
        Write-Output $result.ReturnValue
    }
}
catch {
    Write-Output ("BRIGHTNESS FAILURE: " + $_.Exception.Message)
    exit 1
}
"""
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", powershell_command],
            capture_output=True,
            text=True
        )
        print("BRIGHTNESS RETURN CODE:", result.returncode)
        print("BRIGHTNESS OUTPUT:", result.stdout)
        print("BRIGHTNESS ERROR:", result.stderr)
        if result.returncode == 0:
            return "Brightness increased."
        return "I couldn't change the brightness."

    
    # ==================================================
    # BRIGHTNESS DOWN
    # ==================================================

    brightness_down_words = [
        "brightness down",
        "decrease brightness",
        "decrease the brightness",
        "turn brightness down",
        "make screen darker",
        "make it darker",
        "ಪರದೆಯ ಹೊಳಪನ್ನು ಕಡಿಮೆ ಮಾಡಿ",
        "ಪರದೆಯ ಹೊಳಪನ್ನು ಕಡಿಮೆ ಮಾಡು",
        "ಹೊಳಪನ್ನು ಕಡಿಮೆ ಮಾಡಿ",
        "ಹೊಳಪನ್ನು ಕಡಿಮೆ ಮಾಡು",
        "ಬ್ರೈಟ್ನೆಸ್ ಕಡಿಮೆ ಮಾಡಿ",
        "ಬ್ರೈಟ್ನೆಸ್ ಕಡಿಮೆ ಮಾಡು",
    ]

    
    if any(word in command for word in brightness_down_words):
        
        powershell_command = """
        $ErrorActionPreference = 'Stop'
        try {
            $brightness = Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightness -ErrorAction Stop
            $methods = Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightnessMethods -ErrorAction Stop

            if (-not $brightness -or -not $methods) {
                throw "Brightness control is unavailable."
            }

            $new = [Math]::Max(0, $brightness[0].CurrentBrightness - 10)

            foreach ($method in $methods) {
                Invoke-CimMethod -InputObject $method -MethodName WmiSetBrightness -Arguments @{
                    Timeout = [uint32]1
                    Brightness = [byte]$new
                } -ErrorAction Stop | Format-List *
            }
        }
        catch {
            Write-Output ("BRIGHTNESS FAILURE: " + $_.Exception.Message)
            exit 1
        }
        """


        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", powershell_command],
            capture_output=True,
            text=True
        )

        print("BRIGHTNESS-DOWN RETURN CODE:", result.returncode)
        print("BRIGHTNESS-DOWN OUTPUT:", result.stdout)
        print("BRIGHTNESS-DOWN ERROR:", result.stderr)

        if result.returncode == 0:
            return "Brightness decreased."
        return "I couldn't change the brightness."


  
    # ==================================================
    # BATTERY STATUS
    # ==================================================

    battery_words = [
        "battery",
        "battery status",
        "check battery",
        "check my battery",
        "how much battery",
        "battery percentage",
        "what is my battery",
        "ಬ್ಯಾಟರಿ",
        "ಬ್ಯಾಟರಿ ಸ್ಥಿತಿ",
        "ಬ್ಯಾಟರಿ ಎಷ್ಟು",
        "ಲ್ಯಾಪ್‌ಟಾಪ್ ಬ್ಯಾಟರಿ",
    ]

    if any(word in command for word in battery_words):

        powershell_command = """
        $ErrorActionPreference = 'Stop'
        try {
            $battery = Get-CimInstance Win32_Battery -ErrorAction Stop

            if ($battery) {
                Write-Output $battery[0].EstimatedChargeRemaining
            } else {
                Write-Output "NO_BATTERY"
            }
        } catch {
            Write-Output "BATTERY_ERROR"
            exit 1
        }
        """

        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", powershell_command],
            capture_output=True,
            text=True
        )

        battery = result.stdout.strip()

        if battery == "NO_BATTERY":
            return "I couldn't find a battery on this computer."

        if battery.isdigit():
            return f"Your battery is at {battery} percent."

        return "I couldn't check the battery."


    # ==================================================
    # SCREENSHOT
    # ==================================================

    screenshot_words = [
        "take screenshot",
        "take a screenshot",
        "capture screenshot",
        "capture the screen",
        "screenshot",
        "take screen shot",
    ]

    if any(word in command for word in screenshot_words):

        pictures_path = os.path.join(
            os.path.expanduser("~"),
            "Pictures"
        )

        os.makedirs(pictures_path, exist_ok=True)

        powershell_command = f"""
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing

        $screen = [System.Windows.Forms.Screen]::PrimaryScreen
        $bounds = $screen.Bounds

        $bitmap = New-Object System.Drawing.Bitmap(
            $bounds.Width,
            $bounds.Height
        )

        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)

        $graphics.CopyFromScreen(
            $bounds.Location,
            [System.Drawing.Point]::Empty,
            $bounds.Size
        )

        $filename = Join-Path "{pictures_path}" `
            ("Nexa_Screenshot_" + `
            (Get-Date -Format "yyyyMMdd_HHmmss") + ".png")

        $bitmap.Save(
            $filename,
            [System.Drawing.Imaging.ImageFormat]::Png
        )

        $graphics.Dispose()
        $bitmap.Dispose()

        Write-Output $filename
        """

        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                powershell_command
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return "Screenshot taken and saved in your Pictures folder."

        return "I couldn't take the screenshot."

    
    # FILE ASSISTANT
    # ==================================================
    
   
    search_roots = [
        "C:\\",
        "D:\\",
    ]




    # ==================================================
    # FIND / OPEN LATEST FILE
    # ==================================================

    latest_words = [
        "open latest file",
        "open the latest file",
        "find latest file",
        "find the latest file",
        "open newest file",
        "find newest file",
    ]

    if any(word in command for word in latest_words):

        files = []

        for root in search_roots:

            if not os.path.exists(root):
                continue

            try:
                for current_root, dirs, filenames in os.walk(root):

                    for filename in filenames:

                        full_path = os.path.join(
                            current_root,
                            filename
                        )

                        try:
                            modified_time = os.path.getmtime(
                                full_path
                            )

                            files.append(
                                (
                                    modified_time,
                                    full_path
                                )
                            )

                        except OSError:
                            continue

            except Exception:
                continue

        if files:

            files.sort(
                key=lambda x: x[0],
                reverse=True
            )

            latest_file = files[0][1]

            subprocess.Popen(
                ["explorer.exe", "/select,", latest_file]
            )

            return (
                "I found your latest file: "
                + os.path.basename(latest_file)
            )

        return "I couldn't find any files."


    # ==================================================
    # FIND PDF FILES
    # ==================================================

    pdf_words = [
        "find pdf",
        "find pdfs",
        "find pdf files",
        "search pdf",
        "search pdfs",
        "search pdf files",
        "show pdf files",
        "show my pdf files",
        "find my pdf",
        "find my pdfs",
    ]

    if any(word in command for word in pdf_words):

        pdf_files = []

        for root in search_roots:

            if not os.path.exists(root):
                continue

            
            try:
                for current_root, dirs, filenames in os.walk(root):
                    dirs[:] = [
                        directory for directory in dirs
                        if directory.lower() not in {
                            "$recycle.bin",
                            "system volume information",
                            "windows",
                            "program files",
                            "program files (x86)",
                            "programdata",
                            "appdata",
                            "node_modules",
                            ".git",
                            "venv",
                            ".venv",
                            "__pycache__",
                        }
                    ]

                    for filename in filenames:
                        if filename.lower().endswith(".pdf"):
                            pdf_files.append(
                                os.path.join(
                                    current_root,
                                    filename
                                )
                            )

            except OSError:
                continue


        if pdf_files:

            # Open the folder containing the first PDF
            first_pdf = pdf_files[0]

            subprocess.Popen(
                [
                    "explorer.exe",
                    "/select,",
                    first_pdf
                ]
            )

            if len(pdf_files) == 1:

                return (
                    "I found one PDF: "
                    + os.path.basename(first_pdf)
                )

            return (
                f"I found {len(pdf_files)} PDF files. "
                f"I opened the first one: "
                f"{os.path.basename(first_pdf)}"
            )

        return "I couldn't find any PDF files."


   
    
    # ==================================================
    # FIND FILE BY NAME
    # ==================================================

    file_command_patterns = [
        r"^open my (.+)$",
        r"^open the (.+)$",
        r"^open (.+)$",
        r"^find my (.+)$",
        r"^find the (.+)$",
        r"^find (.+)$",
        r"^search for my (.+)$",
        r"^search for (.+)$",
    ]

    file_query = None

    for pattern in file_command_patterns:
        match = re.match(pattern, command, flags=re.IGNORECASE)

        if match:
            candidate = match.group(1).strip()

            ignored_queries = {
                "chrome", "browser", "vscode", "vs code",
                "calculator", "calc", "notepad", "file explorer",
                "explorer", "youtube", "google", "settings",
                "task manager", "downloads", "desktop", "documents",
                "pictures", "videos", "music", "screenshot", "screen",
                "battery", "battery status", "volume", "volume up",
                "volume down", "brightness", "brightness up",
                "brightness down", "recycle bin",
            }

            if candidate.lower() not in ignored_queries:
                file_query = candidate
                break

    if file_query:
        cleaned_query = file_query.lower().strip()
        target_roots = search_roots

        # Detect searches specifically in Downloads
        downloads_requested = bool(
            re.search(r"\bdownloads\b", cleaned_query)
        )

        if downloads_requested:
            # Resolve the actual Windows Downloads folder
            downloads_path = os.path.expandvars(
                r"%USERPROFILE%\Downloads"
            )

            try:
                result = subprocess.run(
                    [
                        "powershell",
                        "-NoProfile",
                        "-Command",
                        "(New-Object -ComObject Shell.Application)"
                        ".Namespace('shell:Downloads').Self.Path",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if result.returncode == 0 and result.stdout.strip():
                    downloads_path = result.stdout.strip()

            except (OSError, subprocess.SubprocessError):
                pass

            target_roots = [downloads_path]

            # Remove the folder location from the search phrase
            cleaned_query = re.sub(
                r"\b(in|from|inside|of)?\s*downloads\b",
                "",
                cleaned_query,
                flags=re.IGNORECASE,
            ).strip()

        # Remove common request words
        cleaned_query = re.sub(
            r"\b(find|search|for|my|the|a|an|open|please|"
            r"file|files|document|documents|folder|folders|in|from)\b",
            "",
            cleaned_query,
            flags=re.IGNORECASE,
        )

       
        cleaned_query = re.sub(
            r"[^\w\s.-]",
            "",
            cleaned_query,
        )

        cleaned_query = re.sub(
            r"\s+",
            " ",
            cleaned_query,
        ).strip(" .")

        if not cleaned_query:
            return (
                "Please tell me the file name to search for"
                + (" in Downloads." if downloads_requested else ".")
            )
        
        # Support searches such as "Find my Python files"
        search_python_files = (
            bool(
                re.search(
                    r"\bpython\s+files?\b",
                    command,
                    flags=re.IGNORECASE,
                )
            )
            or cleaned_query in {
                "python",
                "python file",
                "python files",
            }
            or cleaned_query.endswith(".py")
        )

        
        matches = []

        for root in target_roots:
            if not os.path.isdir(root):
                continue


            try:
                for current_root, dirs, filenames in os.walk(root):
                    dirs[:] = [
                        directory for directory in dirs
                        if directory.lower() not in {
                            "$recycle.bin",
                            "system volume information",
                            "windows",
                            "program files",
                            "program files (x86)",
                            "programdata",
                            "appdata",
                            "node_modules",
                            ".git",
                            "venv",
                            ".venv",
                            "__pycache__",
                            ".antigravity-ide",
                            ".vscode",
                            ".idea",
                            "extensions",
                        }
                    ]

                    for filename in filenames:
                        full_path = os.path.join(current_root, filename)

                        if search_python_files:
                            matched = filename.lower().endswith(".py")
                        else:
                            matched = cleaned_query in filename.lower()

                        if matched:
                            matches.append(full_path)

                    if not search_python_files:
                        for dirname in dirs:
                            if cleaned_query in dirname.lower():
                                matches.append(
                                    os.path.join(current_root, dirname)
                                )

            except OSError:
                continue

        if matches:
            if search_python_files:
                folders = sorted(
                    set(os.path.dirname(path) for path in matches),
                    key=lambda folder: (
                        0 if folder.lower().startswith("d:\\") else 1,
                        folder.lower(),
                    ),
                )

                folder_to_open = folders[0]
                subprocess.Popen(["explorer.exe", folder_to_open])

                return (
                    f"Found {len(matches)} Python files "
                    f"in {len(folders)} folders. "
                    f"Opening {folder_to_open}."
                )

            selected = matches[0]

            if os.path.isdir(selected):
                subprocess.Popen(["explorer.exe", selected])
                return (
                    "Opening folder "
                    + os.path.basename(selected)
                    + "."
                )

            subprocess.Popen(["explorer.exe", "/select,", selected])

            return (
                "I found "
                + os.path.basename(selected)
                + " and opened its location."
            )

        return (
            "I couldn't find anything matching "
            + cleaned_query
            + "."
        )

    # ==================================================
    # RETURN NONE
    # ==================================================

    return None